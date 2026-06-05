#!/usr/bin/env python3
"""Main simulation engine for drone fleet management."""

from models.graph import Graph
from models.zone import Zone
from models.connection import Connection
from simulator.drone import Drone
from pathfinder.pathfinder import PathFinder
from visualizer.terminal import TerminalVisualizer
from visualizer.graph_display import GraphDisplay
from typing import List


class Simulator:
    """
    Manages the drone simulation, handling turn-by-turn
    movement and scheduling.

    This class coordinates the pathfinding, drone deployment, and the
    enforcement of movement constraints (like zone capacity) over time.

    Attributes:
        graph: The Graph instance representing the network topology.
        drones: List of Drone objects active in the simulation.
        turn: Current simulation turn counter.
        visualizer: Component for terminal-based output.
        display: Component for graphical representation.
    """

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.drones: List[Drone] = []
        self.turn: int = 0
        self.visualizer = TerminalVisualizer(self.graph)
        self.display = GraphDisplay(graph)

        pathfinder = PathFinder(self.graph)
        paths = pathfinder.find_all_paths(self.graph.start, self.graph.end)

        if not paths:
            raise ValueError(
                "Error: no valid path found between start and end.")

        paths.sort(key=lambda p: len(p))
        shortest = len(paths[0])
        paths = [p for p in paths if len(p) == shortest]

        drones_per_path = [0] * len(paths)
        for i in range(self.graph.nb_drones):
            min_index = drones_per_path.index(min(drones_per_path))
            drones_per_path[min_index] += 1
            route = paths[min_index]
            drone = Drone(i+1, self.graph.start, route.copy())
            self.drones.append(drone)

    def run(self) -> None:
        """
        Executes the simulation loop until all drones reach the destination.

        The loop runs turn-by-turn, calculating movements
            and updating visualizers.
        """
        self.display.draw()
        max_turns = 1000
        while not all(drone.state == "arrived" for drone in self.drones):
            self.turn += 1
            if self.turn > max_turns:
                print(f"Warning: simulation stopped at {max_turns} turns")
                break
            movements = self.compute_turn()
            if movements:
                self.visualizer.print_turn(self.turn, movements)
        print("Simulation complete!")
        print("Total turns: ", self.turn)
        arrived = sum(1 for drone in self.drones if drone.state == "arrived")
        print(f"Drones delivered: {arrived}/{self.graph.nb_drones}")

    def compute_turn(self) -> List[str]:
        """
        Calculates valid movements for the current turn.
        Restricted zones cost 2 turns — drone occupies connection first turn,
        arrives at zone second turn.
        """
        ocupation: dict[Zone, int] = self.get_ocupation()
        conn_usage: dict[frozenset[Zone], int] = {}
        movements = []

        for drone in self.drones:
            if drone.state == "arrived":
                continue

            # CASO 1: dron en tránsito en conexión hacia restricted
            if drone.wait > 0:
                drone.wait -= 1
                if drone.wait == 0 and drone.next_zone is not None:
                    drone.current_zone = drone.next_zone
                    drone.path_index += 1
                    movements.append(f"D{drone.id}-{drone.current_zone.name}")
                    drone.next_zone = None
                    if drone.current_zone == self.graph.end:
                        drone.state = "arrived"
                else:
                    if drone.next_zone is not None:
                        conn_name = (
                            f"{drone.current_zone.name}_"
                            f"{drone.next_zone.name}"
                        )
                        movements.append(f"D{drone.id}-{conn_name}")
                    movements.append(f"D{drone.id}-{conn_name}")
                continue

            # CASO 2: dron en tierra intenta moverse
            if drone.path_index + 1 < len(drone.path):
                next_zone = drone.path[drone.path_index + 1]
                connection = self.get_connection(drone.current_zone, next_zone)

                if self.can_move(next_zone, ocupation, connection, conn_usage):
                    if connection:
                        pair = frozenset(
                            [connection.zone_a, connection.zone_b]
                        )
                        conn_usage[pair] = conn_usage.get(pair, 0) + 1

                    ocupation[drone.current_zone] = ocupation.get(
                        drone.current_zone, 0) - 1
                    ocupation[next_zone] = ocupation.get(next_zone, 0) + 1

                    if next_zone.zone_type == "restricted":
                        drone.wait = 1
                        drone.next_zone = next_zone

                        conn_name = (
                            f"{drone.current_zone.name}_"
                            f"{next_zone.name}"
                        )
                        movements.append(f"D{drone.id}-{conn_name}")
                    else:
                        drone.current_zone = next_zone
                        drone.path_index += 1
                        movements.append(f"D{drone.id}-{next_zone.name}")
                        if next_zone == self.graph.end:
                            drone.state = "arrived"

        return movements

    def get_connection(
            self, zone_a: Zone, zone_b: Zone) -> Connection | None:
        """Return the connection between two zones, or None."""
        for connection in self.graph.connections:
            if (
                (connection.zone_a == zone_a and connection.zone_b == zone_b)
                or
                (connection.zone_b == zone_a and connection.zone_a == zone_b)
            ):
                return connection
        return None

    def get_ocupation(self) -> dict[Zone, int]:
        """
        Calculates the current number of drones in each zone.

        Returns:
            A dictionary mapping Zone objects to the number of drones present.
        """
        ocupation: dict[Zone, int] = {}
        for drone in self.drones:
            if drone.state != "arrived":
                zone = drone.current_zone
                ocupation[zone] = ocupation.get(zone, 0) + 1
        return ocupation

    def can_move(
            self, next_zone: Zone, ocupation: dict[Zone, int],
            connection: Connection | None,
            conn_usage: dict[frozenset[Zone], int]) -> bool:
        """
            Validates if a move is legal according to zone and capacity rules.

            Args:
                next_zone: The Zone the drone is attempting to enter.
                occupation: Current count of drones per zone in this turn.

            Returns:
                True if the move is allowed, False otherwise.
        """
        if next_zone.zone_type == "blocked":
            return False
        if ocupation.get(next_zone, 0) >= next_zone.max_drones:
            return False
        if connection:
            pair = frozenset([connection.zone_a, connection.zone_b])
            if conn_usage.get(pair, 0) >= connection.max_link_capacity:
                return False
        return True
