import blenderproc as bproc
import numpy as np

import suturo_blenderproc.types.room
import suturo_blenderproc.types.shelf
import suturo_blenderproc.types.table
import utils.path_utils
import utils.math_utils
import json
import re


class SceneInitializer(object):
    def __init__(self, yaml_config, path_id2name):
        self.yaml_config = yaml_config
        self.path_id2name = None
        self.mesh_objects = None
        self.scene_collection = {}

    def initialize_scene(self):
        bproc.init()
        self.mesh_objects = bproc.loader.load_blend(
            utils.path_utils.get_path_blender_scene(self.yaml_config.get_scene()))
        self.iterate_through_yaml_obj(self.yaml_config.get_path_to_object_source())
        bproc.camera.set_resolution(640, 480)
        self._set_category_id(path_to_json=self.get_path_to_id2name(), obj_list=self.get_objects2annotate())
        self.scene_collection.update({'Room': self._create_room_from_mesh_objects()})
        self.scene_collection.update({'Tables': self._create_table_from_mesh_objects()})
        self.scene_collection.update({'Shelves': self._create_shelves_from_mesh_objects()})

    def get_scene_collection(self):
        return self.scene_collection

    def get_path_to_id2name(self):
        path = self.yaml_config.get_id2name_path()
        return path

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

    def get_path_to_obj(self, obj, path_to_source):
        blenderproc_path_objects = path_to_source
        obj_path = blenderproc_path_objects + str(obj) + ".glb"
        return obj_path

    def iterate_through_yaml_obj(self, path_to_source):
        list_of_new_objects = []
        for obj in self.yaml_config.get_objects():
            if self.check_if_object_is_in_scene(obj):
                continue
            else:
                path_to_obj = self.get_path_to_obj(obj, path_to_source)
                new_obj = bproc.loader.load_obj(path_to_obj)
                new_obj[0].move_origin_to_bottom_mean_point()
                new_obj[0].set_name(str(obj))
                list_of_new_objects.append(new_obj[0])
        self.mesh_objects.extend(list_of_new_objects)

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

            bbox, height, center_point = utils.math_utils.compute_bbox_properties(wall)
            wall_object.height = height
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

    def _process_objects(self, mesh_objects, object_type):
        res = []

        for mesh_object in mesh_objects:
            siblings = [o for o in self.mesh_objects if mesh_object.get_parent() == o.get_parent()]
            bbox, height, center_point = utils.math_utils.compute_bbox_properties(mesh_object)

            if object_type == "Table":
                table = suturo_blenderproc.types.table.Table()
                table_surface = suturo_blenderproc.types.table.TableSurface()
                table_surface.bbox = bbox
                table_surface.height = height
                table_surface.center = center_point
                table_surface.mesh_object = mesh_object
                for sibling in siblings:
                    if "tablelegs" in sibling.get_name().lower():
                        table_legs = suturo_blenderproc.types.table.TableLegs()
                        table_legs.mesh_object = sibling
                        table.table_legs = table_legs
                    if "chair" in sibling.get_name().lower():
                        table_chair = suturo_blenderproc.types.table.TableChairs()
                        table_chair.mesh_object = sibling
                        table.table_chairs = table_chair

                table.table_surface = table_surface
                res.append(table)

            if object_type == "Shelf":
                shelf = suturo_blenderproc.types.shelf.Shelf()
                shelf.bbox = bbox
                shelf.center = center_point
                shelf.height = height
                shelf.mesh_object = mesh_object

                for sibling in siblings:
                    if "shelffloor" in sibling.get_name().lower():
                        bbox, height, center_point = utils.math_utils.compute_bbox_properties(
                            sibling)
                        shelf_floor = suturo_blenderproc.types.shelf.ShelfFloor()
                        shelf_floor.bbox = bbox
                        shelf_floor.shelf = shelf
                        shelf_floor.mesh_object = sibling
                        shelf_floor.center = center_point
                        shelf_floor.height = height
                        shelf.shelf_floors.append(shelf_floor)
                res.append(shelf)
            return res

    def _create_table_from_mesh_objects(self):
        tables = self._get_mesh_objects_by_name("Table")
        tables.extend(self._get_mesh_objects_by_name("TableSurface"))
        return self._process_objects(tables, "Table")

    def _create_shelves_from_mesh_objects(self):
        shelves = self._get_mesh_objects_by_name("Shelf")
        return self._process_objects(shelves, "Shelf")

    def _get_mesh_objects_by_name(self, object_name):
        pattern = re.compile(fr"\b{object_name}\b.*", re.IGNORECASE)
        mesh_objects = bproc.filter.by_attr(self.mesh_objects, "name", pattern, regex=True)
        mesh_objects = [mesh_object for mesh_object in mesh_objects if isinstance(mesh_object, bproc.types.MeshObject)]
        return mesh_objects
