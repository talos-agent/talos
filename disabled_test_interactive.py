import os
import subprocess

# Set dummy environment variables
env = os.environ.copy()
env["OPENAI_API_KEY"] = "dummy"
env["GITHUB_API_TOKEN"] = "dummy"

# Start the talos process
process = subprocess.Popen(
    ["talos"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env,
)

# Send input to the process
process.stdin.write("hello\n")
process.stdin.flush()
process.stdin.write("exit\n")
process.stdin.flush()

# Read the output
stdout, stderr = process.communicate()

# Check the output
print("stdout:")
print(stdout)
print("stderr:")
print(stderr)
assert "Entering interactive mode." in stdout
assert ">>" in stdout
assert "hello" in stdout

print("Test passed!")
