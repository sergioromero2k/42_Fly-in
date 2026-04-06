#!/usr/bin/env python3

from models.zone import Zone
from models.connection import Connection


class Graph:
    """
    Represents the entire network of zones and connections for drone routing.

    Attributes:
        zones (list[Zone]): All defined zones in the network.
        connections (list[Connection]): All bidirectional edges between zones.
        start (Zone): The designated starting hub for all drones.
        end (Zone): The target destination hub.
        nb_drones (int): The total number of drones to be routed.
    """

    def __init__(
        self,
        zones: list[Zone],
        connections: list[Connection],
        start: Zone,
        end: Zone,
        nb_drones: int,
    ):
        self.zones = zones
        self.connections = connections
        self.start = start
        self.end = end
        self.nb_drones = nb_drones

    def __str__(self) -> str:
        return (
            f"Graph: {len(self.zones)} zones, "
            f"{len(self.connections)} connections, "
            f"{self.nb_drones} drones. "
            f"Route: {self.start.name} -> {self.end.name}"
        )
