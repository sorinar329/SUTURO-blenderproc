import blenderproc as bproc
import numpy as np

import suturo_blenderproc.types.room
import suturo_blenderproc.types.shelf
import suturo_blenderproc.types.table
import utils.path_utils
import json
import re


class SceneInitializer(object):
    def __init__(self, yaml_config, path_id2name):
        self.yaml_config = yaml_config
        self.path_id2name = path_id2name
        self.mesh_objects = None
        self.scene_collection = {}

    def initialize_scene(self):
        bproc.init()
        self.mesh_objects = bproc.loader.load_blend(
            utils.path_utils.get_path_blender_scene(self.yaml_config.get_scene()))
        bproc.camera.set_resolution(640, 480)
        self._set_category_id(path_to_json=self.path_id2name, obj_list=self.get_objects2annotate())
        self.scene_collection.update({'Room': self._create_room_from_mesh_objects()})
        tables = []
        tables.extend(self._create_rectangular_table_from_mesh_objects())
        tables.extend(self._create_round_table_from_mesh_objects())
        tables.extend(self._create_oval_table_from_mesh_objects())
        self.scene_collection.update({'Tables': tables})
        self.scene_collection.update({'Shelves': self._create_shelves_from_mesh_objects()})

    def get_scene_collection(self):
        return self.scene_collection

    def get_objects2annotate(self):
        object_names = self.yaml_config.get_objects()
        objects2annotate = []
        for name in object_names:
            objects2annotate.extend(self._get_mesh_objects_by_name(name))
        return objects2annotate

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

    def _compute_bbox_properties(self, mesh_object: bproc.types.MeshObject):
        bbox = mesh_object.get_bound_box()
        x_min, y_min, z_min = np.min(bbox, axis=0)
        x_max, y_max, z_max = np.max(bbox, axis=0)
        x_length = x_max - x_min
        y_length = y_max - y_min
        height = z_max
        center_point = np.array([x_min + (x_length / 2), y_min + (y_length / 2), z_min + ((height - z_min) / 2)])
        return bbox, x_length, y_length, height, center_point

    def _set_category_id(self, path_to_json, obj_list):
        with open(path_to_json) as json_file:
            data = json.load(json_file)
        data_inverse = {v: k for k, v in data.items()}

        for obj in obj_list:
            obj_id = data_inverse.get(obj.get_name().split(".")[0])
            obj.set_cp("category_id", obj_id)

    def _create_room_from_mesh_objects(self):
        walls = self._get_mesh_objects_by_name("Walls")
        floor = self._get_mesh_objects_by_name("Floor")
        baseboard = self._get_mesh_objects_by_name("Baseboard")

        res = []
        for wall, floor, baseboard in zip(walls, floor, baseboard):
            room = suturo_blenderproc.types.room.Room()

            wall_object = suturo_blenderproc.types.room.Walls()
            wall_object.mesh_object = wall

            bbox, x_length, y_length, z_length, center_point = self._compute_bbox_properties(wall)
            wall_object.x_length = x_length
            wall_object.y_length = y_length
            wall_object.height = z_length
            wall_object.center = center_point

            wall_object.bbox = np.array(bbox)
            floor_object = suturo_blenderproc.types.room.Floor()
            floor_object.mesh_object = floor

            baseboard_object = suturo_blenderproc.types.room.Baseboard()
            baseboard_object.mesh_object = baseboard

            room.walls = wall_object
            room.floor = floor_object
            room.baseboard = baseboard_object
            res.append(room)
        return res

    def _process_table_surface(self, tables, table_type):
        res = []
        for table in tables:
            assert isinstance(table, bproc.types.MeshObject)
            t = suturo_blenderproc.types.table.Table()
            siblings = [o for o in self.mesh_objects if table.get_parent() == o.get_parent()]
            for sibling in siblings:
                if "tablelegs" in sibling.get_name().lower():
                    table_legs = suturo_blenderproc.types.table.TableLegs()
                    table_legs.mesh_object = sibling
                    t.table_legs = table_legs
                if "chair" in sibling.get_name().lower():
                    table_chair = suturo_blenderproc.types.table.TableChairs()
                    table_chair.mesh_object = sibling
                    t.table_chairs = table_chair
            bbox, x_length, y_length, height, center_point = self._compute_bbox_properties(table)

            if table_type == "round":
                radius = np.linalg.norm(center_point[0] - (x_length / 2))
                surface = suturo_blenderproc.types.table.RoundTableSurface()
                surface.radius = radius
                surface.height = height

            elif table_type == "oval":
                radius_x = np.linalg.norm(center_point[0] - (x_length / 2))
                radius_y = np.linalg.norm(center_point[1] - (y_length / 2))
                surface = suturo_blenderproc.types.table.OvalTableSurface()
                surface.semi_major_x = radius_x
                surface.semi_major_y = radius_y
                surface.height = height

            else:  # Assuming rectangular by default
                surface = suturo_blenderproc.types.table.RectangularTableSurface()
                surface.x_size = x_length
                surface.y_size = y_length
                surface.height = height

            surface.center = center_point
            surface.mesh_object = table
            t.table_surface = surface
            res.append(t)

        return res

    def _create_rectangular_table_from_mesh_objects(self):
        tables = self._get_mesh_objects_by_name("RectangularTable")
        tables.extend(self._get_mesh_objects_by_name("RectangularTableSurface"))
        return self._process_table_surface(tables, "rectangular")

    def _create_round_table_from_mesh_objects(self):
        tables = self._get_mesh_objects_by_name("RoundTable")
        tables.extend(self._get_mesh_objects_by_name("RoundTableSurface"))
        return self._process_table_surface(tables, "round")

    def _create_oval_table_from_mesh_objects(self):
        tables = self._get_mesh_objects_by_name("OvalTable")
        tables.extend(self._get_mesh_objects_by_name("OvalTableSurface"))
        return self._process_table_surface(tables, "oval")

    def _create_shelves_from_mesh_objects(self):

        shelves = self._get_mesh_objects_by_name("Shelf")
        shelf_floors = self._get_mesh_objects_by_name("ShelfFloor")

        res = []
        for shelf in shelves:
            bbox, x_length, y_length, height, center_point = self._compute_bbox_properties(shelf)
            # Propertly transform, such that bbox has correct coordinates
            # if shelf.get_parent():
            #     transform_matrix = shelf.get_local2world_mat()
            #     location = transform_matrix[:, 3][0:3]
            #     shelf.set_location(location)
            #     shelf.set_rotation_mat(transform_matrix[:3, :3])

            shelf_object = suturo_blenderproc.types.shelf.Shelf()
            shelf_object.bbox = bbox
            shelf_object.center = shelf.get_location()
            shelf_object.x_size = x_length
            shelf_object.y_size = y_length
            shelf_object.height = height
            shelf_object.mesh_object = shelf

            for floor in shelf_floors:
                if floor.get_parent() != shelf.get_parent():
                    continue

                bbox, x_length, y_length, height, center_point = self._compute_bbox_properties(shelf)
                # transform_matrix = floor.get_local2world_mat()
                # location = transform_matrix[:, 3][0:3]
                # floor.set_location(location)
                # floor.set_rotation_mat(transform_matrix[:3, :3])
                shelf_floor = suturo_blenderproc.types.shelf.ShelfFloor()
                shelf_floor.mesh_object = floor
                shelf_floor.center = floor.get_location()
                shelf_floor.x_size = x_length
                shelf_floor.y_size = y_length
                shelf_floor.height = height
                shelf_object.shelf_floors.append(shelf_floor)
            res.append(shelf_object)
        return res

    def _get_mesh_objects_by_name(self, object_name):
        pattern = re.compile(fr"\b{object_name}\b.*", re.IGNORECASE)
        mesh_objects = bproc.filter.by_attr(self.mesh_objects, "name", pattern, regex=True)
        mesh_objects = [mesh_object for mesh_object in mesh_objects if isinstance(mesh_object, bproc.types.MeshObject)]
        return mesh_objects
