"""Generic execution tools: code interpreter and virtual terminal."""

import subprocess
import sys
import io
import traceback
from typing import Dict, Any, Optional
from contextlib import redirect_stdout, redirect_stderr
from llm_helper import LLMHelper
from config import Config
from multilang_executor import LanguageExecutor, ExecutionStatus


class ExecutionTools:
    """Generic execution tools with safety and result analysis."""
    
    def __init__(self, llm_helper: LLMHelper):
        """Initialize execution tools with LLM helper."""
        self.llm_helper = llm_helper
        self.lang_executor = LanguageExecutor(workspace_dir=Config.WORKSPACE_DIR)
    
    async def code_interpreter(
        self,
        code: str,
        language: str = "python",
        timeout: float = 30.0,
        stdin: Optional[str] = None,
        files: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute code in a sandboxed environment with multi-language support.
        
        Args:
            code: Code to execute
            language: Programming language (python, javascript, typescript, go, java, cpp, rust, php, bash)
            timeout: Execution timeout in seconds
            stdin: Optional stdin input
            files: Optional additional files
            
        Returns:
            Result dictionary with output and analysis
        """
        language = language.lower()
        
        # Verify syntax first (only for Python for now)
        if Config.AUTO_VERIFY_CODE and language in ['python', 'python3']:
            is_valid, error_msg = self.llm_helper.verify_code_syntax(code, language)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Syntax error: {error_msg}",
                    "verification": "failed",
                    "language": language
                }
        
        # Check for dangerous operations
        if Config.REQUIRE_APPROVAL_FOR_DANGEROUS_OPS:
            dangerous_patterns = {
                'python': ['os.system', 'subprocess', 'eval', 'exec', 'open(', '__import__', 'compile'],
                'bash': ['rm -rf', 'dd if=', 'mkfs', '> /dev/', 'curl', 'wget'],
                'php': ['exec(', 'system(', 'shell_exec(', 'passthru(', 'eval('],
            }
            
            patterns = dangerous_patterns.get(language, [])
            detected = [p for p in patterns if p in code]
            
            if detected:
                approved, reason = self.llm_helper.request_approval(
                    "code_execution",
                    {
                        "code": code,
                        "language": language,
                        "detected_patterns": detected
                    }
                )
                
                if not approved:
                    return {
                        "success": False,
                        "error": f"Execution not approved: {reason}",
                        "language": language
                    }
        
        # Execute code using multi-language executor
        try:
            result = await self.lang_executor.execute_code(
                code=code,
                language=language,
                timeout=timeout,
                stdin=stdin,
                files=files
            )
            
            # Convert status to success flag
            success = result.get('status') == ExecutionStatus.SUCCESS
            
            # Summarize long outputs
            stdout = result.get('stdout', '')
            stderr = result.get('stderr', '')
            
            if Config.AUTO_SUMMARIZE_COMPLEX_OUTPUT and len(stdout) > 10000:
                stdout = self.llm_helper.summarize_output("code_interpreter", stdout)
            if Config.AUTO_SUMMARIZE_COMPLEX_OUTPUT and len(stderr) > 10000:
                stderr = self.llm_helper.summarize_output("code_interpreter", stderr)
            
            return {
                "success": success,
                "status": result.get('status'),
                "language": result.get('language', language),
                "stdout": stdout,
                "stderr": stderr,
                "returncode": result.get('returncode'),
                "error": result.get('error'),
                "compile_output": result.get('compile_output'),
                "phase": result.get('phase'),
                "verification": "passed" if Config.AUTO_VERIFY_CODE else "skipped"
            }
            
        except Exception as e:
            error_output = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return {
                "success": False,
                "error": error_output,
                "language": language
            }
    
    async def virtual_terminal(
        self,
        command: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute shell command in a virtual terminal.
        
        Args:
            command: Shell command to execute
            timeout: Timeout in seconds
            
        Returns:
            Result dictionary with output and analysis
        """
        # Check for dangerous commands
        if Config.REQUIRE_APPROVAL_FOR_DANGEROUS_OPS:
            dangerous_commands = [
                'rm -rf', 'dd', 'mkfs', 'format',
                '> /dev/', 'chmod -R', 'chown -R'
            ]
            
            if any(dangerous in command for dangerous in dangerous_commands):
                approved, reason = self.llm_helper.request_approval(
                    "terminal_command",
                    {
                        "command": command,
                        "detected_patterns": [p for p in dangerous_commands if p in command]
                    }
                )
                
                if not approved:
                    return {
                        "success": False,
                        "error": f"Command execution not approved: {reason}"
                    }
        
        # Execute command
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Config.WORKSPACE_DIR
            )
            
            stdout = result.stdout
            stderr = result.stderr
            
            # Summarize long output (>10000 characters)
            if Config.AUTO_SUMMARIZE_COMPLEX_OUTPUT:
                if len(stdout) > 10000:
                    stdout = self.llm_helper.summarize_output(
                        "virtual_terminal",
                        stdout
                    )
                if len(stderr) > 10000:
                    stderr = self.llm_helper.summarize_output(
                        "virtual_terminal",
                        stderr
                    )
            
            response = {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": stdout,
                "stderr": stderr
            }
            return response
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Command execution failed: {str(e)}"
            }
