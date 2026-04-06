#!/usr/bin/env python3

from typing import Optional


class Zone:
    """
    Represents a zone within the drone routing network.

    Attributes:
        name (str): Unique identifier for the zone (cannot contain dashes).
        x (int): Horizontal coordinate of the zone.
        y (int): Vertical coordinate of the zone.
        zone_type (str): Type of zone (normal, blocked, restricted, priority).
        color (Optional[str]): Color for visual representation.
        max_drone (int): Maximum number of drones allowed simultaneously.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "Normal",
        color: Optional[str] = None,
        max_drone: int = 1,
    ):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drone = max_drone

    def __str__(self):
        return (
            f"Name: {self.name}, x: {self.x}, y: {self.y}"
            f", type_zone: {self.zone_type}, color: {self.color}, "
            f"Max drone: {self.max_drone}"
        )
