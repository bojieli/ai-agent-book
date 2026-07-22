"""
Test cases for ShellSession __CMD_DONE__ marker handling
"""

from tools.shell_session import ShellSession


class TestShellSessionMarker:
    """Test that command output containing the marker string can't break the protocol"""

    def test_basic_command_and_exit_code(self):
        """Normal commands still work and report exit codes"""
        s = ShellSession(session_id="test_basic")
        try:
            out, code = s.execute("echo hello", timeout=10)
            assert code == 0
            assert "hello" in out
            out, code = s.execute("false", timeout=10)
            assert code == 1
        finally:
            s.kill()

    def test_output_containing_marker_text(self):
        """Output containing the marker text must not crash or be truncated"""
        s = ShellSession(session_id="test_marker_text")
        try:
            out, code = s.execute('echo "prefix__CMD_DONE__notanumber"', timeout=10)
            assert code == 0
            assert "prefix__CMD_DONE__notanumber" in out
        finally:
            s.kill()

    def test_marker_text_does_not_desync_next_command(self):
        """Marker-like output must not swallow the next command's output"""
        s = ShellSession(session_id="test_desync")
        try:
            s.execute('echo "see __CMD_DONE__123 here"', timeout=10)
            out, code = s.execute("echo hello-after", timeout=10)
            assert code == 0
            assert "hello-after" in out
        finally:
            s.kill()

    def test_execute_when_cwd_contains_spaces(self, temp_dir):
        """ShellSession must quote cwd so paths with spaces do not break cd."""
        space_dir = temp_dir / "dir with spaces"
        space_dir.mkdir()
        s = ShellSession(
            session_id="test_cwd_spaces",
            current_directory=str(space_dir),
        )
        try:
            out, code = s.execute("pwd", timeout=10)
            assert code == 0
            assert "dir with spaces" in out
            assert "too many arguments" not in out.lower()
        finally:
            s.kill()
