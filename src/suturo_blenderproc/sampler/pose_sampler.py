import blenderproc as bproc
import numpy as np

import suturo_blenderproc.types.table


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
        x_min, y_min, z_min = np.min(bbox, axis=0)
        x_max, y_max, z_max = np.max(bbox, axis=0)
        bool1 = np.greater(position, np.array([x_max, y_max, z_max]))
        bool2 = np.less(position, np.array([x_min, y_min, z_min]))
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
    def __init__(self, surface, ):
        self.surface = surface

    def sample_object_pose_gaussian(self, obj: bproc.types.MeshObject):
        surface = self.surface
        center = surface.center
        variance_x = surface.x_size * 2 / 3
        variance_y = surface.y_size * 2 / 3
        print(variance_x, variance_y)
        cov = [[np.sqrt(variance_x), 0], [0, np.sqrt(variance_y)]]
        mean = center[:2]
        x, y = np.random.multivariate_normal(mean=mean, cov=cov)
        print(f"Sampled x,y location at: {x, y}")
        obj.set_location([x, y, surface.height])
        set_random_rotation_euler_zaxis(obj)

    def sample_object_pose_uniform(self, obj: bproc.types.MeshObject):
        surface = self.surface
        center = surface.center
        dimensions = np.array([surface.x_size * 2 / 3, surface.y_size * 2 / 3])

        lower_bound = np.append(center[:2] - (dimensions / 2), surface.height)
        upper_bound = np.append(center[:2] + (dimensions / 2), surface.height)
        object_pose = np.random.uniform(lower_bound, upper_bound)
        obj.set_location([object_pose])
        set_random_rotation_euler_zaxis(obj)

# Noch nicht benutzen, das ist WIP
class LightPoseSampler(object):
    def __init__(self, surface: suturo_blenderproc.types.table.Table, walls: suturo_blenderproc.types.wall.Wall):
        self.surface = surface
        self.walls = walls

    def sample__homogenous_lights(self, strength, num_lights, offset):
        ceiling_height = self.walls.height
        surface_center = self.surface.center[:2].append(ceiling_height)
        light = bproc.types.Light()
        light.set_location(surface_center)
        light.set_energy(strength)
