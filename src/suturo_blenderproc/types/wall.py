import numpy as np
import suturo_blenderproc.types.entity


class Wall(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.x_length = 0.0
        self.y_length = 0.0
        self.height = 0.0
        self.bbox = np.zeros(shape=(8, 3))
