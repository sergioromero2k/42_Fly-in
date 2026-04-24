#!/usr/bin/env python3
"""Entry point for the drone fleet simulation."""

import sys
from parser.map_parser import Parser
from simulator.simulator import Simulator


def main() -> None:
    """
    Initializes the parser, builds the graph, and runs the simulation.

    Handles command-line arguments and basic error reporting for file
    access or parsing issues.
    """

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
