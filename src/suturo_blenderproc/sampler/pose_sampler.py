import blenderproc as bproc
import numpy as np


class CameraPoseSampler(object):
    def __init__(self, walls):
        self.walls = walls

    def is_cam_pose_outofbounds(self, camera_position) -> bool:
        bbox = self.walls.bbox
        x_min, y_min, z_min = np.min(bbox, axis=0)
        x_max, y_max, z_max = np.max(bbox, axis=0)
        bool1 = np.greater(camera_position, np.array([x_max, y_max, z_max]))
        bool2 = np.less(camera_position, np.array([x_min, y_min, z_min]))
        return np.any(bool1) or np.any(bool2)

    def get_cam_poses(self, camera_positions: [float], poi: [float]):
        step = 0
        while step != len(camera_positions):
            camera_position = camera_positions[step]
            if not self.is_cam_pose_outofbounds(camera_position):
                # Sample random camera location above objects
                # Compute rotation based on vector going from location towards poi
                rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - np.array(camera_position),
                                                                         inplane_rot=np.random.uniform(0, 0))
                # Add homog cam pose based on location an rotation
                cam2world_matrix = bproc.math.build_transformation_mat(camera_position, rotation_matrix)
                bproc.camera.add_camera_pose(cam2world_matrix)
                step += 1
            else:
                print("Camera position is out of bounds")
                continue

    def get_sampled_cam_poses(self, num_poses: int, dimensions: np.ndarray, center: np.ndarray, offset: float,
                              poi: [float]):
        step = 0
        while step != num_poses:
            lower_bound = np.append(center[:2] - (dimensions[:2] / 2) - offset, center[2])
            upper_bound = np.append(center[:2] + (dimensions[:2] / 2) + offset, center[2])
            camera_position = np.random.uniform(lower_bound, upper_bound)
            if not self.is_cam_pose_outofbounds(camera_position):
                rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - np.array(camera_position),
                                                                         inplane_rot=np.random.uniform(0, 0))
                cam2world_matrix = bproc.math.build_transformation_mat(camera_position, rotation_matrix)
                bproc.camera.add_camera_pose(cam2world_matrix)
                step += 1
            else:
                print("Camera position is out of bounds")
                continue

    def get_sampled_circular_cam_poses(self, num_poses: int, radius: float, center: np.ndarray, height: float,
                                       offset: float,
                                       poi: [float]):
        for radian in np.linspace(0 + offset, 360 + offset, num_poses):
            x = center[0] + radius * np.sin(radian * np.pi / 180.0)
            y = center[1] + radius * np.cos(radian * np.pi / 180.0)
            camera_position = np.array([x, y, height])
            if not self.is_cam_pose_outofbounds(camera_position):
                rotation_matrix = bproc.camera.rotation_from_forward_vec(
                    poi - camera_position, inplane_rot=np.random.uniform(0, 0))
                cam2world_matrix = bproc.math.build_transformation_mat(np.array([x, y, center[2]]), rotation_matrix)
                bproc.camera.add_camera_pose(cam2world_matrix)
            else:
                print("Camera position is out of bounds")
                continue
