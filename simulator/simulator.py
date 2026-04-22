#!/usr/bin/env python3


from models.graph import Graph
from models.zone import Zone
from simulator.drone import Drone
from pathfinder.pathfinder import PathFinder
from typing import List


class Simulator:
    """
    Manages the drone simulation, hadling turn-by-turn movement and scheduling.

    Attributes:
        graph (Graph): The droen network topology and constraints.
        drones (List[Drone]): List of active drones in the simulation.
        turn (int): The current simulation turn count.
    """

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.drones: List[Drone] = []
        self.turn: int = 0

        pathfinder = PathFinder(self.graph)
        paths = pathfinder.find_all_paths(self.graph.start, self.graph.end)

        for i in range(self.graph.nb_drones):
            route = paths[i % len(paths)]
            drone = Drone(i+1, self.graph.start, route.copy())
            self.drones.append(drone)

    def run(self) -> None:
        """
        Executes the simulation until all drones reach the end_hub.
        """
        while not all(drone.state == "arrived" for drone in self.drones):
            self.turn += 1
            movements = self.compute_turn()
            if movements:
                print(" ".join(movements))

    def compute_turn(self) -> List:
        """
        Caclulates movements for the current turn respecting capacities.
        """
        ocupation: dict[Zone, int] = self.get_ocupation()
        movemts = []

        for drone in self.drones:
            if drone.state == "arrived":
                continue
            if drone.path_index + 1 < len(drone.path):
                next_zone = drone.path[drone.path_index + 1]
                if self.can_move(next_zone, ocupation):
                    ocupation[next_zone] = ocupation.get(next_zone, 0) + 1
                    drone.current_zone = next_zone
                    drone.path_index += 1
                    movemts.append(f"D{drone.id}-{next_zone.name}")
                    if next_zone == self.graph.end:
                        drone.state = "arrived"
        return movemts

    def get_ocupation(self) -> dict[Zone, int]:
        """
        Returns the current number of drones in each zone.
        """
        ocupation: dict[Zone, int] = {}
        for drone in self.drones:
            if drone.state != "arrived":
                zone = drone.current_zone
                ocupation[zone] = ocupation.get(zone, 0) + 1
        return ocupation

    def can_move(self, next_zone: Zone, ocupation: dict[Zone, int]) -> bool:
        """
        Validates if a move to next_node is allowed under project rules.
        """
        if next_zone.zone_type == "blocked":
            return False
        if ocupation.get(next_zone, 0) >= next_zone.max_drone:
            return False
        return True
