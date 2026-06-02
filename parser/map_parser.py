#!/usr/bin/env python3
"""Module for parsing drone network configuration files."""
from models.zone import Zone
from models.connection import Connection
from models.graph import Graph
from typing import List

MAX_VALUE = 1000


class Parser:
    """Class responsible for parsing map files into a Graph object."""

    def parse_zone(self, parts: List[str]) -> Zone:
        """Parses a zone definition line and extracts metadata.

        Args:
            parts: A list of strings representing the split line from the file.

        Returns:
            A Zone object populated with the parsed data.

        Raises:
            ValueError: If an invalid zone type is encountered.
        """
        name = parts[1]
        if "-" in name or " " in name:
            raise ValueError(
                f"Error: zone name '{name}' cannot contain dashes or spaces."
            )

        try:
            x = int(parts[2])
            y = int(parts[3])
        except ValueError:
            raise ValueError("Error: zone coordinates must be valid integers.")
        zone_type = "normal"
        color = None
        max_drones = 1
        VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

        if len(parts) > 4:
            metadata_parts = parts[4:]
            for meta in metadata_parts:
                meta = meta.replace("[", "").replace("]", "")
                parts_meta = meta.split("=")
                if len(parts_meta) != 2:
                    raise ValueError(
                        f"Error: invalid metada format '{meta}', "
                        "expected 'key=value'"
                    )
                clave = parts_meta[0]
                value = parts_meta[1]
                if clave == "zone":
                    if value not in VALID_ZONE_TYPES:
                        raise ValueError(f"Error: invalid zone type '{value}'")
                    zone_type = value
                elif clave == "color":
                    color = value
                elif clave == "max_drones":
                    try:
                        max_drones = int(value)
                    except ValueError:
                        raise ValueError(
                            "Error: max_drones must be valid integers.")
                    if max_drones <= 0:
                        raise ValueError(
                            "Error: max_drones must be a positive integer.")
                    if max_drones > MAX_VALUE:
                        raise ValueError(
                            f"Error: max_drones cannot exceed {MAX_VALUE}."
                        )

        return Zone(name, x, y, zone_type, color, max_drones)

    def parse(self, filepath: str) -> Graph:
        """Reads a file and constructs the Graph
            representing the drone network.

        Args:
            filepath: Path to the input map file.

        Returns:
            A fully initialized Graph object.

        Raises:
            ValueError: If parsing fails due to syntax errors, missing hubs,
                duplicate connections, or invalid drone counts.
            FileNotFoundError: If the specified file does not exist.
        """
        zones = []
        connections = []
        start = None
        end = None
        nb_drones = 0
        seen_connections = set()
        seen_zones = set()

        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line.startswith("nb_drones:"):
                    parts = line.split()
                    try:
                        nb_drones = int(parts[1])
                    except ValueError:
                        raise ValueError(
                            "Error: nb_drones must be a valid integer.")
                    if nb_drones <= 0:
                        raise ValueError(
                            "Error: nb_drones must be a positive integer.")
                    if nb_drones > MAX_VALUE:
                        raise ValueError(
                            f"Error: nb_drones cannot exceed {MAX_VALUE}."
                        )
                elif line.startswith("start_hub:"):
                    parts = line.split()
                    start = self.parse_zone(parts)
                    if start.name in seen_zones:
                        raise ValueError(
                            f"Error: duplicate zone name '{start.name}'")
                    seen_zones.add(start.name)
                    zones.append(start)
                elif line.startswith("end_hub:"):
                    parts = line.split()
                    end = self.parse_zone(parts)
                    if end.name in seen_zones:
                        raise ValueError(
                            f"Error: duplicate zone name '{end.name}'")
                    seen_zones.add(end.name)
                    zones.append(end)
                elif line.startswith("hub:"):
                    parts = line.split()
                    zone = self.parse_zone(parts)
                    if zone.name in seen_zones:
                        raise ValueError(
                            f"Error: duplicate zone name '{zone.name}'")
                    seen_zones.add(zone.name)
                    zones.append(zone)
                elif line.startswith("connection:"):
                    parts = line.split()
                    names = parts[1].split("-")

                    pair = frozenset([names[0], names[1]])
                    if pair in seen_connections:
                        raise ValueError(
                            "Error: duplicate connection "
                            f"'{names[0]}-{names[1]}'")
                    seen_connections.add(pair)
                    zona_a = next(
                        (z for z in zones if z.name == names[0]), None)
                    zona_b = next(
                        (z for z in zones if z.name == names[1]), None)

                    max_link_capacity = 1
                    if len(parts) > 2:
                        meta = parts[2].replace("[", "").replace("]", "")
                        parts_meta = meta.split("=")
                        if parts_meta[0] == "max_link_capacity":
                            try:
                                max_link_capacity = int(parts_meta[1])
                            except ValueError:
                                raise ValueError(
                                    "Error: max_link_capacity "
                                    "must be valid integers")
                            if max_link_capacity <= 0:
                                raise ValueError(
                                    "Error: max_link_capacity must be"
                                    " a positive integer.")
                            if max_link_capacity > MAX_VALUE:
                                raise ValueError(
                                    "Error: max_link_capacity "
                                    f"cannot exceed {MAX_VALUE}.")
                    if zona_a is None:
                        raise ValueError(
                            f"Error: unknown zone '{names[0]}' in connection")
                    if zona_b is None:
                        raise ValueError(
                            f"Error: unknown zone '{names[1]}' in connection")

                    connections.append(
                        Connection(zona_a, zona_b, max_link_capacity))
        if start is None:
            raise ValueError("Error: no start_hub in map file")
        if end is None:
            raise ValueError("Error: no end_hub found in map file")

        return Graph(zones, connections, start, end, nb_drones)
