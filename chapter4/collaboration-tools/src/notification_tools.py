"""Notification tools for email and instant messaging."""

import asyncio
import json
from typing import Optional, Dict, Any, List
import logging
import httpx

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html: bool = False,
    cc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Send an email notification.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        html: Whether body is HTML formatted
        cc: Optional list of CC recipients
        attachments: Optional list of file paths to attach
        
    Returns:
        Dictionary with send status
    """
    try:
        from config import config
        
        # Check if SendGrid is configured (preferred)
        if config.email.sendgrid_api_key:
            return await _send_email_sendgrid(
                to_email, subject, body, html, cc, attachments
            )
        # Fall back to SMTP
        elif config.email.smtp_username and config.email.smtp_password:
            return await _send_email_smtp(
                to_email, subject, body, html, cc, attachments
            )
        else:
            return {
                "success": False,
                "error": "No email service configured",
                "message": "Please configure SendGrid API key or SMTP credentials"
            }
            
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to send email to {to_email}"
        }


async def _send_email_smtp(
    to_email: str,
    subject: str,
    body: str,
    html: bool,
    cc: Optional[List[str]],
    attachments: Optional[List[str]]
) -> Dict[str, Any]:
    """Send email using SMTP."""
    try:
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
        from pathlib import Path
        from config import config
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config.email.smtp_from_email or config.email.smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = ', '.join(cc)
        
        # Add body
        mime_type = 'html' if html else 'plain'
        msg.attach(MIMEText(body, mime_type))
        
        # Add attachments
        if attachments:
            for filepath in attachments:
                path = Path(filepath)
                if path.exists():
                    with open(path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={path.name}'
                        )
                        msg.attach(part)
        
        # Send email
        await aiosmtplib.send(
            msg,
            hostname=config.email.smtp_host,
            port=config.email.smtp_port,
            username=config.email.smtp_username,
            password=config.email.smtp_password,
            use_tls=config.email.smtp_use_tls
        )
        
        return {
            "success": True,
            "to": to_email,
            "subject": subject,
            "method": "SMTP",
            "message": f"Email sent successfully to {to_email}"
        }
        
    except Exception as e:
        logger.error(f"SMTP send failed: {e}")
        raise


async def _send_email_sendgrid(
    to_email: str,
    subject: str,
    body: str,
    html: bool,
    cc: Optional[List[str]],
    attachments: Optional[List[str]]
) -> Dict[str, Any]:
    """Send email using SendGrid API."""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
        import base64
        from pathlib import Path
        from config import config
        
        # Create message
        message = Mail(
            from_email=config.email.smtp_from_email,
            to_emails=to_email,
            subject=subject
        )
        
        # Add body
        if html:
            message.add_html_content(body)
        else:
            message.add_plain_text_content(body)
        
        # Add CC
        if cc:
            for cc_email in cc:
                message.add_cc(cc_email)
        
        # Add attachments
        if attachments:
            for filepath in attachments:
                path = Path(filepath)
                if path.exists():
                    with open(path, 'rb') as f:
                        data = f.read()
                        encoded = base64.b64encode(data).decode()
                        attachment = Attachment(
                            FileContent(encoded),
                            FileName(path.name),
                            FileType('application/octet-stream'),
                            Disposition('attachment')
                        )
                        message.add_attachment(attachment)
        
        # Send
        sg = SendGridAPIClient(config.email.sendgrid_api_key)
        response = sg.send(message)
        
        return {
            "success": True,
            "to": to_email,
            "subject": subject,
            "method": "SendGrid",
            "status_code": response.status_code,
            "message": f"Email sent successfully to {to_email}"
        }
        
    except Exception as e:
        logger.error(f"SendGrid send failed: {e}")
        raise


async def send_telegram_message(
    message: str,
    chat_id: Optional[str] = None,
    parse_mode: str = "HTML"
) -> Dict[str, Any]:
    """Send a Telegram message.
    
    Args:
        message: Message text to send
        chat_id: Optional Telegram chat ID (uses default if not provided)
        parse_mode: Message parse mode (HTML, Markdown, or None)
        
    Returns:
        Dictionary with send status
    """
    try:
        from config import config
        
        if not config.im.telegram_bot_token:
            return {
                "success": False,
                "error": "Telegram bot token not configured",
                "message": "Please set TELEGRAM_BOT_TOKEN in environment"
            }
        
        target_chat_id = chat_id or config.im.telegram_default_chat_id
        if not target_chat_id:
            return {
                "success": False,
                "error": "No chat ID provided",
                "message": "Please provide chat_id parameter or set TELEGRAM_DEFAULT_CHAT_ID"
            }
        
        # Send message via Telegram Bot API
        url = f"https://api.telegram.org/bot{config.im.telegram_bot_token}/sendMessage"
        
        payload = {
            "chat_id": target_chat_id,
            "text": message
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
        
        return {
            "success": True,
            "chat_id": target_chat_id,
            "message_id": result.get("result", {}).get("message_id"),
            "message": "Telegram message sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send Telegram message"
        }


async def send_slack_message(
    message: str,
    webhook_url: Optional[str] = None,
    channel: Optional[str] = None,
    username: str = "Collaboration Agent"
) -> Dict[str, Any]:
    """Send a Slack message via webhook.
    
    Args:
        message: Message text to send
        webhook_url: Optional Slack webhook URL (uses default if not provided)
        channel: Optional channel to post to
        username: Bot username to display
        
    Returns:
        Dictionary with send status
    """
    try:
        from config import config
        
        target_webhook = webhook_url or config.im.slack_webhook_url
        if not target_webhook:
            return {
                "success": False,
                "error": "Slack webhook URL not configured",
                "message": "Please provide webhook_url or set SLACK_WEBHOOK_URL"
            }
        
        payload = {
            "text": message,
            "username": username
        }
        
        if channel:
            payload["channel"] = channel
        
        async with httpx.AsyncClient() as client:
            response = await client.post(target_webhook, json=payload)
            response.raise_for_status()
        
        return {
            "success": True,
            "channel": channel or "default",
            "message": "Slack message sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send Slack message"
        }


async def send_discord_message(
    message: str,
    webhook_url: Optional[str] = None,
    username: str = "Collaboration Agent"
) -> Dict[str, Any]:
    """Send a Discord message via webhook.
    
    Args:
        message: Message text to send
        webhook_url: Optional Discord webhook URL (uses default if not provided)
        username: Bot username to display
        
    Returns:
        Dictionary with send status
    """
    try:
        from config import config
        
        target_webhook = webhook_url or config.im.discord_webhook_url
        if not target_webhook:
            return {
                "success": False,
                "error": "Discord webhook URL not configured",
                "message": "Please provide webhook_url or set DISCORD_WEBHOOK_URL"
            }
        
        payload = {
            "content": message,
            "username": username
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(target_webhook, json=payload)
            response.raise_for_status()
        
        return {
            "success": True,
            "message": "Discord message sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to send Discord message: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send Discord message"
        }
