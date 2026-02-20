from .DraggableRectItem import DraggableRectItem
from .Settings import Settings
from PySide6.QtGui import QPixmap, QPainterPath

from model.BuldingInstance import BuildingType
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
        if change == BuildingItem.ItemPositionHasChanged:
            self.instance.move_to(value.x() / Settings.PIXELS_PER_METER,
                                  value.y() / Settings.PIXELS_PER_METER)
            
        return super().itemChange(change, value)
    
    def shape(self):
        path = super().shape()
        path = path.toFillPolygon().boundingRect().adjusted(0.1, 0.1, -0.1, -0.1)
        new_path = QPainterPath()
        new_path.addRect(path)
        return new_path

    def is_colliding(self) -> bool:
        return len(self.collidingItems()) > 0