import blenderproc as bproc
import suturo_blenderproc.types as types
import suturo_blenderproc.utils as utils
import suturo_blenderproc.utils.math_utils
import json
import re


class SceneInitializer(object):
    def __init__(self, yaml_config):
        self.yaml_config = yaml_config
        self.path_id2name = self.yaml_config.get_id2name_path()
        self.mesh_objects = None
        self.scene_collection = {}

    def initialize_scene(self):
        bproc.init()
        self.mesh_objects = bproc.loader.load_blend(
            utils.path_utils.get_path_blender_scene(self.yaml_config.get_scene()))
        self.iterate_through_yaml_obj(self.yaml_config.get_path_to_object_source())
        bproc.camera.set_resolution(640, 480)
        self._set_category_id(path_to_json=self.path_id2name, obj_list=self.get_objects2annotate())
        self.scene_collection.update({'Room': self._create_room_from_mesh_objects()})
        self.scene_collection.update({'Tables': self._create_table_from_mesh_objects()})
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

    def get_all_mesh_objects_id2name(self):
        objects_id2name = []
        with open(self.yaml_config.get_id2name_path()) as json_file:
            data = json.load(json_file)
            names = data.values()
            for name in names:
                objects_id2name.extend(self._get_mesh_objects_by_name(name))

        return objects_id2name

    def check_if_object_is_in_scene(self, obj):
        found = False
        for item in self.get_objects2annotate():
            if obj in item.get_name().split("."):
                found = True
                break
        return found

    # Method that returns the path to an object which is not in the scene, but can be found in the objects folder.
    def get_path_to_obj(self, obj, path_to_source):
        blenderproc_path_objects = path_to_source
        obj_path = blenderproc_path_objects + str(obj) + ".glb"
        return obj_path

    # Method to actually import objects that are not already in the scene,
    # by checking if there are objects in the object list, which contains the objects that should
    # be included and annotated and are not in the scene. These objects should then be located in the objects folder
    def iterate_through_yaml_obj(self, path_to_source):
        list_of_new_objects = []
        for obj in self.yaml_config.get_objects():
            # Check if the object is already in the scene
            if self.check_if_object_is_in_scene(obj):
                continue
            else:
                # If the object is not in the scene, the object will be imported into the scene from the objects'
                # folder.
                path_to_obj = self.get_path_to_obj(obj, path_to_source)
                new_obj = bproc.loader.load_obj(path_to_obj)
                # The origin of the object will be moved to the bottom, that makes it simpler to place the object on
                # surfaces.
                new_obj[0].move_origin_to_bottom_mean_point()
                # The name of the new object will be set, that is important for the annotations.
                new_obj[0].set_name(str(obj))
                list_of_new_objects.append(new_obj[0])
        self.mesh_objects.extend(list_of_new_objects)

    # Set the category id of objects according to the given id from the id2namejson.
    def _set_category_id(self, path_to_json, obj_list):
        with open(path_to_json) as json_file:
            data = json.load(json_file)
        data_inverse = {v: k for k, v in data.items()}

        for obj in obj_list:
            obj_id = data_inverse.get(obj.get_name().split(".")[0])
            obj.set_cp("category_id", obj_id)

    def _create_room_from_mesh_objects(self):
        walls = self._get_mesh_objects_by_name("Walls")
        floors = self._get_mesh_objects_by_name("Floor")
        res = []
        for wall in walls:
            room = types.room.Room()

            wall_object = types.room.Walls()
            wall_object.mesh_object = wall

            bbox, height, center_point = utils.math_utils.compute_bbox_properties(wall)
            wall_object.bbox = bbox
            wall_object.height = height
            wall_object.center = center_point

            room.walls = wall_object
            res.append(room)
        for floor in floors:
            room = types.room.Room()

            floor_object = types.room.Floor
            floor_object.mesh_object = floor

            room.floor = floor_object
            res.append(room)
        return res

    def _process_objects(self, mesh_objects, object_type):
        res = []

        for mesh_object in mesh_objects:
            siblings = [o for o in self.mesh_objects if mesh_object.get_parent() == o.get_parent()]
            bbox, height, center_point = utils.math_utils.compute_bbox_properties(mesh_object)

            if object_type == "Table":
                table = types.table.Table()
                table_surface = types.table.TableSurface()
                table_surface.bbox = bbox
                table_surface.height = height
                table_surface.center = center_point
                table_surface.mesh_object = mesh_object
                for sibling in siblings:
                    if "tablelegs" in sibling.get_name().lower():
                        table_legs = types.table.TableLegs()
                        table_legs.mesh_object = sibling
                        table.table_legs = table_legs
                    if "chair" in sibling.get_name().lower():
                        table_chair = types.table.TableChairs()
                        table_chair.mesh_object = sibling
                        table.table_chairs = table_chair

                table.table_surface = table_surface
                res.append(table)

            if object_type == "Shelf":
                shelf = types.shelf.Shelf()
                shelf.bbox = bbox
                shelf.center = center_point
                shelf.height = height
                shelf.mesh_object = mesh_object

                for sibling in siblings:
                    if "shelffloor" in sibling.get_name().lower():
                        bbox, height, center_point = utils.math_utils.compute_bbox_properties(
                            sibling)
                        shelf_floor = types.shelf.ShelfFloor()
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
