#!/usr/bin/env python3
"""Module defining the Drone entity and its state within the simulation."""

from models.zone import Zone
from typing import List


class Drone:
    """
    Represents an autonomous drone within the simulation.

    Attributes:
        id (int): Unique identifier for the drone.
        current_zone (Zone): The zone where the drone is currently located.
        path (List[Zone]): The planned sequence of zones
            to reach the destination.
        path_index (int): Current step index within the assigned path.
        state (str): Current operational status (e.g., "waiting", "moving").
    """
    def __init__(
            self, id: int, current_zone: Zone, path: List[Zone]) -> None:
        self.id = id
        self.current_zone = current_zone
        self.path = path
        self.path_index = 0
        self.state = "waiting"

    def __str__(self) -> str:
        return (
            f"id: {self.id}"
            f", zone: {self.current_zone.name}"
            f", state: {self.state}"
        )
