import numpy as np
import suturo_blenderproc.types.entity


class Table(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.table_surface = TableSurface()
        self.table_legs = TableLegs()
        self.table_chairs = TableChairs()

    def get_mesh_objects_from_table(self):
        mesh_objects = [self.table_chairs.mesh_object, self.table_legs.mesh_object, self.table_surface.mesh_object]
        return mesh_objects


class TableSurface(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.height = 0.0


class RectangularTableSurface(TableSurface):
    def __init__(self):
        super().__init__()
        self.x_size = 0.0
        self.y_size = 0.0


class RoundTableSurface(TableSurface):
    def __init__(self):
        super().__init__()
        self.radius = 0.0


class OvalTableSurface(TableSurface):
    def __init__(self):
        super().__init__()
        self.semi_major_x = 0.0
        self.semi_major_y = 0.0


class TableLegs(suturo_blenderproc.types.entity.Entity):
    pass


class TableChairs(suturo_blenderproc.types.entity.Entity):
    pass
