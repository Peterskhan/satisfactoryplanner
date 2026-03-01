from dataclasses import dataclass
from enum import Enum

class Rotation(Enum):
    DEG_0 = 0
    DEG_90 = 1
    DEG_180 = 2
    DEG_270 = 3

    def rotate_clockwise(self):
        return Rotation((self.value + 1) % 4)

    def rotate_counterclockwise(self):
        return Rotation((self.value - 1) % 4)

@dataclass
class Position:
    x: int
    y: int

@dataclass
class BuildingType:
    name: str
    width: int
    length: int
    category: str
    icon: str

building_types = {
    # Production
    'Constructor': BuildingType('Constructor', 8, 10, 'Production', './slapp/resources/Constructor.png'),
    'Assembler': BuildingType('Assembler', 10, 15, 'Production', './slapp/resources/Assembler.png'),
    'Manufacturer': BuildingType('Manufacturer', 18, 20, 'Production', './slapp/resources/Manufacturer.png'),
    'Foundry': BuildingType('Foundry', 10, 9, 'Production', './slapp/resources/Foundry.png'),
    'Smelter': BuildingType('Smelter', 6, 9, 'Production', './slapp/resources/Smelter.png'),
    'Refinery': BuildingType('Refinery', 10, 20, 'Production', './slapp/resources/Refinery.png'),

    # Power
    'Coal Generator': BuildingType('Coal Generator', 10, 26, 'Power', './slapp/resources/CoalGenerator.png'),
    'Fuel Generator': BuildingType('Fuel Generator', 20, 20, 'Power', './slapp/resources/FuelGenerator.png'),

    # Logistics
    'Lift (IN)': BuildingType('Lift (IN)', 2, 2, 'Logistics', './slapp/resources/LiftIn.png'),
    'Lift (OUT)': BuildingType('Lift (OUT)', 2, 2, 'Logistics', './slapp/resources/LiftOut.png'),
    'Splitter': BuildingType('Splitter', 4, 4, 'Logistics', './slapp/resources/Splitter.png'),
    'Merger': BuildingType('Merger', 4, 4, 'Logistics', './slapp/resources/Merger.png'),
    'Pipe Junction': BuildingType('Pipe Junction', 4, 4, 'Logistics', './slapp/resources/PipeJunction.png'),

    # Organisation
    'Storage container': BuildingType('Storage container', 10, 5, 'Organisation', './slapp/resources/StorageContainer.png'),

    # Other
    'AWESOME Sink': BuildingType('AWESOME Sink', 16, 13, 'Other', './slapp/resources/Sink.png'),
}

class DiscreteElement:
    type: BuildingType
    position: Position
    rotation: Rotation

    def __init__(self, type: BuildingType, position: Position, rotation: Rotation) -> None:
        """Initialize a building instance with a type, position, and rotation."""
        self.type = type
        self.position = position
        self.rotation = rotation

    def clone(self) -> 'DiscreteElement':
        """Create a copy of this building instance."""
        return DiscreteElement(self.type, Position(self.position.x, self.position.y), self.rotation)

    def translate(self, dx: int, dy: int) -> None:
        """Move the building by dx and dy."""
        self.position.x += dx
        self.position.y += dy

    def move_to(self, x: int, y: int) -> None:
        """Move the building to a specific position."""
        self.position.x = x
        self.position.y = y

    def rotate_clockwise(self) -> None:
        """Rotate the building 90 degrees clockwise."""
        self.rotation = self.rotation.rotate_clockwise()

    def rotate_counterclockwise(self) -> None:
        """Rotate the building 90 degrees counterclockwise."""
        self.rotation = self.rotation.rotate_counterclockwise()

    def to_dict(self) -> dict:
        return {
            "type": self.type.name,  # or some unique identifier
            "position": {"x": self.position.x, "y": self.position.y},
            "rotation": self.rotation.value
        }

    @classmethod
    def from_dict(cls, data: dict, type_lookup: dict) -> "DiscreteElement":
        # type_lookup maps type name to BuildingType
        type_obj = type_lookup[data["type"]]
        pos = Position(data["position"]["x"], data["position"]["y"])
        rot = Rotation(data["rotation"])
        return cls(type_obj, pos, rot)
