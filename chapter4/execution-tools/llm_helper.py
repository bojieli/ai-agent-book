"""LLM helper for safety checks, approval, and summarization."""

import json
from typing import Optional, Dict, Any
from openai import OpenAI
from config import Config


class LLMHelper:
    """Helper class for LLM-based operations."""
    
    def __init__(self):
        """Initialize the LLM client based on configuration."""
        llm_config = Config.get_llm_config()
        
        # All providers use OpenAI-compatible API
        self.client = OpenAI(
            api_key=llm_config["api_key"],
            base_url=llm_config.get("base_url")
        )
        self.model = llm_config["model"]
        self.provider = llm_config["provider"]
    
    def request_approval(
        self, 
        operation: str, 
        details: Dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Request LLM approval for a dangerous operation.
        
        Args:
            operation: The operation name
            details: Details about the operation
            
        Returns:
            Tuple of (approved, reason)
        """
        prompt = f"""You are a safety reviewer for an AI agent execution system.
Review the following operation and determine if it should be approved.

Operation: {operation}
Details: {json.dumps(details, indent=2)}

Analyze the operation for:
1. Potential data loss or destructive actions
2. Security risks
3. Resource consumption concerns
4. Compliance with best practices

Respond in JSON format:
{{
    "approved": true/false,
    "reason": "Brief explanation of your decision",
    "risk_level": "low/medium/high",
    "recommendations": ["List of recommendations if any"]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cautious safety reviewer. Approve operations that are safe and reject risky ones."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=Config.MAX_TOKENS
            )
            
            result = json.loads(response.choices[0].message.content)
            return result["approved"], result["reason"]
            
        except Exception as e:
            # If approval check fails, default to rejection for safety
            return False, f"Approval check failed: {str(e)}"
    
    def summarize_output(
        self, 
        tool_name: str,
        output: str
    ) -> str:
        """
        Summarize complex tool output.
        
        Args:
            tool_name: Name of the tool that produced the output
            output: The output to summarize
            
        Returns:
            Summarized output
        """
        
        prompt = f"""Summarize the following output from the '{tool_name}' tool.
Focus on:
1. Key results or findings
2. Errors or warnings
3. Important patterns or insights
4. Actionable information

Output to summarize:
{output[:5000]}  # Limit input to avoid token limits

Provide a concise summary that captures the essential information."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at summarizing technical output. Be concise and focus on actionable information."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=Config.MAX_TOKENS
            )
            
            summary = response.choices[0].message.content
            return f"[SUMMARIZED OUTPUT]\n{summary}\n\n[Original output length: {len(output)} characters]"
            
        except Exception as e:
            return f"[SUMMARIZATION FAILED: {str(e)}]\n\n{output[:max_length]}..."
    
    def analyze_error(
        self,
        tool_name: str,
        command: str,
        error_output: str
    ) -> str:
        """
        Analyze error output and provide suggestions.
        
        Args:
            tool_name: Name of the tool that produced the error
            command: The command or code that failed
            error_output: The error output
            
        Returns:
            Analysis with suggestions
        """
        prompt = f"""Analyze the following error from the '{tool_name}' tool:

Command/Code:
{command}

Error Output:
{error_output[:3000]}

Provide:
1. Root cause analysis
2. Suggested fixes
3. Prevention strategies

Be concise and practical."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert debugger. Analyze errors and provide clear, actionable solutions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=Config.MAX_TOKENS
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error analysis failed: {str(e)}"
    
    def verify_code_syntax(
        self,
        code: str,
        language: str = "python"
    ) -> tuple[bool, Optional[str]]:
        """
        Verify code syntax and provide feedback.
        
        Args:
            code: The code to verify
            language: Programming language
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # For Python, we can do actual syntax checking
        if language == "python":
            try:
                compile(code, "<string>", "exec")
                return True, None
            except SyntaxError as e:
                return False, f"Syntax error at line {e.lineno}: {e.msg}"
        
        # For other languages, use LLM for basic validation
        prompt = f"""Check the following {language} code for syntax errors:

```{language}
{code}
```

Respond in JSON format:
{{
    "valid": true/false,
    "errors": ["List of syntax errors if any"],
    "warnings": ["List of warnings if any"]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a {language} syntax validator. Check code for syntax errors."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=Config.MAX_TOKENS
            )
            
            result = json.loads(response.choices[0].message.content)
            if result["valid"]:
                return True, None
            else:
                return False, "; ".join(result["errors"])
                
        except Exception as e:
            # If validation fails, allow the code through
            return True, None
