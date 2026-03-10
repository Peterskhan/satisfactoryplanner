from slapp.core.floor import Floor

class Factory():

    floors: list[Floor]

    def __init__(self) -> None:
        self.floors = []
        self.floors.append(Floor())

    def add_floor(self, index: int) -> Floor:
        floor = Floor()
        self.floors.insert(index, floor)
        return floor

    def remove_floor(self, index: int) -> None:
        self.floors.pop(index)

    def serialize(self) -> dict:
        return {
            'floors': [floor.serialize() for floor in self.floors]
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'Factory':
        result = Factory()
        result.floors = [Floor.deserialize(floor_data) for floor_data in data['floors']]
        return result
