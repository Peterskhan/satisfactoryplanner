import json
from model.BuldingInstance import BuildingInstance, building_types

type_lookup = {b.name: b for b in building_types}

class FactoryLayout:

    def __init__(self):
        self.buildings = []

    @staticmethod
    def create_from_buildings(buildings: list[BuildingInstance]) -> 'FactoryLayout':
        layout = FactoryLayout()
        for building in buildings:
            layout.add_building(building.clone())
        return layout
    
    def clone(self) -> 'FactoryLayout':
        new_layout = FactoryLayout()
        for building in self.buildings:
            new_layout.add_building(building.clone())
        return new_layout

    def add_sublayout(self, sublayout: 'FactoryLayout', offset_x: int, offset_y: int) -> None:
        for building in sublayout.buildings:
            building.translate(offset_x, offset_y)
            self.add_building(building)

    def add_building(self, instance: BuildingInstance) -> None:
        self.buildings.append(instance)

    def remove_building(self, instance: BuildingInstance) -> None:
        self.buildings.remove(instance)

    def buildings(self) -> list[BuildingInstance]:
        return list(self.buildings)

    def serialize(self) -> str:
        data = [b.to_dict() for b in self.buildings]
        result = json.dumps(data, indent=2)
        return result

    def deserialize(self, json_str: str, type_lookup: dict):
        data = json.loads(json_str)
        self.buildings = [BuildingInstance.from_dict(d, type_lookup) for d in data]