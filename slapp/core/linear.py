from PySide6.QtCore import QObject, Signal, QPointF
from dataclasses import dataclass

@dataclass
class LineType:
    name: str
    width: int
    category: str
    icon: str

line_types = {
    'Conveyor belt': LineType('Conveyor belt', 2, 'Logistics', './slapp/resources/ConveyorBelt.png'),
    'Pipeline': LineType('Pipeline', 2, 'Logistics', './slapp/resources/Pipeline.png')
}

class LinearElement(QObject):
    type: LineType
    _nodes: list[QPointF]

    changed = Signal()

    def __init__(self, type: LineType, nodes: list[QPointF] = None) -> None:
        """Initialize a line instance with a type and position."""
        super().__init__()
        self.type = type
        self._nodes = nodes if nodes is not None else []

        # The intermediate node is used during preview to indicate when a
        # turn is necessary for reaching the preview node
        self._intermediate_node = None

        # The preview node is not yet added to the line but indicates the
        # next potential node to be added
        self._preview_node = None

    def clone(self) -> 'LinearElement':
        """Create a copy of this line instance."""
        return LinearElement(self.type, self._nodes.copy())

    def nodes(self) -> list[QPointF]:
        """Get all nodes of the line, including the preview and intermediate nodes."""
        result = self._nodes.copy()
        if self._intermediate_node is not None:
            result.append(self._intermediate_node)
        if self._preview_node is not None:
            result.append(self._preview_node)
        return result

    def add_preview_node(self) -> None:
        """Add a new preview node."""
        self._preview_node = QPointF(0, 0)
        self.changed.emit()

    def discard_preview_node(self) -> None:
        """Discard the preview node."""
        self._preview_node = None
        self.changed.emit()

    def move_preview_node_to(self, node_pos: QPointF) -> None:
        """Move the preview node to the specified position."""

        num_nodes = len(self._nodes)
        match(num_nodes):
            case 0:
                self._preview_node = node_pos
                self._intermediate_node = None
            case 1:
                if (self._nodes[0].x() == node_pos.x() or self._nodes[0].y() == node_pos.y()):
                    self._preview_node = node_pos
                    self._intermediate_node = None
                else:
                    self._intermediate_node = QPointF(node_pos.x(), self._nodes[0].y())
                    self._preview_node = node_pos
            case _:
                # TODO: This is not finished!
                if (self._nodes[-1].x() == node_pos.x() or self._nodes[-1].y() == node_pos.y()):
                    self._preview_node = node_pos
                    self._intermediate_node = None
                else:
                    self._intermediate_node = QPointF(node_pos.x(), self._nodes[-1].y())
                    self._preview_node = node_pos

        self.changed.emit()

    def accept_preview_node(self) -> None:
        """Accept and place the current preview & intermediate nodes."""
        if self._intermediate_node:
            self._nodes.append(self._intermediate_node)
            self._intermediate_node = None
        if self._preview_node:
            self._nodes.append(self._preview_node)
            self._preview_node = None
        self.changed.emit()

    def serialize(self) -> dict:
        return {
            'type': self.type.name,
            'nodes': [{'x': node.x(), 'y': node.y()} for node in self._nodes]
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'LinearElement':
        type_obj = line_types[data['type']]
        return cls(type_obj, [QPointF(node['x'], node['y']) for node in data['nodes']])
