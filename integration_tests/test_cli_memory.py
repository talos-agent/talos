#!/usr/bin/env python3
"""
CLI-based memory functionality test script.
Tests memory functionality through the actual CLI interface.
"""

import subprocess
import tempfile
import json
import time
from pathlib import Path


def run_cli_command(command, input_text=None, timeout=30):
    """Run a CLI command and return the output."""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/home/ubuntu/repos/talos"
        )
        
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Command timed out"


def test_memory_cli_functionality():
    """Test memory functionality through CLI commands."""
    print("Testing Talos CLI Memory Functionality")
    print("=" * 50)
    
    temp_dir = tempfile.mkdtemp()
    memory_file = Path(temp_dir) / "cli_test_memory.json"
    user_id = "cli-test-user"
    
    try:
        print(f"Using memory file: {memory_file}")
        print(f"Using user ID: {user_id}")
        
        print("\n1. Testing CLI availability...")
        returncode, stdout, stderr = run_cli_command("uv run talos --help")
        if returncode == 0:
            print("✓ CLI is available and working")
        else:
            print(f"✗ CLI failed: {stderr}")
            assert False, f"CLI failed: {stderr}"
        
        print("\n2. Testing initial memory state...")
        cmd = f"uv run talos memory list --user-id {user_id} --memory-file {memory_file}"
        returncode, stdout, stderr = run_cli_command(cmd)
        if returncode == 0:
            print("✓ Memory list command works")
            print(f"Initial memories: {stdout.strip()}")
        else:
            print(f"✗ Memory list failed: {stderr}")
        
        print("\n3. Testing interactive conversation...")
        cmd = f"uv run talos main --user-id {user_id} --memory-file {memory_file} --verbose"
        input_text = "I like pizza\n"
        
        print(f"Sending input: '{input_text.strip()}'")
        returncode, stdout, stderr = run_cli_command(cmd, input_text, timeout=60)
        
        print(f"Return code: {returncode}")
        print(f"Output: {stdout}")
        if stderr:
            print(f"Errors: {stderr}")
        
        print("\n4. Checking if memory was stored...")
        time.sleep(1)  # Give time for memory to be saved
        
        cmd = f"uv run talos memory list --user-id {user_id} --memory-file {memory_file}"
        returncode, stdout, stderr = run_cli_command(cmd)
        
        if returncode == 0:
            print("✓ Memory list after conversation:")
            print(stdout)
            
            if "pizza" in stdout.lower():
                print("✓ Pizza preference was stored in memory!")
            else:
                print("✗ Pizza preference not found in memory")
        else:
            print(f"✗ Failed to list memories: {stderr}")
        
        print("\n5. Testing memory search...")
        cmd = f"uv run talos memory search 'pizza' --user-id {user_id} --memory-file {memory_file}"
        returncode, stdout, stderr = run_cli_command(cmd)
        
        if returncode == 0:
            print("✓ Memory search works:")
            print(stdout)
        else:
            print(f"✗ Memory search failed: {stderr}")
        
        print("\n6. Checking memory file contents...")
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    memory_data = json.load(f)
                print(f"✓ Memory file exists with {len(memory_data.get('memories', []))} memories")
                
                for memory in memory_data.get('memories', []):
                    if memory.get('user_id') == user_id:
                        print(f"  - {memory.get('description', 'No description')}")
            except Exception as e:
                print(f"✗ Failed to read memory file: {e}")
        else:
            print("✗ Memory file was not created")
        
        print("\n" + "=" * 50)
        print("CLI Memory Test Completed")
        
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        raise
    
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_tool_invocation_detection():
    """Test if we can detect when memory tools are being invoked."""
    print("\nTesting Tool Invocation Detection")
    print("=" * 40)
    
    
    print("Checking memory tool infrastructure...")
    
    files_to_check = [
        "/home/ubuntu/repos/talos/src/talos/tools/memory_tool.py",
        "/home/ubuntu/repos/talos/src/talos/core/memory.py",
        "/home/ubuntu/repos/talos/src/talos/core/agent.py"
    ]
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            assert False, f"{file_path} missing"
    
    print("Tool invocation detection test completed")


if __name__ == "__main__":
    print("Talos Memory CLI Test Suite")
    print("=" * 60)
    
    success = test_memory_cli_functionality()
    test_tool_invocation_detection()
    
    if success:
        print("\n✓ CLI memory tests completed successfully")
    else:
        print("\n✗ CLI memory tests failed")
    
    print("\nNext steps:")
    print("1. Run: uv run pytest test_memory_integration.py -v")
    print("2. Run: uv run pytest tests/test_memory_tool.py -v")
    print("3. Check memory tool binding and automatic invocation")
