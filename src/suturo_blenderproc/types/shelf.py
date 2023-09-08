import suturo_blenderproc.types.entity
import numpy as np


class ShelfFloor(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.x_size = 0.0
        self.y_size = 0.0
        self.height = 0.0


class Shelf(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.shelf_floors = []
        self.x_size = 0.0
        self.y_size = 0.0

    def add_shelf_floor(self, shelf_floor: ShelfFloor):
        self.shelf_floors.append(shelf_floor)
