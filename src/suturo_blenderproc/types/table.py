import numpy as np
import suturo_blenderproc.types.entity


class Table(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()


class RectangularTable(Table):
    def __init__(self):
        super().__init__()
        self.x_size = 0.0
        self.y_size = 0.0
        self.z_size = 0.0


class RoundTable(Table):
    def __init__(self):
        super().__init__()
        self.radius = 0.0


class OvalTable(Table):
    def __init__(self):
        super().__init__()
        self.semi_major_x = 0.0
        self.semi_major_y = 0.0
