import json
from slapp.core.DiscreteElement import DiscreteElement, building_types
from slapp.core.LinearElement import LinearElement, line_types

class FactoryLayout:

    def __init__(self):
        self.buildings = []
        self.lines = []

    @staticmethod
    def create_from_buildings(buildings: list[DiscreteElement]) -> 'FactoryLayout':
        layout = FactoryLayout()
        for building in buildings:
            layout.add_instance(building.clone())
        return layout

    def clear(self) -> None:
        """Clear every element from the layout."""
        self.buildings.clear()
        self.lines.clear()

    def clone(self) -> 'FactoryLayout':
        new_layout = FactoryLayout()
        for building in self.buildings:
            new_layout.add_instance(building.clone())
        return new_layout

    def add_sublayout(self, sublayout: 'FactoryLayout', offset_x: int, offset_y: int) -> None:
        for building in sublayout.buildings:
            building.translate(offset_x, offset_y)
            self.add_instance(building)

    def add_instance(self, instance: DiscreteElement | LinearElement) -> None:
        if isinstance(instance, DiscreteElement):
            self.buildings.append(instance)
        elif isinstance(instance, LinearElement):
            self.lines.append(instance)

    def add_line(self, instance: LinearElement) -> None:
        self.lines.append(instance)

    def remove_instance(self, instance: DiscreteElement | LinearElement) -> None:
        if isinstance(instance, DiscreteElement):
            self.buildings.remove(instance)
        elif isinstance(instance, LinearElement):
            self.lines.remove(instance)

    def serialize(self) -> str:
        building_data = [b.to_dict() for b in self.buildings]
        line_data = [l.to_dict() for l in self.lines]
        result = {
            'buildings': building_data,
            'lines': line_data
        }
        return json.dumps(result, indent=2)

    def deserialize(self, json_str: str):
        data = json.loads(json_str)
        self.buildings = [DiscreteElement.from_dict(d, building_types) for d in data['buildings']]
        self.lines = [LinearElement.from_dict(d, line_types) for d in data['lines']]
