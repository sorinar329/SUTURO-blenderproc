import numpy as np


class Table(object):
    def __init__(self):
        self.id = ""
        self.center = np.zeros(shape=(3, 1))
        self.mesh_object = None


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
