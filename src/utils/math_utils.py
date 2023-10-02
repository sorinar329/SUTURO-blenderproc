import blenderproc as bproc
import numpy as np


def position_2D_circle(angle: float, radius: float, height: float, center: np.ndarray):
    if angle < 0:
        angle = 360 + angle
    radian = np.radians(angle)
    x = center[0] + radius * np.cos(radian)
    y = center[1] + radius * np.sin(radian)

    return np.array([x, y, height])


def compute_bbox_properties(mesh_object: bproc.types.MeshObject):
    bbox = mesh_object.get_bound_box()
    height = np.max(bbox, axis=0)[2]
    center_point = np.mean(bbox, axis=0)
    return bbox, height, center_point
