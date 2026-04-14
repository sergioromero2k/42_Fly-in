from models.zone import Zone


class Connection:
    """
    Represents a bidirectional edge between two zoens in the drone network.

    Attributes:
        zone_a (Zone): The first connected zone.
        zone_b (Zone): The second connected zone.
        max_link_capacity (int): Maximum number of drones that can traverse
            this connection simultaneously.
    """

    def __init__(self, zone_a: Zone, zone_b: Zone, max_link_capacity: int = 1):
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    def __str__(self) -> str:
        return (
            f"Zone A: {self.zone_a}, Zone B: {self.zone_b}"
            f" Max link Capacity: {self.max_link_capacity}"
        )
