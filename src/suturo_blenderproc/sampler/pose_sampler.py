from typing import Union

import blenderproc as bproc
import numpy as np

import suturo_blenderproc.types.table
import suturo_blenderproc.types.shelf
import suturo_blenderproc.types.entity
import suturo_blenderproc.types.room

import utils.math_utils
import utils.blenderproc_utils


def extract_surfaces_from_furnitures(furnitures):
    extracted_surfaces = []
    for furniture in furnitures:
        if isinstance(furniture, suturo_blenderproc.types.table.Table):
            extracted_surfaces.append(furniture.table_surface)
        elif isinstance(furniture, suturo_blenderproc.types.shelf.Shelf):
            for shelf_floor in furniture.shelf_floors:
                extracted_surfaces.append(shelf_floor)
        else:
            continue

    return extracted_surfaces


class CameraPoseSampler:
    def __init__(self, room: suturo_blenderproc.types.room.Room):
        self.room = room

    def is_position_out_of_bounds(self, position):
        bbox = self.room.walls.bbox
        return np.any(np.greater(position, np.max(bbox, axis=0))) \
               or np.any(np.less(position, np.min(bbox, axis=0)))

    def build_camera_pose(self, camera_position, poi) -> bool:
        if self.is_position_out_of_bounds(poi):
            raise Exception("Position of Interest is out of bounds, please use a valid poi")

        if not self.is_position_out_of_bounds(camera_position):
            rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - np.array(camera_position))
            cam2world_matrix = bproc.math.build_transformation_mat(camera_position, rotation_matrix)
            bproc.camera.add_camera_pose(cam2world_matrix)
            return True
        print("Camera position is out of bounds")
        return False

    def build_cam_poses_from_config(self, camera_positions: [float], poi: [float]) -> None:
        for camera_position in camera_positions:
            self.build_camera_pose(camera_position, poi)

    def sample_circular_camera_poses_table(self, table_surface: suturo_blenderproc.types.table.TableSurface,
                                           num_poses: int = 1, radius: float = 1.5,
                                           height: float = 1.3) -> None:

        step = 0
        while step != num_poses:
            angle = np.random.randint(360 / 5) * 5
            camera_position = utils.math_utils.position_2D_circle(angle, radius, height, table_surface.center)
            print(f"Camera is currently located at: {camera_position}")
            if self.build_camera_pose(camera_position, bproc.object.compute_poi([table_surface.mesh_object])):
                step += 1

    def sample_circular_camera_poses_shelf(self, shelf_or_shelf_floor: Union[
        suturo_blenderproc.types.shelf.Shelf, suturo_blenderproc.types.shelf.ShelfFloor] = None,
                                           num_poses: int = 1, radius: float = 1.5,
                                           height: float = 1.3) -> None:

        shelf = shelf_or_shelf_floor
        if isinstance(shelf, list) and isinstance(shelf[0], suturo_blenderproc.types.shelf.ShelfFloor):
            shelf = shelf[0].shelf

        step = 0
        while step != num_poses:
            euler_z = shelf.mesh_object.get_rotation_euler()[2]
            if isinstance(shelf.mesh_object.get_parent(), bproc.types.Entity):
                euler_z = shelf.mesh_object.get_parent().get_rotation_euler()[2]
            deg_z = np.rad2deg(euler_z) - 90
            new_angle = np.random.randint(low=deg_z - 30, high=deg_z + 30)
            camera_position = utils.math_utils.position_2D_circle(new_angle, radius, height, shelf.center)
            print(f"Camera is currently located at: {camera_position}")

            if self.build_camera_pose(camera_position, bproc.object.compute_poi([shelf.mesh_object])):
                step += 1

    def sample_circular_camera_poses_list(self, surfaces: [suturo_blenderproc.types.entity.Entity], num_poses: int = 1,
                                          radius: float = 1.5,
                                          height: float = 1.3) -> None:
        for surface in surfaces:
            if isinstance(surface, suturo_blenderproc.types.shelf.Shelf) or isinstance(surface,
                                                                                       suturo_blenderproc.types.shelf.ShelfFloor):
                self.sample_circular_camera_poses_shelf(shelf_or_shelf_floor=surface.shelf, num_poses=num_poses,
                                                        radius=radius, height=height)

            else:
                self.sample_circular_camera_poses_table(table_surface=surface, num_poses=num_poses, radius=radius,
                                                        height=height)


class ObjectPoseSampler:
    def __init__(self, furnitures: [suturo_blenderproc.types.entity.Entity]):
        self.surfaces = extract_surfaces_from_furnitures(furnitures)
        self.current_surface = 0

    def sample_object_pose_uniform(self, obj: bproc.types.MeshObject) -> None:
        surface = self.surfaces[self.current_surface]
        bbox = surface.bbox
        height = surface.height
        lower_corner = np.min(bbox, axis=0)[:2] + 0.15
        upper_corner = np.max(bbox, axis=0)[:2] - 0.15
        lower_bound = np.append(lower_corner, height)
        upper_bound = np.append(upper_corner, height)
        object_pose = np.random.uniform(lower_bound, upper_bound)
        obj.set_location(object_pose)
        utils.blenderproc_utils.set_random_rotation_euler_zaxis(obj)

    def get_len_surfaces(self) -> int:
        return len(self.surfaces)

    def get_current_surface(self) -> suturo_blenderproc.types.entity.Entity:
        return self.surfaces[self.current_surface]

    def next_surface_same_parent(self) -> bool:
        current = self.current_surface
        if current == self.get_len_surfaces() - 1:
            return False
        return self.surfaces[self.current_surface].mesh_object.get_parent() == \
               self.surfaces[self.current_surface + 1].mesh_object.get_parent()

    def next_surface(self) -> None:
        self.current_surface = self.current_surface + 1
        if self.current_surface == self.get_len_surfaces():
            self.current_surface = 0


class LightPoseSampler:
    def __init__(self, room: suturo_blenderproc.types.room.Room):
        self.room = room
        self.lights = []

    def set_light_for_furniture(self, surface: suturo_blenderproc.types.entity.Entity, strength=50) -> None:
        center = surface.center
        height = self.room.walls.height - 0.6
        light = bproc.types.Light()

        if isinstance(surface, suturo_blenderproc.types.table.TableSurface):
            light.set_location(np.append(center[:2], height))
            light.set_energy(strength)

        if isinstance(surface, suturo_blenderproc.types.shelf.ShelfFloor) \
                or isinstance(surface, suturo_blenderproc.types.shelf.Shelf):
            euler_z = surface.mesh_object.get_rotation_euler()[2]
            if isinstance(surface.mesh_object.get_parent(), bproc.types.Entity):
                euler_z = surface.mesh_object.get_parent().get_rotation_euler()[2]
            deg_z = np.rad2deg(euler_z) - 90
            lights_position = utils.math_utils.position_2D_circle(angle=deg_z, radius=0.8, center=center, height=height)

            light.set_location(lights_position)
            light.set_energy(strength)

        self.lights.append(light)

    def delete_lights(self) -> None:
        for light in self.lights:
            light.delete()
