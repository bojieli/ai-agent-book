"""
Shell session management for persistent bash execution
"""

import subprocess
import time
import os
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict


@dataclass
class ShellSession:
    """Manages a persistent shell session"""
    session_id: str
    process: Optional[subprocess.Popen] = None
    current_directory: str = field(default_factory=lambda: os.getcwd())
    env: Dict[str, str] = field(default_factory=lambda: os.environ.copy())
    output_buffer: str = ""
    
    def start(self):
        """Start the shell process"""
        if self.process is None or self.process.poll() is not None:
            self.process = subprocess.Popen(
                ["/bin/bash"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=self.current_directory,
                env=self.env
            )
    
    def execute(self, command: str, timeout: int = 120) -> Tuple[str, int]:
        """Execute command in the persistent shell"""
        self.start()
        
        try:
            # Send command
            full_command = f"cd {self.current_directory} && {command}\n"
            self.process.stdin.write(full_command)
            self.process.stdin.write("echo __CMD_DONE__$?\n")
            self.process.stdin.flush()
            
            # Read output until marker
            output_lines = []
            start_time = time.time()
            
            while True:
                if time.time() - start_time > timeout:
                    return "Command timed out", -1
                
                line = self.process.stdout.readline()
                if not line:
                    break
                
                if "__CMD_DONE__" in line:
                    exit_code = int(line.split("__CMD_DONE__")[1].strip())
                    break
                
                output_lines.append(line.rstrip())
            
            output = "\n".join(output_lines)
            
            # Update current directory if cd was used
            if command.strip().startswith("cd "):
                try:
                    self.process.stdin.write("pwd\n")
                    self.process.stdin.flush()
                    new_dir = self.process.stdout.readline().strip()
                    if new_dir and os.path.isdir(new_dir):
                        self.current_directory = new_dir
                except:
                    pass
            
            return output, exit_code
            
        except Exception as e:
            return f"Error executing command: {str(e)}", -1
    
    def kill(self):
        """Terminate the shell session"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

