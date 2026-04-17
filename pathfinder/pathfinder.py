#!/usr/bin/env python3

from models.zone import Zone
from models.graph import Graph
from typing import List
import heapq


class PathFinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def get_neighbors(self, zone: Zone) -> List[Zone]:
        neighbors = []
        for connection in self.graph.connections:
            if connection.zone_a == zone:
                neighbor = connection.zone_b
                if neighbor.zone_type != "blocked":
                    neighbors.append(connection.zone_b)
            elif connection.zone_b == zone:
                neighbor = connection.zone_a
                if neighbor.zone_type != "blocked":
                    neighbors.append(connection.zone_a)
        return neighbors

    def get_cost(self, zone: Zone) -> float:
        if zone.zone_type == "normal":
            return 1
        if zone.zone_type == "priority":
            return 1
        if zone.zone_type == "restricted":
            return 2
        if zone.zone_type == "blocked":
            return float("inf")
        return 1

    def find_path(self, start: Zone, end: Zone) -> List[Zone]:
        distances = {zone: float("inf") for zone in self.graph.zones}
        distances[start] = 0

        previous: dict[Zone, Zone] = {}
        visited = set()

        counter = 0
        queue: list[tuple[float, int, Zone]] = [(0, counter, start)]
        while queue:
            cost, _, zone = heapq.heappop(queue)
            if zone == end:
                path = []
                current_zone = end
                while current_zone in previous:
                    path.append(current_zone)
                    current_zone = previous[current_zone]
                path.append(start)
                path.reverse()
                return path

            if zone in visited:
                continue
            visited.add(zone)
            for neighbor in self.get_neighbors(zone):
                new_cost = cost + self.get_cost(neighbor)
                if new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    previous[neighbor] = zone
                    counter += 1
                    heapq.heappush(queue, (new_cost, counter, neighbor))
        return []
