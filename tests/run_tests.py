#!/usr/bin/env python3
"""Script to run all tests in the tests/ and maps/ directories."""
import os
import subprocess
import re

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
RESET = "\033[0m"

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGETS = {
    "maps/easy/01_linear_path.txt": 6,
    "maps/easy/02_simple_fork.txt": 8,
    "maps/easy/03_basic_capacity.txt": 6,
    "maps/medium/01_dead_end_trap.txt": 12,
    "maps/medium/02_circular_loop.txt": 15,
    "maps/medium/03_priority_puzzle.txt": 12,
    "maps/hard/01_maze_nightmare.txt": 30,
    "maps/hard/02_capacity_hell.txt": 35,
    "maps/hard/03_ultimate_challenge.txt": 45,
    "maps/challenger/01_the_impossible_dream.txt": 45,
}

if not os.path.exists(os.path.join(root, "venv")):
    print("Installing dependencies...")
    subprocess.run(["make", "install"], cwd=root)


def run_map(path: str) -> None:
    """Run a single map and print the result."""
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

        # Check target if this map has one
        normalized = path.replace("\\", "/")
        if normalized in TARGETS:
            target = TARGETS[normalized]
            match = re.search(r"Total turns:\s+(\d+)", output)
            if match:
                turns = int(match.group(1))
                if turns <= target:
                    print(
                        f"{GREEN}TARGET ✅ {turns} turns "
                        f"(target ≤ {target}){RESET}"
                    )
                else:
                    print(
                        f"{RED}TARGET ❌ {turns} turns "
                        f"(target ≤ {target}){RESET}"
                    )

    elif output.startswith("Error:"):
        print(f"{YELLOW}CONTROLLED ERROR{RESET}")
        print(f"{RED}{output}{RESET}")
    else:
        print(f"{RED}[PYTHON ERROR]{RESET}")
        print(error)


def run_directory(dir_path: str, label: str) -> None:
    """Run all .txt files in a directory recursively."""
    if not os.path.exists(dir_path):
        print(f"{RED}Directory not found: {dir_path}{RESET}")
        return

    maps = []
    for dirpath, _, filenames in os.walk(dir_path):
        for f in sorted(filenames):
            if f.endswith(".txt"):
                maps.append(os.path.join(dirpath, f))

    if not maps:
        print(f"{YELLOW}No .txt files found in {dir_path}{RESET}")
        return

    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}{label}{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")

    for map_path in sorted(maps):
        relative = os.path.relpath(map_path, root)
        print(f"\n--- {relative} ---")
        run_map(relative)


# Run tests/
tests_dir = os.path.join(root, "tests")
run_directory(tests_dir, "TESTS")

# Run maps/
maps_dir = os.path.join(root, "maps")
run_directory(maps_dir, "MAPS")
