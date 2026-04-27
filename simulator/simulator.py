#!/usr/bin/env python3
"""Main simulation engine for drone fleet management."""

from models.graph import Graph
from models.zone import Zone
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
        """Initializes the simulator and schedules drone paths.

        Args:
            graph: A validated Graph object.

        Raises:
            ValueError: If no valid paths exist between start and end hubs.
        """
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
        paths = [p for p in paths if len(p) <= shortest + 2]

        if not paths:
            paths = pathfinder.find_all_paths(self.graph.start, self.graph.end)
            paths.sort(key=lambda p: len(p))

        drones_per_path = [0] * len(paths)  # ← AQUÍ, después del filtro

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

    def compute_turn(self) -> List:
        """
        Calculates valid movements for the current turn.

        This method checks zone capacities and moves drones to their next
        destination if allowed.

        Returns:
            A list of strings formatted as 'D<id>-<zone_name>' for the output.
        """
        ocupation: dict[Zone, int] = self.get_ocupation()
        movemts = []

        for drone in self.drones:
            if drone.state == "arrived":
                continue
            if drone.path_index + 1 < len(drone.path):
                next_zone = drone.path[drone.path_index + 1]
                if self.can_move(next_zone, ocupation):
                    ocupation[drone.current_zone] = ocupation.get(
                        drone.current_zone, 0) - 1
                    ocupation[next_zone] = ocupation.get(next_zone, 0) + 1
                    drone.current_zone = next_zone
                    drone.path_index += 1
                    movemts.append(f"D{drone.id}-{next_zone.name}")
                    if next_zone == self.graph.end:
                        drone.state = "arrived"
        return movemts

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

    def can_move(self, next_zone: Zone, ocupation: dict[Zone, int]) -> bool:
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
        if ocupation.get(next_zone, 0) >= next_zone.max_drone:
            return False
        return True
