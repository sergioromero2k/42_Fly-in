#!/usr/bin/env python3

from models.zone import Zone
from models.connection import Connection


class Parser:
    def parse(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line.startswith("nb_drones:"):
                    parts = line.split()
                    number = int(parts[1])
                elif line.startswith("start_hub:"):
                    parts = line.split()
                    metada_parts = parts[4:]
                    for meta in metada_parts:
                        meta.replace("]", "").replace("[", "")
                        meta.split("=")
                        calve = 
                    start = Zone(parts[1], int(parts[2]), int(parts[3]), parts[4], parts[5])
                elif line.startswith("end_hub:"):
                    parts = line.split()
                    end = Zone(parts[1], int(parts[2]), int(parts[3]), parts[4], parts[5])
                elif line.startswith("hub:"):
                    parts = line.split()
                    hub = Zone(parts[1], int(parts[2]), int(parts[3]), parts[4], parts[5])
                elif line.startswith("connection:"):
                    parts = line.split()
