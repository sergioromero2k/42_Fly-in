#!/usr/bin/env python3
"""Module for parsing drone network configuration files."""
from models.zone import Zone
from models.connection import Connection
from models.graph import Graph
from typing import List


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
        x = int(parts[2])
        y = int(parts[3])
        zone_type = "normal"
        color = None
        max_drones = 1
        VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

        if len(parts) > 4:
            metadata_parts = parts[4:]
            for meta in metadata_parts:
                meta = meta.replace("[", "").replace("]", "")
                parts_meta = meta.split("=")
                clave = parts_meta[0]
                value = parts_meta[1]
                if clave == "zone":
                    if value not in VALID_ZONE_TYPES:
                        raise ValueError(f"Error: invalid zone type '{value}'")
                    zone_type = value
                elif clave == "color":
                    color = value
                elif clave == "max_drones":
                    max_drones = int(value)

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

        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line.startswith("nb_drones:"):
                    parts = line.split()
                    nb_drones = int(parts[1])
                    if nb_drones <= 0:
                        raise ValueError(
                            "Error: nb_drones must be a positive integer.")
                elif line.startswith("start_hub:"):
                    parts = line.split()
                    start = self.parse_zone(parts)
                    zones.append(start)
                elif line.startswith("end_hub:"):
                    parts = line.split()
                    end = self.parse_zone(parts)
                    zones.append(end)
                elif line.startswith("hub:"):
                    parts = line.split()
                    zones.append(self.parse_zone(parts))
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
                            max_link_capacity = int(parts_meta[1])

                    if zona_a is None:
                        raise ValueError("Error: no zona_a")
                    if zona_b is None:
                        raise ValueError("Error: no zona_b")

                    connections.append(
                        Connection(zona_a, zona_b, max_link_capacity))
        if start is None:
            raise ValueError("Error: no start_hub in map file")
        if end is None:
            raise ValueError("Error: no end_hub found in map file")

        return Graph(zones, connections, start, end, nb_drones)
