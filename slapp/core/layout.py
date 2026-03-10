from slapp.core.discrete import DiscreteElement, building_types
from slapp.core.linear import LinearElement, line_types

class Layout:

    def __init__(self):
        self.buildings = []
        self.lines = []

    @staticmethod
    def from_buildings(buildings: list[DiscreteElement]) -> 'Layout':
        layout = Layout()
        for building in buildings:
            layout.add_element(building.clone())
        return layout

    def clear(self) -> None:
        """Clear every element from the layout."""
        self.buildings.clear()
        self.lines.clear()

    def clone(self) -> 'Layout':
        new_layout = Layout()
        for building in self.buildings:
            new_layout.add_element(building.clone())
        return new_layout

    def add_sublayout(self, sublayout: 'Layout', offset_x: int, offset_y: int) -> None:
        for building in sublayout.buildings:
            building.translate(offset_x, offset_y)
            self.add_element(building)

    def add_element(self, instance: DiscreteElement | LinearElement) -> None:
        if isinstance(instance, DiscreteElement):
            self.buildings.append(instance)
        elif isinstance(instance, LinearElement):
            self.lines.append(instance)

    def remove_element(self, instance: DiscreteElement | LinearElement) -> None:
        if isinstance(instance, DiscreteElement):
            self.buildings.remove(instance)
        elif isinstance(instance, LinearElement):
            self.lines.remove(instance)

    def serialize(self) -> dict:
        return {
            'buildings': [building.serialize() for building in self.buildings],
            'lines': [line.serialize() for line in self.lines]
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'Layout':
        result = cls()
        result.buildings = [DiscreteElement.deserialize(building_data) for building_data in data['buildings']]
        result.lines = [LinearElement.deserialize(line_data) for line_data in data['lines']]
        return result
