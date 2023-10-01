import blenderproc as bproc
import numpy as np


def hide_mesh_objects(mesh_objects: [bproc.types.MeshObject], render: bool):
    for mesh_object in mesh_objects:
        mesh_object.blender_obj.hide_render = render


def randomize_materials(mesh_objects: [bproc.types.MeshObject]):
    for furniture in mesh_objects:
        print(furniture.get_name())
        furniture.set_material(0, np.random.choice(furniture.get_materials()))
        print(furniture.get_materials()[0].get_name())


def build_camera_pose(camera_position, poi):
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - np.array(camera_position))
    cam2world_matrix = bproc.math.build_transformation_mat(camera_position, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)
