import json
from dataclasses import dataclass
from enum import Enum
from .building import BuildingType, building_types

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

type_lookup = {b.name: b for b in building_types}

class BuildingInstance:
    type: BuildingType
    position: Position
    rotation: Rotation

    def __init__(self, type: BuildingType, position: Position, rotation: Rotation) -> None:
        self.type = type
        self.position = position
        self.rotation = rotation

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

class LayoutModel:

    def __init__(self):
        self.buildings = []

    def add_building(self, type: BuildingType, position: Position, rotation: Rotation) -> BuildingInstance:
        instance = BuildingInstance(type, position, rotation)
        self.buildings.append(instance)
        self.serialize()
        return instance

    def create_building(self, type: BuildingType, position: Position, rotation: Rotation) -> BuildingInstance:
        return BuildingInstance(type, position, rotation)

    def remove_building(self, instance: BuildingInstance) -> None:
        self.buildings.remove(instance)
        self.serialize()

    def buildings(self) -> list[BuildingInstance]:
        return list(self.buildings)

    def serialize(self) -> str:
        data = [b.to_dict() for b in self.buildings]
        result = json.dumps(data, indent=2)
        print(result)
        return result

    def deserialize(self, json_str: str, type_lookup: dict):
        data = json.loads(json_str)
        self.buildings = [BuildingInstance.from_dict(d, type_lookup) for d in data]