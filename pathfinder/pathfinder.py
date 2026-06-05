#!/usr/bin/env python3
"""Module for drone pathfinding and routing logic."""

from models.zone import Zone
from models.graph import Graph
from typing import List


class PathFinder:
    """
    Algorithm provider for finding the most efficient routes for drones.

    This class implements search algorithms to navigate the zone network,
    accounting for movement costs, zone types, and connectivity.

    Attributes:
        graph: A validated Graph instance representing the drone network.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initializes the PathFinder with a graph.

        Args:
            graph: A validated Graph instance representing the drone network.
        """
        self.graph = graph

    def get_neighbors(self, zone: Zone) -> List[Zone]:
        """
        Retrieves all accessible adjacent zones that are not blocked.

        Args:
            zone: The Zone object to check neighbors from.

        Returns:
            A list of accessible Zone objects connected to the input zone.
            Zones of type 'blocked' are excluded.
        """
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

    def dfs(
        self,
        current_zone: Zone,
        current_path: List[Zone],
        visited: set[Zone],
        end: Zone,
        all_paths: List[List[Zone]],
    ) -> None:
        """
        Performs a Depth-First Search to find all possible simple paths.

        Args:
            current_zone: The zone being currently explored.
            current_path: The sequence of zones traversed so far.
            visited: Set of zones already in the current path to avoid cycles.
            end: The target destination zone.
            all_paths: A list to store all discovered valid paths.
        """
        for neighbor in self.get_neighbors(current_zone):
            if neighbor == end:
                all_paths.append(current_path + [neighbor])
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                current_path.append(neighbor)
                self.dfs(neighbor, current_path, visited, end, all_paths)
                current_path.pop()
                visited.remove(neighbor)

    def find_all_paths(self, start: Zone, end: Zone) -> List[List[Zone]]:
        """
        Finds all non-cyclic paths from start to end.
        Useful for distributing drones across multiple paths to maximize
        throughput.

        Args:
            start: The starting hub.
            end: The destination hub.

        Returns:
            A list containing all valid paths (each path is a list of Zones).
        """
        all_paths: List[List[Zone]] = []
        self.dfs(start, [start], {start}, end, all_paths)
        return all_paths
