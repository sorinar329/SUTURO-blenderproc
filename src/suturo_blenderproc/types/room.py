import numpy as np
import suturo_blenderproc.types.entity
import blenderproc


class Room(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.walls = Walls()
        self.floor = Floor()
        self.baseboard = Baseboard()

    def get_mesh_objects_from_room(self) -> [blenderproc.types.MeshObject]:
        mesh_objects = [self.walls.mesh_object, self.floor.mesh_object, self.baseboard.mesh_object]
        mesh_objects = [o for o in mesh_objects if o]
        return mesh_objects


class Walls(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.x_length = 0.0
        self.y_length = 0.0
        self.height = 0.0


class Floor(suturo_blenderproc.types.entity.Entity):
    pass


class Baseboard(suturo_blenderproc.types.entity.Entity):
    pass
