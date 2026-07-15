"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from system_state import SystemState


@pytest.fixture
def system_state():
    """Create a fresh system state for each test"""
    return SystemState()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing"""
    # Create Python file
    python_file = temp_dir / "sample.py"
    python_file.write_text("""
def hello(name):
    return f"Hello, {name}!"

def add(a, b):
    return a + b

if __name__ == "__main__":
    print(hello("World"))
""")
    
    # Create JavaScript file
    js_file = temp_dir / "sample.js"
    js_file.write_text("""
function hello(name) {
    return `Hello, ${name}!`;
}

function add(a, b) {
    return a + b;
}

console.log(hello("World"));
""")
    
    # Create text files
    text_file1 = temp_dir / "file1.txt"
    text_file1.write_text("This is a test file.\nIt has multiple lines.\nSome contain the word ERROR.\n")
    
    text_file2 = temp_dir / "file2.txt"
    text_file2.write_text("Another file here.\nNo errors in this one.\nJust normal text.\n")
    
    # Create nested directory
    nested_dir = temp_dir / "subdir"
    nested_dir.mkdir()
    
    nested_file = nested_dir / "nested.py"
    nested_file.write_text("""
class TestClass:
    def method(self):
        pass
""")
    
    return {
        "python_file": python_file,
        "js_file": js_file,
        "text_file1": text_file1,
        "text_file2": text_file2,
        "nested_file": nested_file,
        "temp_dir": temp_dir
    }

