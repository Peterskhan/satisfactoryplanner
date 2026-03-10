from slapp.core.layout import Layout

class Floor():
    index: int
    layout: Layout

    def __init__(self) -> None:
        self.layout = Layout()

    def serialize(self) -> dict:
        return {
            'layout': self.layout.serialize()
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'Floor':
        result = Floor()
        result.layout = Layout.deserialize(data['layout'])
        return result