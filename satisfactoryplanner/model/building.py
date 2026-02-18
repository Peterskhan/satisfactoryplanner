
from dataclasses import dataclass

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