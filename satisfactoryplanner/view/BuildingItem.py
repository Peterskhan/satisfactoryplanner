from .DraggableRectItem import DraggableRectItem
from .Settings import Settings
from PySide6.QtGui import QPixmap

from model.building import BuildingType
from model.FactoryLayout import BuildingInstance

class BuildingItem(DraggableRectItem):
    type: BuildingType

    def __init__(self, instance: BuildingInstance):
        super().__init__(Settings.PIXELS_PER_METER * instance.position.x,
                         Settings.PIXELS_PER_METER * instance.position.y,
                         Settings.PIXELS_PER_METER * instance.type.width, 
                         Settings.PIXELS_PER_METER * instance.type.length,
                         QPixmap(instance.type.icon))
        self.instance = instance
        self.update()

    def update(self):
        """Update the visual representation of the building based on its instance data."""
        self.setPos(Settings.PIXELS_PER_METER * self.instance.position.x,
                    Settings.PIXELS_PER_METER * self.instance.position.y)
        self.setRotation(self.instance.rotation.value * 90)

    def itemChange(self, change, value):
        if change == BuildingItem.ItemPositionChange:
            self.instance.move_to(round(value.x() / Settings.PIXELS_PER_METER), 
                                  round(value.y() / Settings.PIXELS_PER_METER))

        return super().itemChange(change, value)