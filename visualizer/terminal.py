#!/usr/bin/env python3
"""Module for terminal-based visual output of the drone simulation."""

from models.graph import Graph


class TerminalVisualizer:
    """
    Handles the colored text output in the terminal for simulation turns.

    This class maps zone colors defined in the map file to ANSI escape codes,
    allowing the simulation progress to be easily monitored in the console.

    Attributes:
        graph: The Graph instance used to look up zone metadata (colors).
        COLORS: A dictionary mapping color names to ANSI escape sequences.
    """

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
        "maroon": "\033[31m",
        "darkred": "\033[31m",
        "violet": "\033[35m",
        "crimson": "\033[31m",
        "rainbow": "\033[93m",
    }

    def __init__(self, graph: Graph):
        """
        Initializes the visualizer with the current graph.

        Args:
            graph: The Graph object containing the network data.
        """
        self.graph = graph

    def get_color(self, zone_name: str) -> str:
        """
        Retrieves the ANSI color code for a specific zone.

        Args:
            zone_name: The name of the zone to look up.

        Returns:
            A string containing the ANSI escape code for the zone's color,
            or the 'reset' code if no specific color is found.
        """
        for zone in self.graph.zones:
            if zone_name == zone.name:
                if zone.color:
                    return self.COLORS[zone.color]
        return self.COLORS["reset"]

    def print_turn(self, turn: int, movements: list[str]) -> None:
        """
        Prints the movements of a single turn to the terminal with colors.

        Output format: Turn X: D1-ZoneA D2-ZoneB ...

        Args:
            turn: The current turn number.
            movements: A list of strings in the format 'D<id>-<zone_name>'.
        """
        print(f"Turn {turn}: ", end="")
        for movement in movements:
            zone_name = movement.split("-")[1]
            color = self.get_color(zone_name)
            reset = self.COLORS["reset"]
            print(f"{color}{movement}{reset}", end=" ")
        print()
