import numpy as np


class Entity(object):
    def __init__(self):
        self.id = ""
        self.center = np.zeros(shape=(3, 1))
        self.mesh_object = None
