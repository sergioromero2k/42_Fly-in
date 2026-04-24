#!/usr/bin/env python3

from models.graph import Graph


class TerminalVisualizer:
    COLORS = {
        "green": "\033[32m",
        "red": "\033[31m",
        "blue": "\033[34m",
        "yellow": "\033[33m",
        "gray": "\033[90m",
        "orange": "\033[91m",
        "cyan": "\033[36m",
        "brown": "\033[33m",
        "lime": "\033[92m",
        "gold": "\033[93m",
        "purple": "\033[35m",
        "magenta": "\033[35m",
        "white": "\033[37m",
        "black": "\033[30m",
        "reset": "\033[0m",
    }

    def __init__(self, graph: Graph):
        self.graph = graph

    def get_color(self, zone_name: str) -> str:
        for zone in self.graph.zones:
            if zone_name == zone.name:
                if zone.color:
                    return self.COLORS[zone.color]
        return self.COLORS["reset"]

    def print_turn(self, turn: int, movements: list[str]) -> None:
        print(f"Turn {turn}: ", end="")
        for movement in movements:
            zone_name = movement.split("-")[1]
            color = self.get_color(zone_name)
            reset = self.COLORS["reset"]
            print(f"{color}{movement}{reset}", end=" ")
        print()
