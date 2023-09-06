import suturo_blenderproc.types.entity


class Shelf(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.shelf_floors = []


class ShelfFloor(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.x_size = 0.0
        self.y_size = 0.0
        self.height = 0.0
