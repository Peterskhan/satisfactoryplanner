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

building_types = [
    # Production
    BuildingType('Constructor', 8, 10, 'Production', './resources/Constructor.png'),
    BuildingType('Assembler', 10, 15, 'Production', './resources/Assembler.jpg'),
    BuildingType('Manufacturer', 18, 20, 'Production', './resources/Manufacturer.png'),
    BuildingType('Foundry', 10, 9, 'Production', './resources/Foundry.png'),
    BuildingType('Smelter', 6, 9, 'Production', './resources/Smelter.png'),
    BuildingType('Refinery', 10, 20, 'Production', './resources/Refinery.png'),

    # Power
    BuildingType('Coal Generator', 10, 26, 'Power', './resources/CoalGenerator.png'),
    BuildingType('Fuel Generator', 20, 20, 'Power', './resources/FuelGenerator.png'),

    # Logistics
    BuildingType('Lift (IN)', 2, 2, 'Logistics', './resources/LiftIn.png'),
    BuildingType('Lift (OUT)', 2, 2, 'Logistics', './resources/LiftOut.png'),
    BuildingType('Splitter', 4, 4, 'Logistics', './resources/Splitter.png'),
    BuildingType('Merger', 4, 4, 'Logistics', './resources/Merger.png'),
    BuildingType('Pipe Junction', 4, 4, 'Logistics', './resources/PipeJunction.png'),

    # Organisation
    BuildingType('Storage container', 10, 5, 'Organisation', './resources/StorageContainer.png'),

    # Other
    BuildingType('AWESOME Sink', 16, 13, 'Other', './resources/Sink.png'),
]

class BuildingInstance:
    type: BuildingType
    position: Position
    rotation: Rotation

    def __init__(self, type: BuildingType, position: Position, rotation: Rotation) -> None:
        """Initialize a building instance with a type, position, and rotation."""
        self.type = type
        self.position = position
        self.rotation = rotation

    def clone(self) -> 'BuildingInstance':
        """Create a copy of this building instance."""
        return BuildingInstance(self.type, Position(self.position.x, self.position.y), self.rotation)

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
    def from_dict(cls, data: dict, type_lookup: dict) -> "BuildingInstance":
        # type_lookup maps type name to BuildingType
        type_obj = type_lookup[data["type"]]
        pos = Position(data["position"]["x"], data["position"]["y"])
        rot = Rotation(data["rotation"])
        return cls(type_obj, pos, rot)