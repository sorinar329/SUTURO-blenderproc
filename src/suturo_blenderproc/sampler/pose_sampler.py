import blenderproc as bproc
import numpy as np

import suturo_blenderproc.types.table
import suturo_blenderproc.types.entity


def build_cam_pose(camera_position, poi):
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - np.array(camera_position),
                                                             inplane_rot=np.random.uniform(0, 0))
    # Add homog cam pose based on location an rotation
    cam2world_matrix = bproc.math.build_transformation_mat(camera_position, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)


class CameraPoseSampler(object):
    def __init__(self, walls):
        self.walls = walls

    def is_position_out_of_bounds(self, position) -> bool:
        bbox = self.walls.bbox
        bool1 = np.greater(position, np.max(bbox, axis=0))
        bool2 = np.less(position, np.min(bbox, axis=0))
        return np.any(bool1) or np.any(bool2)

    def build_cam_poses_from_config(self, camera_positions: [float], poi: [float]):

        if self.is_position_out_of_bounds(poi):
            raise Exception("Position of Interest is out of bounds, pls use a valid poi")

        step = 0
        while step != len(camera_positions):
            camera_position = camera_positions[step]
            if not self.is_position_out_of_bounds(camera_position):
                build_cam_pose(camera_position, poi)
                step += 1
            else:
                print("Camera position is out of bounds")
                continue

    def get_sampled_cam_poses(self, num_poses: int, dimensions: np.ndarray, center: np.ndarray, offset: float,
                              poi: [float], height: float):

        if self.is_position_out_of_bounds(poi):
            raise Exception("Position of Interest is out of bounds, pls use a valid poi")

        step = 0
        while step != num_poses:
            lower_bound = np.append(center[:2] - (dimensions[:2] / 2) - offset, height)
            upper_bound = np.append(center[:2] + (dimensions[:2] / 2) + offset, height)
            camera_position = np.random.uniform(lower_bound, upper_bound)
            if not self.is_position_out_of_bounds(camera_position):
                build_cam_pose(camera_position, poi)
                step += 1
            else:
                print("Camera position is out of bounds")
                continue

    def get_sampled_circular_cam_poses(self, num_poses: int, radius: float, center: np.ndarray, height: float,
                                       poi: [float]):
        step = 0
        while step != num_poses:
            radian = np.random.randint(360 / 5) * 5
            x = center[0] + radius * np.sin(radian * np.pi / 180.0)
            y = center[1] + radius * np.cos(radian * np.pi / 180.0)
            camera_position = np.array([x, y, height])
            if not self.is_position_out_of_bounds(camera_position):
                build_cam_pose(camera_position, poi)
                step += 1
            else:
                print("Camera position is out of bounds")
                continue


def set_random_rotation_euler_zaxis(mesh_object: bproc.types.MeshObject):
    rotation = np.random.uniform([0, 0, 0], [0, 0, 6])
    mesh_object.set_rotation_euler(mesh_object.get_rotation_euler() + rotation)


class ObjectPoseSampler(object):
    def __init__(self, surface: suturo_blenderproc.types.entity.Entity):
        self.surface = surface

    def sample_object_pose_gaussian(self, obj: bproc.types.MeshObject):
        surface = self.surface
        center = surface.center
        variance_x = 1
        variance_y = 1
        if isinstance(surface, suturo_blenderproc.types.table.RectangularTable):
            variance_x = surface.x_size * 2 / 3
            variance_y = surface.y_size * 2 / 3
        if isinstance(surface, suturo_blenderproc.types.table.RoundTable):
            variance_x = surface.radius * 2 / 3
            variance_y = surface.radius * 2 / 3
        if isinstance(surface, suturo_blenderproc.types.table.OvalTable):
            variance_x = surface.semi_major_x * 2 / 3
            variance_y = surface.semi_major_y * 2 / 3

        cov = [[variance_x, 0], [0, variance_y]]
        mean = center[:2]
        xy = np.random.multivariate_normal(mean=mean, cov=cov)
        x, y = np.clip(xy, a_min=mean - [variance_x, variance_y], a_max=mean + [variance_x, variance_y])
        obj.set_location([x, y, surface.height])
        set_random_rotation_euler_zaxis(obj)

    def sample_object_pose_uniform(self, obj: bproc.types.MeshObject):
        surface = self.surface
        center = surface.center
        dimensions = None
        if isinstance(surface, suturo_blenderproc.types.table.RectangularTable):
            dimensions = np.array([surface.x_size * 2 / 3, surface.y_size * 2 / 3])
        if isinstance(surface, suturo_blenderproc.types.table.RoundTable):
            dimensions = np.array([surface.radius * 2 / 3, surface.radius * 2 / 3])
        if isinstance(surface, suturo_blenderproc.types.table.OvalTable):
            dimensions = np.array([surface.semi_major_x * 2 / 3, surface.semi_major_y * 2 / 3])

        if dimensions is None:
            raise Exception("Unrecognized surface type")

        lower_bound = np.append(center[:2] - (dimensions / 2), surface.height)
        upper_bound = np.append(center[:2] + (dimensions / 2), surface.height)
        object_pose = np.random.uniform(lower_bound, upper_bound)
        obj.set_location(object_pose)
        set_random_rotation_euler_zaxis(obj)


# Noch nicht benutzen, das ist WIP
class LightPoseSampler(object):
    def __init__(self, walls: suturo_blenderproc.types.wall.Wall):
        self.walls = walls

    def sample_homogenous_lights_around_center(self, strength: float):
        ceiling_height = self.walls.height
        bbox = self.walls.bbox
        center = np.mean(bbox, axis=0)
        center[2] = ceiling_height
        max = np.max(bbox, axis=0)
        matrix = np.array(
            [[max[0] * 3 / 4, 0, 0],
             [-max[0] * 3 / 4, 0, 0],
             [0, max[1] * 3 / 4, 0],
             [0, -max[1] * 3 / 4, 0],
             [0, 0, 0]])

        light_positions = center + matrix
        for position in light_positions:
            light = bproc.types.Light()
            light.set_location(position)
            light.set_energy(strength)
