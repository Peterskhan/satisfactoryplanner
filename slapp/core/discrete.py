from dataclasses import dataclass
from enum import Enum
from slapp.resources.loader import ResourceLoader

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
    texture: str
    icon: str

building_types = {
    # Production
    'Constructor': BuildingType('Constructor', 8, 10, 'Production', ResourceLoader.load(':/buildings/Constructor.png'), ResourceLoader.load(':/building_icons/IconDesc_ConstructorMk1_512.png')),
    'Assembler': BuildingType('Assembler', 10, 15, 'Production', ResourceLoader.load(':/buildings/Assembler.png'), ResourceLoader.load(':/building_icons/IconDesc_AssemblerMk1_512.png')),
    'Manufacturer': BuildingType('Manufacturer', 18, 20, 'Production', ResourceLoader.load(':/buildings/Manufacturer.png'), ResourceLoader.load(':/building_icons/IconDesc_Manufacturer_512.png')),
    'Foundry': BuildingType('Foundry', 10, 9, 'Production', ResourceLoader.load(':/buildings/Foundry.png'), ResourceLoader.load(':/building_icons/IconDesc_Foundry_512.png')),
    'Smelter': BuildingType('Smelter', 6, 9, 'Production', ResourceLoader.load(':/buildings/Smelter.png'), ResourceLoader.load(':/building_icons/IconDesc_SmelterMk1_512.png')),
    'Refinery': BuildingType('Refinery', 10, 20, 'Production', ResourceLoader.load(':/buildings/Refinery.png'), ResourceLoader.load(':/building_icons/IconDesc_OilRefinery_512.png')),

    # Power
    'Coal Generator': BuildingType('Coal Generator', 10, 26, 'Power', ResourceLoader.load(':/buildings/CoalGenerator.png'), ResourceLoader.load(':/building_icons/IconDesc_CoalGenerator_512.png')),
    'Fuel Generator': BuildingType('Fuel Generator', 20, 20, 'Power', ResourceLoader.load(':/buildings/FuelGenerator.png'), ResourceLoader.load(':/building_icons/FuelGenerator_512.png')),

    # Logistics
    'Lift (IN)': BuildingType('Lift (IN)', 2, 2, 'Logistics', ResourceLoader.load(':/buildings/LiftIn.png'), ResourceLoader.load(':/building_icons/ConveyorLiftMK1_512.png')),
    'Lift (OUT)': BuildingType('Lift (OUT)', 2, 2, 'Logistics', ResourceLoader.load(':/buildings/LiftOut.png'), ResourceLoader.load(':/building_icons/ConveyorLiftMK1_512.png')),
    'Splitter': BuildingType('Splitter', 4, 4, 'Logistics', ResourceLoader.load(':/buildings/Splitter.png'), ResourceLoader.load(':/building_icons/IconDesc_ConveyorSplitter_512.png')),
    'Merger': BuildingType('Merger', 4, 4, 'Logistics', ResourceLoader.load(':/buildings/Merger.png'), ResourceLoader.load(':/building_icons/IconDesc_ConveyorMerger_512.png')),
    'Pipe Junction': BuildingType('Pipe Junction', 4, 4, 'Logistics', ResourceLoader.load(':/buildings/PipeJunction.png'), ResourceLoader.load(':/building_icons/PipelineJunction_512.png')),

    # Organisation
    'Storage container': BuildingType('Storage container', 10, 5, 'Organisation', ResourceLoader.load(':/buildings/StorageContainer.png'), ResourceLoader.load(':/building_icons/IconDesc_StorageContainer_512.png')),

    # Other
    'AWESOME Sink': BuildingType('AWESOME Sink', 16, 13, 'Other', ResourceLoader.load(':/buildings/Sink.png'), ResourceLoader.load(':/building_icons/ResourceSink_512.png')),
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

    def serialize(self) -> None:
        return {
            'type': self.type.name,
            'position': { 'x': self.position.x, 'y': self.position.y },
            'rotation': self.rotation.value
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'DiscreteElement':
        type_obj = building_types[data['type']]
        pos = Position(data['position']['x'], data['position']['y'])
        rot = Rotation(data['rotation'])
        return cls(type_obj, pos, rot)
