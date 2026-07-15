#!/usr/bin/env python3
"""Test script to verify the improvements made to the retrieval pipeline."""

import subprocess
import time
import requests
import sys
import signal

def test_server_startup():
    """Test that the server starts without deprecation warnings."""
    print("=" * 60)
    print("Testing Server Startup (No Deprecation Warnings)")
    print("=" * 60)
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, "main.py", "--port", "8004"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Collect output for 5 seconds
    output_lines = []
    start_time = time.time()
    
    while time.time() - start_time < 5:
        line = process.stdout.readline()
        if line:
            output_lines.append(line.strip())
            print(f"  {line.strip()}")
    
    # Check for deprecation warning
    has_warning = any("DeprecationWarning" in line or "on_event is deprecated" in line 
                     for line in output_lines)
    
    if has_warning:
        print("\n❌ FAILED: Deprecation warning still present!")
    else:
        print("\n✅ PASSED: No deprecation warnings found!")
    
    # Check for model loading messages
    has_model_info = any(
        "Model already cached" in line or 
        "Downloading model" in line or
        "Reranker initialized successfully" in line
        for line in output_lines
    )
    
    if has_model_info:
        print("✅ PASSED: Model loading information displayed!")
    else:
        print("❌ FAILED: No model loading information found!")
    
    # Check for loading time display
    has_timing = any("initialized successfully in" in line for line in output_lines)
    
    if has_timing:
        print("✅ PASSED: Model loading time displayed!")
    else:
        print("❌ FAILED: No loading time information found!")
    
    # Clean up
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
    
    print("\n" + "=" * 60)
    print("Summary of Improvements:")
    print("=" * 60)
    print("1. FastAPI deprecation warning: FIXED ✅" if not has_warning else "1. FastAPI deprecation warning: NOT FIXED ❌")
    print("2. Model loading progress: ADDED ✅" if has_model_info else "2. Model loading progress: NOT ADDED ❌")
    print("3. Loading time display: ADDED ✅" if has_timing else "3. Loading time display: NOT ADDED ❌")

if __name__ == "__main__":
    test_server_startup()
    print("\nTest completed!")
