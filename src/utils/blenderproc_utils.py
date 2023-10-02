import blenderproc as bproc
import numpy as np

import utils.yaml_config


def hide_mesh_objects(mesh_objects: [bproc.types.MeshObject], render: bool):
    for mesh_object in mesh_objects:
        mesh_object.blender_obj.hide_render = render


def randomize_materials(mesh_objects: [bproc.types.MeshObject]):
    for furniture in mesh_objects:
        print(furniture.get_name())
        furniture.set_material(0, np.random.choice(furniture.get_materials()))
        print(furniture.get_materials()[0].get_name())


def set_random_rotation_euler_zaxis(mesh_object: bproc.types.MeshObject):
    rotation = np.random.uniform([0, 0, 0], [0, 0, 6])
    mesh_object.set_rotation_euler(mesh_object.get_rotation_euler() + rotation)


def duplicate_objects(object_list: [bproc.types.MeshObject], config: utils.yaml_config.YAMLConfig):
    num_duplicate = config.get_duplicate_objects()
    duplicated_objects = []

    if isinstance(num_duplicate, int):
        for o in object_list:
            duplicated_objects.append(o)
            for _ in range(num_duplicate):
                duplicated_object = o.duplicate()
                duplicated_objects.append(duplicated_object)

    if isinstance(num_duplicate, dict):
        num_duplicate = [v for k, v in num_duplicate.items()]

    return duplicated_objects
