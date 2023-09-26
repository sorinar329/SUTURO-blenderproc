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
    def __init__(self, room: suturo_blenderproc.types.room.Room, tables: [suturo_blenderproc.types.table.Table]):
        super().__init__(room=room)
        extracted_table_surfaces = []
        for table in tables:
            assert isinstance(table, suturo_blenderproc.types.table.Table)
            extracted_table_surfaces.append(table.table_surface)
        self.table_surfaces = extracted_table_surfaces

    def sample_camera_poses_circular_table(self, table_surfaces: [suturo_blenderproc.types.table.TableSurface] = [],
                                           num_poses: int = 1, radius: float = 1.5,
                                           height: float = 1.3) -> None:
        sample_camera_poses_surfaces = self.table_surfaces
        if len(table_surfaces) > 0:
            sample_camera_poses_surfaces = table_surfaces

        for table_surface in sample_camera_poses_surfaces:
            self.sample_circular_poses(num_poses=num_poses, radius=radius, center=table_surface.center, height=height,
                                       poi=bproc.object.compute_poi([table_surface.mesh_object]))

    def sample_camera_poses_table(self, num_poses: int, offset: float,
                                  height: float) -> None:
        for table_surface in self.table_surfaces:

            if isinstance(table_surface, suturo_blenderproc.types.table.RectangularTableSurface):
                dimensions = np.array([table_surface.x_size, table_surface.y_size])
            elif isinstance(table_surface, suturo_blenderproc.types.table.RoundTableSurface):
                dimensions = np.array([table_surface.radius, table_surface.radius])
            else:
                dimensions = np.array([table_surface.semi_major_x, table_surface.semi_major_y])

            self.sample_camera_poses(num_poses=num_poses, dimensions=dimensions, center=table_surface.center,
                                     offset=offset,
                                     height=height, poi=bproc.object.compute_poi([table_surface.mesh_object]))


class ShelfCameraPoseSampler(CameraPoseSampler):
    def __init__(self, room: suturo_blenderproc.types.room.Room, shelves: [suturo_blenderproc.types.shelf.Shelf]):
        super().__init__(room=room)
        self.shelves = shelves

    def sample_circular_cam_poses_shelves(self, num_poses: int, radius: float, height: float) -> None:
        for shelf in self.shelves:
            step = 0
            center = shelf.center
            while step != num_poses:
                assert isinstance(shelf.mesh_object, bproc.types.MeshObject)
                euler_z = shelf.mesh_object.get_rotation_euler()[2]
                if isinstance(shelf.mesh_object.get_parent(), bproc.types.Entity):
                    euler_z = shelf.mesh_object.get_parent().get_rotation_euler()[2]
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
                    for shelf_floors in shelf.shelf_floors:
                        poi = bproc.object.compute_poi([shelf_floors.mesh_object])
                        self.build_camera_pose(camera_position, poi)
                    step += 1
                else:
                    print("Camera position is out of bounds")


class ObjectPoseSampler:
    def __init__(self, furnitures: [suturo_blenderproc.types.entity.Entity]):
        extracted_surfaces = []
        for furniture in furnitures:
            if isinstance(furniture, suturo_blenderproc.types.table.Table):
                extracted_surfaces.append(furniture.table_surface)
            elif isinstance(furniture, suturo_blenderproc.types.shelf.Shelf):
                for shelf_floor in furniture.shelf_floors:
                    extracted_surfaces.append(shelf_floor)
            else:
                continue

        self.surfaces = extracted_surfaces
        self.current_surface = 0

    def set_random_rotation_euler_zaxis(self, mesh_object: bproc.types.MeshObject):
        rotation = np.random.uniform([0, 0, 0], [0, 0, 360])
        rotation = np.radians(rotation)
        mesh_object.set_rotation_euler(mesh_object.get_rotation_euler() + rotation)

    def sample_object_pose_uniform(self, obj: bproc.types.MeshObject) -> None:
        surface = self.surfaces[self.current_surface]
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
        else:
            raise Exception("Pls set a proper surface or a shelf floor")

        lower_bound = np.append(center[:2] - (dimensions / 2), height)
        upper_bound = np.append(center[:2] + (dimensions / 2), height)
        object_pose = np.random.uniform(lower_bound, upper_bound)
        obj.set_location(object_pose)
        self.set_random_rotation_euler_zaxis(obj)

    def get_len_surfaces(self) -> int:
        return len(self.surfaces)

    def get_current_surface(self) -> suturo_blenderproc.types.entity.Entity:
        return self.surfaces[self.current_surface]

    def next_surface_same_parent(self) -> bool:
        return self.surfaces[self.current_surface].mesh_object.get_parent() == \
               self.surfaces[(self.current_surface + 1) % self.get_len_surfaces()].mesh_object.get_parent()

    def next_surface(self) -> None:
        self.current_surface = (self.current_surface + 1) % self.get_len_surfaces()
        print(self.current_surface)


class LightPoseSampler:
    def __init__(self, room: suturo_blenderproc.types.room.Room):
        self.room = room

    def set_light_for_furniture(self, surface: suturo_blenderproc.types.entity.Entity, strength=50):
        center = surface.center
        center[2] = self.room.walls.height - 0.7
        if isinstance(surface, suturo_blenderproc.types.table.TableSurface):
            light = bproc.types.Light()
            light.set_location(center)
            light.set_energy(strength)
            print(f"Set light at location: {center} with strength: {strength}")
        if isinstance(surface, suturo_blenderproc.types.shelf.ShelfFloor):
            euler_z = surface.mesh_object.get_rotation_euler()[2]
            if isinstance(surface.mesh_object.get_parent(), bproc.types.Entity):
                euler_z = surface.mesh_object.get_parent().get_rotation_euler()[2]
            deg_z = np.rad2deg(euler_z) - 90
            if deg_z < 0:
                deg_z = 360 + deg_z
            radian = np.radians(deg_z)
            x = center[0] + 0.6 * np.cos(radian)
            y = center[1] + 0.6 * np.sin(radian)
            light = bproc.types.Light()
            light.set_location([x, y, center[2]])
            light.set_energy(strength)
