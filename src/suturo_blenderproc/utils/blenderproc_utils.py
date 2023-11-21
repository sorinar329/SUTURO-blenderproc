import blenderproc as bproc
import numpy as np

import suturo_blenderproc.utils.yaml_config
import suturo_blenderproc.types as types


def hide_mesh_objects(mesh_objects: [bproc.types.MeshObject], render: bool):
    for mesh_object in mesh_objects:
        mesh_object.blender_obj.hide_render = render


# Method to randomize materials of given objects in a scene. The materials are taken from the scene itself,
# as every object can have multiple materials, while only having one active
def randomize_materials(furnitures: [suturo_blenderproc.types.entity.Entity]):
    mesh_objects = []
    # Create a list of all objects, where the material should be swapped.
    for furniture in furnitures:
        if isinstance(furniture, types.table.Table):
            mesh_objects.extend(furniture.get_mesh_objects_from_table())
        elif isinstance(furniture, types.shelf.Shelf):
            mesh_objects.append(furniture.mesh_object)
        elif isinstance(furniture, types.room.Room):
            mesh_objects.extend(furniture.get_mesh_objects_from_room())

    # The material on index 0, is the material that is actively showing on the object. This is randomly set from a
    # list of materials of the given object
    for furniture in mesh_objects:
        furniture.set_material(0, np.random.choice(furniture.get_materials()))



def set_random_rotation_euler_zaxis(mesh_object: bproc.types.MeshObject):
    rotation = np.random.uniform([0, 0, 0], [0, 0, 6])
    mesh_object.set_rotation_euler(mesh_object.get_rotation_euler() + rotation)


def duplicate_objects(object_list: [bproc.types.MeshObject], config: suturo_blenderproc.utils.yaml_config.YAMLConfig):
    num_duplicate = config.get_duplicate_objects()
    duplicated_objects = []

    for obj in object_list:
        duplicated_objects.append(obj)
    if isinstance(num_duplicate, int):
        for obj in object_list:
            for _ in range(num_duplicate - 1):
                duplicated_object = obj.duplicate()
                duplicated_objects.append(duplicated_object)

    if isinstance(num_duplicate, dict):
        for k, v in num_duplicate.items():
            matching_objects = [o for o in duplicated_objects if k in o.get_name()]
            for obj in matching_objects:
                for _ in range(v - 1):
                    duplicated_object = obj.duplicate()
                    duplicated_objects.append(duplicated_object)

    return duplicated_objects
