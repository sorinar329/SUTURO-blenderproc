import numpy as np


class Entity:
    center = np.zeros(shape=(3, 1))
    bbox = np.zeros(shape=(8, 3))
    mesh_object = None

    def __init__(self):
        self.id = ""
