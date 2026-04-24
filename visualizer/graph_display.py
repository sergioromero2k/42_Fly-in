#!/usr/bin/env python3

import matplotlib.pyplot as plt
from models.graph import Graph


class GraphDisplay:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def draw(self) -> None:
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
