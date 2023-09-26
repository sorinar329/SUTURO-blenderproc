import suturo_blenderproc.types.entity
import blenderproc


class ShelfFloor(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.x_size = 0.0
        self.y_size = 0.0
        self.height = 0.0
        self.shelf = suturo_blenderproc.types.shelf.Shelf()

class Shelf(suturo_blenderproc.types.entity.Entity):
    def __init__(self):
        super().__init__()
        self.shelf_floors = []
        self.x_size = 0.0
        self.y_size = 0.0

    def get_mesh_objects_from_shelf(self) -> [blenderproc.types.MeshObject]:
        mesh_objects = [floor.mesh_object for floor in self.shelf_floors]
        mesh_objects.append(self.mesh_object)
        mesh_objects = [o for o in mesh_objects if isinstance(o, blenderproc.types.MeshObject)]
        return mesh_objects

    def add_shelf_floor(self, shelf_floor: ShelfFloor):
        self.shelf_floors.append(shelf_floor)
