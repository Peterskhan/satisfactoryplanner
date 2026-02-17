
from dataclasses import dataclass

@dataclass
class BuildingType:
    name: str
    width: int
    length: int
    category: str
    icon: str

building_types = [
    BuildingType('Constructor', 8, 10, 'Production', './satisfactoryplanner/resources/Constructor.png'),
    BuildingType('Assembler', 10, 15, 'Production', './satisfactoryplanner/resources/Assembler.jpg'),
    BuildingType('Manufacturer', 18, 20, 'Production', './satisfactoryplanner/resources/Manufacturer.png'),
    BuildingType('Foundry', 10, 9, 'Production', './satisfactoryplanner/resources/Foundry.png'),
    BuildingType('Smelter', 6, 9, 'Production', './satisfactoryplanner/resources/Smelter.png'),
    BuildingType('Refinery', 10, 20, 'Production', './satisfactoryplanner/resources/Refinery.png'),

    BuildingType('Coal Generator', 10, 26, 'Power', './satisfactoryplanner/resources/CoalGenerator.png'),
    BuildingType('Fuel Generator', 20, 20, 'Power', './satisfactoryplanner/resources/FuelGenerator.png'),

    BuildingType('Lift (IN)', 2, 2, 'Logistics', './satisfactoryplanner/resources/LiftIn.png'),
    BuildingType('Lift (OUT)', 2, 2, 'Logistics', './satisfactoryplanner/resources/LiftOut.png'),
    BuildingType('Splitter', 4, 4, 'Logistics', './satisfactoryplanner/resources/Splitter.png'),
    BuildingType('Merger', 4, 4, 'Logistics', './satisfactoryplanner/resources/Merger.png'),
    BuildingType('Pipe Junction', 4, 4, 'Logistics', './satisfactoryplanner/resources/PipeJunction.png'),

    BuildingType('Storage container', 10, 5, 'Organisation', './satisfactoryplanner/resources/StorageContainer.png'),

    BuildingType('AWESOME Sink', 16, 13, 'Other', './satisfactoryplanner/resources/Sink.png'),
]