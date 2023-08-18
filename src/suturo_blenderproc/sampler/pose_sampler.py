import blenderproc as bproc
import numpy as np


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

    def get_cam_poses(self, camera_positions: [float], poi: [float]):

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
