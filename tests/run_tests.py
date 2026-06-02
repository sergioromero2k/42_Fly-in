#!/usr/bin/env python3
"""Script to run all tests in the tests/ directory."""
import os
import subprocess

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RESET = "\033[0m"

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not os.path.exists(os.path.join(root, "venv")):
    print("Installing dependencies...")
    subprocess.run(["make", "install"], cwd=root)

tests_dir = os.path.join(root, "tests")
tests = sorted([f for f in os.listdir(tests_dir) if f.endswith(".txt")])

for test in tests:
    path = f"tests/{test}"
    print(f"\n--- {test} ---")
    result = subprocess.run(
        ["venv/bin/python", "main.py", path],
        cwd=root,
        capture_output=True,
        text=True
    )
    output = result.stdout.strip()
    error = result.stderr.strip()

    if result.returncode == 0:
        print(f"{GREEN}OK{RESET}")
        print(output)
    elif output.startswith("Error:"):
        print(f"{YELLOW}CONTROLLED ERROR{RESET}")
        print(f"{RED}{output}{RESET}")
    else:
        print(f"{RED}[PYTHON ERROR]{RESET}")
        print(error)
