#!/usr/bin/env python3

import sys
from parser.map_parser import Parser
from simulator.simulator import Simulator


def main() -> None:
    # parser = Parser()
    # graph_1 = parser.parse("maps/easy/01_linear_path.txt")
    # graph_2 = parser.parse("maps/easy/02_simple_fork.txt")
    # graph_3 = parser.parse("maps/easy/03_basic_capacity.txt")
    # graph_4 = parser.parse("maps/hard/01_maze_nightmare.txt")

    # print(graph_1)
    # print(graph_2)
    # print(graph_3)
    # print(graph_4)

    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)

    parser = Parser()
    graph = parser.parse(sys.argv[1])
    # graph = parser.parse("maps/easy/01_linear_path.txt")
    sim = Simulator(graph)
    sim.run()

    # pf = PathFinder(graph)
    # paths = pf.find_all_paths(graph.start, graph.end)
    # print(f"Caminos encontrados: {len(paths)}")
    # for path in paths:
    #     print([z.name for z in path])


if __name__ == "__main__":
    main()
