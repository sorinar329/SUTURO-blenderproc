import symtable

import blenderproc as bproc
import numpy as np

import suturo_blenderproc.types.table
import suturo_blenderproc.types.shelf
import suturo_blenderproc.types.entity
import suturo_blenderproc.types.room


class CameraPoseSampler:
    def __init__(self, room: suturo_blenderproc.types.room.Room):
        self.room = room

    def is_position_out_of_bounds(self, position):
        bbox = self.room.walls.bbox
        return np.any(np.greater(position, np.max(bbox, axis=0))) \
               or np.any(np.less(position, np.min(bbox, axis=0)))

    def build_camera_pose(self, camera_position, poi):
        rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - np.array(camera_position))
        cam2world_matrix = bproc.math.build_transformation_mat(camera_position, rotation_matrix)
        bproc.camera.add_camera_pose(cam2world_matrix)

    def build_cam_poses_from_config(self, camera_positions: [float], poi: [float]) -> None:

        if self.is_position_out_of_bounds(poi):
            raise Exception("Position of Interest is out of bounds, please use a valid poi")

        for camera_position in camera_positions:
            if not self.is_position_out_of_bounds(camera_position):
                self.build_camera_pose(camera_position, poi)
            else:
                print("Camera position is out of bounds")

    def sample_camera_poses(self, num_poses: int, dimensions: np.ndarray, center: np.ndarray, offset: float,
                            height: float, poi: [float]) -> None:

        if self.is_position_out_of_bounds(poi):
            raise Exception("Position of Interest is out of bounds, please use a valid poi")

        step = 0
        while step != num_poses:
            lower_bound = np.append(center[:2] - (dimensions[:2] / 2) - offset, height)
            upper_bound = np.append(center[:2] + (dimensions[:2] / 2) + offset, height)
            camera_position = np.random.uniform(lower_bound, upper_bound)
            if not self.is_position_out_of_bounds(camera_position):
                self.build_camera_pose(camera_position, poi)
                step += 1
            else:
                print("Camera position is out of bounds")

    def sample_circular_poses(self, num_poses: int, radius: float, center: np.ndarray, height: float,
                              poi: [float]):

        if self.is_position_out_of_bounds(poi):
            raise Exception("Position of Interest is out of bounds, please use a valid poi")

        step = 0
        while step != num_poses:
            radian = np.radians(np.random.randint(360 / 5) * 5)
            x = center[0] + radius * np.cos(radian)
            y = center[1] + radius * np.sin(radian)
            camera_position = np.array([x, y, height])
            if not self.is_position_out_of_bounds(camera_position):
                self.build_camera_pose(camera_position, poi)
                step += 1
            else:
                print("Camera position is out of bounds")


class TableCameraPoseSampler(CameraPoseSampler):
    def __init__(self, room: suturo_blenderproc.types.room.Room, table=suturo_blenderproc.types.table.Table):
        super().__init__(room=room)
        self.table = table
        self.table_center = self.table.table_surface.center

    def sample_camera_poses_circular_table(self, num_poses: int, radius: float, height: float,
                                           poi: [float]) -> None:

        self.sample_circular_poses(num_poses=num_poses, radius=radius, center=self.table_center, height=height, poi=poi)

    def sample_camera_poses_table(self, num_poses: int, offset: float,
                                  height: float, poi: [float]) -> None:

        table_surface = self.table.table_surface
        if isinstance(table_surface, suturo_blenderproc.types.table.RectangularTableSurface):
            dimensions = np.array([table_surface.x_size, table_surface.y_size])
        elif isinstance(table_surface, suturo_blenderproc.types.table.RoundTableSurface):
            dimensions = np.array([table_surface.radius, table_surface.radius])
        else:
            dimensions = np.array([table_surface.semi_major_x, table_surface.semi_major_y])

        self.sample_camera_poses(num_poses=num_poses, dimensions=dimensions, center=self.table_center, offset=offset,
                                 height=height, poi=poi)


class ShelfCameraPoseSampler(CameraPoseSampler):
    def __init__(self, room: suturo_blenderproc.types.room.Room, shelf: suturo_blenderproc.types.shelf.Shelf):
        super().__init__(room=room)
        self.shelf = shelf

    def sample_circular_cam_poses_shelves(self, num_poses: int, radius: float, center: np.ndarray,
                                          height: float,
                                          poi: [float]) -> None:
        step = 0
        while step != num_poses:
            assert isinstance(self.shelf.mesh_object, bproc.types.MeshObject)

            euler_z = self.shelf.mesh_object.get_rotation_euler()[2]
            deg_z = np.rad2deg(euler_z) - 90
            new_angle = np.random.randint(low=deg_z - 30, high=deg_z + 30)

            if new_angle < 0:
                new_angle = 360 + new_angle
            radian = np.radians(new_angle)

            x = center[0] + radius * np.cos(radian)
            y = center[1] + radius * np.sin(radian)
            print(f"camera position is at x,y: {x, y}")
            camera_position = np.array([x, y, height])
            if not self.is_position_out_of_bounds(camera_position):
                self.build_camera_pose(camera_position, poi)
                step += 1
            else:
                print("Camera position is out of bounds")


class ObjectPoseSampler:
    def __init__(self, surface):
        self.surface = surface

    def set_random_rotation_euler_zaxis(self, mesh_object: bproc.types.MeshObject):
        rotation = np.random.uniform([0, 0, 0], [0, 0, 360])
        rotation = np.radians(rotation)
        mesh_object.set_rotation_euler(mesh_object.get_rotation_euler() + rotation)

    def sample_object_pose_uniform(self, obj: bproc.types.MeshObject) -> None:
        print(self.surface.mesh_object.get_name())
        surface = self.surface
        center = surface.center
        height = surface.height
        if isinstance(surface, suturo_blenderproc.types.table.RectangularTableSurface):
            dimensions = np.array([surface.x_size * 2 / 3, surface.y_size * 2 / 3])
        elif isinstance(surface, suturo_blenderproc.types.table.RoundTableSurface):
            dimensions = np.array([surface.radius * 2 / 3, surface.radius * 2 / 3])
        elif isinstance(surface, suturo_blenderproc.types.table.OvalTableSurface):
            dimensions = np.array([surface.semi_major_x * 2 / 3, surface.semi_major_y * 2 / 3])
        elif isinstance(surface, suturo_blenderproc.types.shelf.ShelfFloor):
            dimensions = np.array([surface.x_size * 1 / 2, surface.y_size * 1 / 2])
        elif isinstance(surface, suturo_blenderproc.types.shelf.Shelf):
            dimensions = np.array([surface.x_size * 1 / 2, surface.y_size * 1 / 2])
            height = 1.42838
        else:
            raise Exception("Pls set a proper surface or a shelf floor")

        lower_bound = np.append(center[:2] - (dimensions / 2), height)
        upper_bound = np.append(center[:2] + (dimensions / 2), height)
        object_pose = np.random.uniform(lower_bound, upper_bound)
        obj.set_location(object_pose)
        self.set_random_rotation_euler_zaxis(obj)


class LightPoseSampler:
    def __init__(self, room: suturo_blenderproc.types.room):
        self.room = room

    def sample_homogenous_lights_around_center(self, strength: float) -> None:
        ceiling_height = self.room.walls.height

        bbox = self.room.walls.bbox
        center = np.mean(bbox, axis=0)
        center[2] = ceiling_height

        matrix = np.array([
            [3 / 4, 0, 0],
            [-3 / 4, 0, 0],
            [0, 3 / 4, 0],
            [0, -3 / 4, 0],
            [0, 0, 0]
        ]) * np.max(bbox, axis=0)

        light_positions = center + matrix
        for position in light_positions:
            light = bproc.types.Light()
            light.set_location(position)
            light.set_energy(strength)
