"""
Shell session management for persistent bash execution
"""

import subprocess
import time
import os
import re
import shlex
import queue
import threading
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
            # Reader thread feeds stdout lines into a queue so that execute()
            # can wait on them with a real timeout (a bare readline() would
            # block forever on silent commands like `sleep`).
            self._output_queue = queue.Queue()
            reader = threading.Thread(
                target=self._read_stdout,
                args=(self.process, self._output_queue),
                daemon=True
            )
            reader.start()

    def _read_stdout(self, process, q):
        """Pump stdout lines into the queue; None marks end of stream."""
        for line in iter(process.stdout.readline, ''):
            q.put(line)
        q.put(None)

    def _restart(self):
        """Kill a stuck shell and start a fresh one (keeps current_directory)."""
        self.kill()
        self.process = None
        self.start()
    
    def execute(self, command: str, timeout: float = 120) -> Tuple[str, int]:
        """Execute command in the persistent shell"""
        self.start()
        
        try:
            # Send command
            full_command = f"cd {shlex.quote(self.current_directory)} && {command}\n"
            self.process.stdin.write(full_command)
            self.process.stdin.write("echo __CMD_DONE__$?\n")
            self.process.stdin.flush()
            
            # Read output until marker
            output_lines = []
            deadline = time.time() + timeout
            exit_code = -1

            while True:
                remaining = deadline - time.time()
                if remaining <= 0:
                    # Kill the stuck shell so the pending marker of the
                    # timed-out command cannot corrupt the next command.
                    self._restart()
                    return f"Command timed out (timeout: {timeout}s)", -1

                try:
                    line = self._output_queue.get(timeout=remaining)
                except queue.Empty:
                    self._restart()
                    return f"Command timed out (timeout: {timeout}s)", -1

                if line is None:  # shell exited unexpectedly
                    break

                # 只认独占一行的结束标记；命令输出中恰好包含标记字符串的行
                # 视为普通输出，避免误截断或与下一命令的输出错位。
                m = re.fullmatch(r"__CMD_DONE__(\d+)", line.strip())
                if m:
                    exit_code = int(m.group(1))
                    break

                output_lines.append(line.rstrip())

            output = "\n".join(output_lines)

            # Update current directory if cd was used
            if command.strip().startswith("cd "):
                try:
                    self.process.stdin.write("pwd\n")
                    self.process.stdin.flush()
                    new_dir = self._output_queue.get(timeout=5)
                    if new_dir:
                        new_dir = new_dir.strip()
                        if new_dir and os.path.isdir(new_dir):
                            self.current_directory = new_dir
                except Exception:
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

