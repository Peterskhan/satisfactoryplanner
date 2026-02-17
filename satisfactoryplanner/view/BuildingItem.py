from .DraggableRectItem import DraggableRectItem
from .Settings import Settings
from PySide6.QtGui import QPixmap

from ..model.building import BuildingType
from ..model.LayoutModel import BuildingInstance

class BuildingItem(DraggableRectItem):
    type: BuildingType

    def __init__(self, instance: BuildingInstance):
        super().__init__(instance.position.x,
                         instance.position.y,
                         Settings.PIXELS_PER_METER * instance.type.width, 
                         Settings.PIXELS_PER_METER * instance.type.length,
                         QPixmap(instance.type.icon))
        self.instance = instance
        self.setRotation(instance.rotation.value * 90)