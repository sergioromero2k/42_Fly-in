#!/usr/bin/env python3
"""Module for parsing drone network configuration files."""
import re
from models.zone import Zone
from models.connection import Connection
from models.graph import Graph
from typing import List

MAX_VALUE = 1000


class Parser:
    """Class responsible for parsing map files into a Graph object."""

    def parse_zone(self, tokens: List[str]) -> Zone:
        """
        Parses a zone definition line and extracts metadata.
        Its only job is to convert a list of words into a Zone object.

        Args:
            tokens: A list of strings representing the split line
            from the file.

        Returns:
            A Zone object populated with the parsed data.

        Raises:
            ValueError: If an invalid zone type is encountered.
        """
        name = tokens[1]
        try:
            x = int(tokens[2])
            y = int(tokens[3])
        except (ValueError, IndexError):
            raise ValueError(
                "Error: zone coordinates must be valid integers and present.")
        zone_type = "normal"
        color = None
        max_drones = 1
        VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

        metadata_matches = re.findall(r'\[([^\]]*)\]', " ".join(tokens[4:]))
        if metadata_matches:
            combined = " ".join(metadata_matches)
            pairs = re.findall(r'(\w+)=(-?\w+)', combined)
            if not pairs and combined.strip():
                raise ValueError(
                    f"Error: invalid metadata format '{combined}', "
                    "expected 'key=value'")
            for key, value in pairs:
                if key == "zone":
                    if value not in VALID_ZONE_TYPES:
                        raise ValueError(f"Error: invalid zone type '{value}'")
                    zone_type = value
                elif key == "color":
                    color = value
                elif key == "max_drones":
                    max_drones = self._parse_positive_int(value, "max_drones")

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
                if not line or line.startswith("#"):
                    continue
                elif line.startswith("nb_drones:"):
                    tokens = line.split()
                    nb_drones = self._parse_positive_int(
                        tokens[1], "nb_drones")
                elif line.startswith(("start_hub:", "end_hub:", "hub:")):
                    name_match = re.search(
                        r'(?:start_hub|end_hub|hub):\s+(.+?)\s+\d+\s+\d+',
                        line)
                    if not name_match:
                        raise ValueError(
                            "Error: invalid zone definition. "
                            "Expected: <type>: <name> <x> <y>")
                    zone_name = name_match.group(1).strip()
                    if "-" in zone_name or " " in zone_name:
                        raise ValueError(
                            f"Error: zone name '{zone_name}' "
                            "cannot contain dashes or spaces.")
                    tokens = line.split()
                    zone = self.parse_zone(tokens)
                    self._register_zone(zone, seen_zones, zones)
                    if line.startswith("start_hub:"):
                        if start is not None:
                            raise ValueError(
                                "Error: multiple start_hubs defined.")
                        start = zone
                    elif line.startswith("end_hub:"):
                        if end is not None:
                            raise ValueError(
                                "Error: multiple end_hubs defined.")
                        end = zone
                elif line.startswith("connection:"):
                    clean_conn = line[11:].strip()
                    conn_part = clean_conn.split("[")[0].strip()
                    zone_names = conn_part.split("-")

                    if (
                        len(zone_names) != 2
                        or not zone_names[0]
                        or not zone_names[1]
                    ):
                        raise ValueError("Error: invalid connection syntax.")

                    pair = frozenset([zone_names[0], zone_names[1]])
                    if pair in seen_connections:
                        raise ValueError(
                            "Error: duplicate connection "
                            f"'{zone_names[0]}-{zone_names[1]}'")
                    seen_connections.add(pair)
                    zone_a = next(
                        (z for z in zones if z.name == zone_names[0]), None)
                    zone_b = next(
                        (z for z in zones if z.name == zone_names[1]), None)

                    max_link_capacity = 1
                    cap_match = re.search(
                        r'max_link_capacity=([^\s\]]+)', line)
                    if cap_match:
                        max_link_capacity = self._parse_positive_int(
                            cap_match.group(1), "max_link_capacity")

                    if zone_a is None:
                        raise ValueError(
                            f"Error: unknown zone '{zone_names[0]}'"
                            " in connection")
                    if zone_b is None:
                        raise ValueError(
                            f"Error: unknown zone '{zone_names[1]}'"
                            " in connection")

                    connections.append(
                        Connection(zone_a, zone_b, max_link_capacity))
        if start is None:
            raise ValueError("Error: no start_hub in map file")
        if end is None:
            raise ValueError("Error: no end_hub found in map file")

        return Graph(zones, connections, start, end, nb_drones)

    def _parse_positive_int(self, value: str, field: str) -> int:
        """Parses and validates a positive integer within MAX_VALUE."""
        try:
            result = int(value)
        except ValueError:
            raise ValueError(f"Error: {field} must be a valid integer.")
        if result <= 0:
            raise ValueError(f"Error: {field} must be a positive integer.")
        if result > MAX_VALUE:
            raise ValueError(f"Error: {field} cannot exceed {MAX_VALUE}.")
        return result

    def _register_zone(self, zone: Zone, seen_zones: set, zones: list) -> None:
        """Registers a zone and checks for duplicates."""
        if zone.name in seen_zones:
            raise ValueError(f"Error: duplicate zone name '{zone.name}'")
        seen_zones.add(zone.name)
        zones.append(zone)
