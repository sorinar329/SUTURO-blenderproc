import blenderproc as bproc
import numpy as np
import suturo_blenderproc.types.table
import suturo_blenderproc.types.wall
import utils.path_utils
import json


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

    def check_if_object_is_in_scene(self, obj):
        found = False
        for item in self.get_objects2annotate():
            if obj in item.get_name().split("."):
                found = True
                break
        return found

    def get_path_to_obj(self, obj):
        blenderproc_path_objects = "/home/charly/dev/blenderproc_suturo/suturo-blenderproc_data/objects/"
        obj_path = blenderproc_path_objects + str(obj) + ".glb"
        return obj_path

    def iterate_through_yaml_obj(self):
        list_of_new_objects = []
        for obj in self.yaml_config.get_objects():
            if self.check_if_object_is_in_scene(obj):
                continue
            else:
                path_to_obj = self.get_path_to_obj(obj)
                new_obj = bproc.loader.load_obj(path_to_obj)
                new_obj[0].move_origin_to_bottom_mean_point()
                new_obj[0].set_name(str(obj))
                list_of_new_objects.append(new_obj[0])
        return list_of_new_objects

    def compute_bbox_properties(self, bbox):
        x_min, y_min, z_min = np.min(bbox, axis=0)
        x_max, y_max, z_max = np.max(bbox, axis=0)
        x_length = x_max - x_min
        y_length = y_max - y_min
        height = z_max

        center_point = np.array([x_min + (x_length / 2), y_min + (y_length / 2), height])

        return x_length, y_length, height, center_point


    def create_id_list_from_json(self, path_to_json):
        with open(path_to_json) as json_file:
            data = json.load(json_file)

        val = list(data.values())
        i = 0
        new_list = []
        for a in val:
            item = a.split(":")

            item_to_list = (item[0]).replace("'", "")
            new_list.append(item_to_list)
        i = i + 1

        return new_list


    def get_id_of_object(self, obj, path_to_json):
        with open(path_to_json) as json_file:
            data = json.load(json_file)

        val = list(data.values())
        i = 0
        for item in val:
            if item.endswith(obj):
                id_of_obj = i
                return id_of_obj
            else:
                i = i + 1


    def assert_id(self, path_to_json, obj_list):
        obj_ids = self.create_id_list_from_json(path_to_json)
        for obj in obj_list:
            print(obj.get_name())
            if "." in obj.get_name():
                if obj.get_name().split(".")[0] in obj_ids:
                    obj_id = self.get_id_of_object(obj.get_name().split(".")[0], path_to_json)
                    obj.set_cp("category_id", obj_id)


            elif obj.get_name() in obj_ids:
                obj_id = self.get_id_of_object(obj.get_name(), path_to_json)
                obj.set_cp("category_id", obj_id)


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
