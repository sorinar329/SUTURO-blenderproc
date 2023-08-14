import blenderproc as bproc


class SceneInitializer(object):
    def __init__(self, yaml_config, mesh_objects):
        self.yaml_config = yaml_config
        self.mesh_objects = mesh_objects

    def init_objects(self):
        object_names = self.yaml_config.get_objects()
        mesh_objects = [m for m in self.mesh_objects if isinstance(m, bproc.types.MeshObject)]
        mesh_objects = [bproc.filter.by_attr(mesh_objects, "name", f"{o}.*", regex=True) for o in object_names]
        return [o for objects in mesh_objects for o in objects]

