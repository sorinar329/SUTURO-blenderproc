import blenderproc as bproc
import numpy as np
import suturo_blenderproc.types.table
import suturo_blenderproc.types.wall
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

    def get_all_mesh_objects(self):
        return self.mesh_objects

    def compute_bbox_properties(self, bbox):
        x_min, y_min, z_min = np.min(bbox, axis=0)
        x_max, y_max, z_max = np.max(bbox, axis=0)
        x_length = x_max - x_min
        y_length = y_max - y_min
        height = z_max
        center_point = np.array([x_min + (x_length / 2), y_min + (y_length / 2), height])
        return x_length, y_length, height, center_point

    def get_walls(self):
        walls = bproc.filter.by_attr(self.mesh_objects, "name", "[^ ]+Room.*", regex=True)
        res = []
        for wall in walls:
            wall_object = suturo_blenderproc.types.wall.Wall()
            wall_object.mesh_object = wall
            bbox = wall.get_bound_box()
            x_length, y_length, z_length, center_point = self.compute_bbox_properties(bbox)

            wall_object.x_length = x_length
            wall_object.y_length = y_length
            wall_object.height = z_length
            wall_object.center = center_point

            wall_object.bbox = np.array(bbox)
            res.append(wall_object)
        return res

    def process_table_surface(self, tables, table_type):
        res = []
        for table in tables:
            assert isinstance(table, bproc.types.MeshObject)
            bbox = table.get_bound_box()
            x_length, y_length, height, center_point = self.compute_bbox_properties(bbox)

            if table_type == "round":
                radius = np.linalg.norm(center_point[0] - (x_length / 2))
                table_object = suturo_blenderproc.types.table.RoundTable()
                table_object.radius = radius
                table_object.height = height

            elif table_type == "oval":
                radius_x = np.linalg.norm(center_point[0] - (x_length / 2))
                radius_y = np.linalg.norm(center_point[1] - (y_length / 2))
                table_object = suturo_blenderproc.types.table.OvalTable()
                table_object.semi_major_x = radius_x
                table_object.semi_major_y = radius_y
                table_object.height = height

            else:  # Assuming rectangular by default
                table_object = suturo_blenderproc.types.table.RectangularTable()
                table_object.x_size = x_length
                table_object.y_size = y_length
                table_object.height = height

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
