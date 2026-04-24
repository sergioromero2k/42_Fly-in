#!/usr/bin/env python3

import sys
from parser.map_parser import Parser
from simulator.simulator import Simulator


def main() -> None:

    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)

    try:
        parser = Parser()
        graph = parser.parse(sys.argv[1])
        sim = Simulator(graph)
        sim.run()
    except FileNotFoundError:
        print(f"Error: file '{sys.argv[1]}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
