import blenderproc as bproc
import numpy as np
import suturo_blenderproc.types.Table
import utils.path_utils


class SceneInitializer(object):
    def __init__(self, yaml_config):
        self.yaml_config = yaml_config
        self.mesh_objects = None

    def initialize_scene(self):
        bproc.init()
        self.mesh_objects = bproc.loader.load_blend(
            utils.path_utils.get_path_blender_scene(self.yaml_config.get_scene()))
        bproc.camera.set_resolution(640, 480)

    def get_objects2annotate(self):
        object_names = self.yaml_config.get_objects()
        mesh_objects = [m for m in self.mesh_objects if isinstance(m, bproc.types.MeshObject)]
        mesh_objects = [bproc.filter.by_attr(mesh_objects, "name", f"{o}.*", regex=True) for o in object_names]
        return [o for objects in mesh_objects for o in objects]

    def process_table_surface(self, tables, table_type):
        res = []
        for table in tables:
            assert isinstance(table, bproc.types.MeshObject)
            bbox = table.get_bound_box()
            x_min, y_min, z_min = np.min(bbox, axis=0)
            x_max, y_max, z_max = np.max(bbox, axis=0)
            x_length = x_max - x_min
            y_length = y_max - y_min
            z_length = z_max - z_min
            center_point = np.array([x_min + (x_length / 2), y_min + (y_length / 2), z_min + (z_length / 2)])

            if table_type == "round":
                radius = np.linalg.norm(center_point[0] - x_min)
                table_object = suturo_blenderproc.types.Table.RoundTable()
                table_object.radius = radius
            elif table_type == "oval":
                radius_x = np.linalg.norm(center_point[0] - x_min)
                radius_y = np.linalg.norm(center_point[1] - y_min)
                table_object = suturo_blenderproc.types.Table.OvalTable()
                table_object.semi_major_x = radius_x
                table_object.semi_major_y = radius_y
            else:  # Assuming rectangular by default
                table_object = suturo_blenderproc.types.Table.RectangularTable()
                table_object.x_size = x_length
                table_object.y_size = y_length
                table_object.z_size = z_length

            table_object.center = center_point
            table_object.mesh_object = table
            res.append(table_object)

        return res

    def get_table_surfaces_rectangular(self):
        tables = bproc.filter.by_attr(self.mesh_objects, "name", "TableSurface.*", regex=True)
        tables.extend(bproc.filter.by_attr(self.mesh_objects, "name", "[^ ]+TableSurface.*", regex=True))
        return self.process_table_surface(tables, "rectangular")

    def get_table_surfaces_round(self):
        tables = bproc.filter.by_attr(self.mesh_objects, "name", "RoundTableSurface.*", regex=True)
        tables.extend(bproc.filter.by_attr(self.mesh_objects, "name", "[^ ]+RoundTableSurface.*", regex=True))
        return self.process_table_surface(tables, "round")

    def get_table_surfaces_oval(self):
        tables = bproc.filter.by_attr(self.mesh_objects, "name", "OvalTableSurface.*", regex=True)
        tables.extend(bproc.filter.by_attr(self.mesh_objects, "name", "[^ ]+OvalTableSurface.*", regex=True))
        return self.process_table_surface(tables, "oval")

    def sample_object_positions_gaussian(self, obj: bproc.types.MeshObject):
        table = self.get_table_surfaces_round()[0]
        center = table.center
        variance_x = table.radius
        variance_y = table.radius
        cov = [[variance_x, 0], [0, variance_y]]
        mean = center[:2]
        x, y = np.random.multivariate_normal(mean=mean, cov=cov)
        obj.set_location([x, y, center[2]])
