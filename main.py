#!/usr/bin/env python3

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

    parser = Parser()
    graph = parser.parse("maps/challenger/01_the_impossible_dream.txt")
    sim = Simulator(graph)
    sim.run()


if __name__ == "__main__":
    main()
