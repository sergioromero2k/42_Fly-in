#!/usr/bin/env python3
"""Module for graphical representation of the drone
    network using Matplotlib."""

import matplotlib.pyplot as plt
from models.graph import Graph


class GraphDisplay:
    """
    Handles the 2D visual rendering of the drone network graph.

    This class uses Matplotlib to draw zones as nodes and connections as edges,
    positioning them based on their parsed coordinates.

    Attributes:
        graph: The Graph instance containing zones and connections to display.
    """
    def __init__(self, graph: Graph) -> None:
        """
        Initializes the display with a specific graph.

        Args:
            graph: The Graph object representing the network topology.
        """
        self.graph = graph

    def draw(self) -> None:
        """
        Renders the graph in a new window.

        Zones are drawn as colored circles based on their metadata, and
        connections are drawn as lines between them. The zone names are
        displayed slightly above their coordinates for clarity.
        """
        fig, ax = plt.subplots()

        for connection in self.graph.connections:
            x1 = connection.zone_a.x
            y1 = connection.zone_a.y
            x2 = connection.zone_b.x
            y2 = connection.zone_b.y
            ax.plot([x1, x2], [y1, y2], "k-")

        for zone in self.graph.zones:
            color = zone.color if zone.color else "white"
            ax.scatter(zone.x, zone.y, color=color, s=600, zorder=5)
            ax.text(
                zone.x, zone.y + 0.2, zone.name, ha="center",
                fontsize=8, zorder=10)

        plt.show()
