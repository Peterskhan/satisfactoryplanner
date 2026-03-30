from PySide6.QtCore import QObject, Signal, QPointF
from dataclasses import dataclass
from slapp.resources.loader import ResourceLoader

@dataclass
class BuildingType:
    name: str
    width: int
    length: int
    category: str
    texture: str
    icon: str

    power_connection: QPointF = None
    input_positions: list[QPointF] = None
    output_positions: list[QPointF] = None
    snap_center: bool = False

building_types = {
    # Production
    'Constructor': BuildingType('Constructor', 8, 10, 'Production',
                                ResourceLoader.load(':/buildings/Constructor.png'),
                                ResourceLoader.load(':/building_icons/IconDesc_ConstructorMk1_512.png'),
                                QPointF(2.1, -4.7),
                                [QPointF(0, -5)],
                                [QPointF(0, 5)]),

    'Assembler': BuildingType('Assembler', 10, 15, 'Production',
                              ResourceLoader.load(':/buildings/Assembler.png'),
                              ResourceLoader.load(':/building_icons/IconDesc_AssemblerMk1_512.png'),
                              QPointF(4.7, 1.2),
                              [QPointF(-2, -6.5), QPointF(2, -6.5)],
                              [QPointF(0, 6.5)]),

    'Manufacturer': BuildingType('Manufacturer', 18, 20, 'Production',
                                 ResourceLoader.load(':/buildings/Manufacturer.png'),
                                 ResourceLoader.load(':/building_icons/IconDesc_Manufacturer_512.png'),
                                 QPointF(8.4, 5.8),
                                 [QPointF(-6, -10), QPointF(-2, -10), QPointF(2, -10), QPointF(6, -10)],
                                 [QPointF(0, 10)]),

    'Foundry': BuildingType('Foundry', 10, 9, 'Production',
                            ResourceLoader.load(':/buildings/Foundry.png'),
                            ResourceLoader.load(':/building_icons/IconDesc_Foundry_512.png'),
                            QPointF(4.2, -3.2),
                            [QPointF(-2, -4.5), QPointF(2, -4.5)],
                            [QPointF(-2, 4.5)]),

    'Smelter': BuildingType('Smelter', 6, 9, 'Production',
                            ResourceLoader.load(':/buildings/Smelter.png'),
                            ResourceLoader.load(':/building_icons/IconDesc_SmelterMk1_512.png'),
                            QPointF(-2.3, 2.4),
                            [QPointF(0, -4.5)],
                            [QPointF(0, 4.5)]),

    'Refinery': BuildingType('Refinery', 10, 20, 'Production',
                             ResourceLoader.load(':/buildings/Refinery.png'),
                             ResourceLoader.load(':/building_icons/IconDesc_OilRefinery_512.png'),
                             QPointF(0, 9.6),
                             [QPointF(-2, -10), QPointF(2, -10)],
                             [QPointF(-2, 10), QPointF(2, 10)]),

    # Power
    'Coal Generator': BuildingType('Coal Generator', 10, 26, 'Power',
                                   ResourceLoader.load(':/buildings/CoalGenerator.png'),
                                   ResourceLoader.load(':/building_icons/IconDesc_CoalGenerator_512.png'),
                                   QPointF(-2.7, -12.7),
                                   [QPointF(-2, 12), QPointF(2, 12)],
                                   []),

    'Fuel Generator': BuildingType('Fuel Generator', 20, 20, 'Power',
                                   ResourceLoader.load(':/buildings/FuelGenerator.png'),
                                   ResourceLoader.load(':/building_icons/FuelGenerator_512.png'),
                                   QPointF(0, 5.5),
                                   [QPointF(0, -9)],
                                   []),

    # Logistics
    'Lift (IN)': BuildingType('Lift (IN)', 2, 2, 'Logistics',
                              ResourceLoader.load(':/buildings/LiftIn.png'),
                              ResourceLoader.load(':/building_icons/ConveyorLiftMK1_512.png'),
                              None,
                              [QPointF(0, 1)],
                              []),

    'Lift (OUT)': BuildingType('Lift (OUT)', 2, 2, 'Logistics',
                               ResourceLoader.load(':/buildings/LiftOut.png'),
                               ResourceLoader.load(':/building_icons/ConveyorLiftMK1_512.png'),
                               None,
                               [],
                               [QPointF(0, 1)]),

    'Splitter': BuildingType('Splitter', 4, 4, 'Logistics',
                             ResourceLoader.load(':/buildings/Splitter.png'),
                             ResourceLoader.load(':/building_icons/IconDesc_ConveyorSplitter_512.png'),
                             None,
                             [QPointF(2, 0)],
                             [QPointF(0, -2), QPointF(-2, 0), QPointF(0, 2)]),

    'Merger': BuildingType('Merger', 4, 4, 'Logistics',
                           ResourceLoader.load(':/buildings/Merger.png'),
                           ResourceLoader.load(':/building_icons/IconDesc_ConveyorMerger_512.png'),
                           None,
                           [QPointF(0, -2), QPointF(-2, 0), QPointF(0, 2)],
                           [QPointF(2, 0)]),

    'Pipe Junction': BuildingType('Pipe Junction', 4, 4, 'Logistics', ResourceLoader.load(':/buildings/PipeJunction.png'), ResourceLoader.load(':/building_icons/PipelineJunction_512.png')),

    # Organisation
    'Storage container': BuildingType('Storage container', 5, 10, 'Organisation',
                                      ResourceLoader.load(':/buildings/StorageContainer.png'),
                                      ResourceLoader.load(':/building_icons/IconDesc_StorageContainer_512.png'),
                                      snap_center=True),

    # Other
    'AWESOME Sink': BuildingType('AWESOME Sink', 16, 13, 'Other',
                                 ResourceLoader.load(':/buildings/Sink.png'),
                                 ResourceLoader.load(':/building_icons/ResourceSink_512.png'),
                                 None,
                                 [QPointF(-2, 6.5)],
                                 []),
}

class DiscreteElement(QObject):
    type: BuildingType
    position: QPointF
    rotation: float

    position_changed = Signal(QPointF)
    rotation_changed = Signal(float)

    def __init__(self, type: BuildingType, position: QPointF, rotation: float = 0) -> None:
        """Initialize a building instance with a type, position, and rotation."""
        super().__init__()
        self.type = type
        self.position = position
        self.rotation = rotation

    def clone(self) -> 'DiscreteElement':
        """Create a copy of this building instance."""
        return DiscreteElement(self.type, QPointF(self.position), self.rotation)

    def translate(self, offset: QPointF) -> None:
        """Move the building by dx and dy."""
        self.position += offset
        self.position_changed.emit(self.position)

    def move_to(self, new_position: QPointF) -> None:
        """Move the building to a specific position."""
        self.position = new_position
        self.position_changed.emit(self.position)

    def rotate(self, degrees: float = 90) -> None:
        """Rotate the building 90 degrees clockwise."""
        self.rotation = (self.rotation + degrees) % 360
        self.rotation_changed.emit(self.rotation)

    def serialize(self) -> None:
        return {
            'type': self.type.name,
            'position': { 'x': self.position.x(), 'y': self.position.y() },
            'rotation': self.rotation
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'DiscreteElement':
        type_obj = building_types[data['type']]
        pos = QPointF(data['position']['x'], data['position']['y'])
        rot = data['rotation']
        return cls(type_obj, pos, rot)
