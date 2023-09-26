import numpy as np


class Entity:
    def __init__(self):
        self.center = np.zeros(shape=(3, 1))
        self.bbox = np.zeros(shape=(8, 3))
        self.mesh_object = None
