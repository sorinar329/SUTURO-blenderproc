import blenderproc as bproc

import sys
import time
from pathlib import Path

p = Path.cwd()
while p.stem != "src":
    p = p.parent

sys.path.append(str(p))
import scenes.argparser
import utils.yaml_config
import utils.path_utils
import suturo_blenderproc.scene_init
import suturo_blenderproc.sampler.pose_sampler
from suturo_blenderproc.sampler.object_partitions import ObjectPartition, PartitionType
import os

import blenderproc.python.types.MeshObjectUtility
import numpy as np
import utils.path_utils

args = scenes.argparser.get_argparse()
config = utils.yaml_config.YAMLConfig(filename=args.config_yaml)

def hide_render_objects(blender_objects, render):
    for b_object in blender_objects:
        b_object.blender_obj.hide_render = render


def deploy_scene(x, scene_initializer: suturo_blenderproc.scene_init.SceneInitializer):
    objects = scene_initializer.get_objects2annotate()
    new_objects = scene_initializer.iterate_through_yaml_obj(config.get_path_to_object_source())
    for obj in new_objects:
        objects.append(obj)

    #for obj in objects:
    #    scene_initializer._set_category_id(config.get_id2name_path(), obj)
    scene_collection = scene_initializer.get_scene_collection()
    scene_initializer._set_category_id(config.get_id2name_path(), objects)
    hide_render_objects(scene_initializer.get_all_mesh_objects(), True)
    table = scene_collection.get("Tables")[0]
    #table2 = scene_collection.get("Tables")[1]
    room = scene_collection.get("Room")[0]
    shelf = scene_collection.get("Shelves")[0]

    furniture = []
    furniture.extend(room.get_mesh_objects_from_room())
    furniture.extend(table.get_mesh_objects_from_table())
    #furniture.extend(table2.get_mesh_objects_from_table())
    furniture.append(shelf.mesh_object)
    hide_render_objects(furniture, False)

    object_pose_sampler = suturo_blenderproc.sampler.pose_sampler.ObjectPoseSampler(
        surface=table.table_surface)
    object_pose_sampler2 = suturo_blenderproc.sampler.pose_sampler.ObjectPoseSampler(
        surface=shelf.shelf_floors[0])
    object_pose_sampler3 = suturo_blenderproc.sampler.pose_sampler.ObjectPoseSampler(
        surface=shelf.shelf_floors[1])
    # object_pose_sampler4 = suturo_blenderproc.sampler.pose_sampler.ObjectPoseSampler(
    #     surface=table2)

    object_partitioner = suturo_blenderproc.sampler.object_partitions.ObjectPartition(num_partitions=3, objects=objects)
    partitions = object_partitioner.create_partition(
        suturo_blenderproc.sampler.object_partitions.PartitionType.LESS_PROBABLE_OBJECTS,
        probability_reduction_factor=0.5)
    camera_pose_sampler = suturo_blenderproc.sampler.pose_sampler.TableCameraPoseSampler(room=room, table=table)
    #camera_pose_sampler2 = suturo_blenderproc.sampler.pose_sampler.TableCameraPoseSampler(room=room, table=table2)
    camera_pose_sampler3 = suturo_blenderproc.sampler.pose_sampler.ShelfCameraPoseSampler(room=room, shelf=shelf)
    light_pose_sampler = suturo_blenderproc.sampler.pose_sampler.LightPoseSampler(room=room)
    light_pose_sampler.sample_homogenous_lights_around_center(170)

    for partition in partitions:
        hide_render_objects(partition, False)

    for i in range(x):
        blenderproc.object.sample_poses_on_surface(partitions[i % 3], table.table_surface.mesh_object,
                                                   object_pose_sampler.sample_object_pose_uniform,
                                                   max_tries=10000,
                                                   min_distance=0.3, max_distance=0.8,
                                                   up_direction=np.array([0.0, 0.0, 1.0]),
                                                   check_all_bb_corners_over_surface=True)
        blenderproc.object.sample_poses_on_surface(partitions[(i + 1) % 3], shelf.shelf_floors[0].mesh_object,
                                                   object_pose_sampler2.sample_object_pose_uniform,
                                                   max_tries=10000,
                                                   min_distance=0.08, max_distance=0.4, up_direction=None,
                                                   check_all_bb_corners_over_surface=True)
        blenderproc.object.sample_poses_on_surface(partitions[(i + 2) % 3], shelf.shelf_floors[1].mesh_object,
                                                   object_pose_sampler3.sample_object_pose_uniform,
                                                   max_tries=10000,
                                                   min_distance=0.08, max_distance=0.4, up_direction=None,
                                                   check_all_bb_corners_over_surface=True)
        # blenderproc.object.sample_poses_on_surface(partitions[(i + 3) % 4], table2.table_surface.mesh_object,
        #                                            object_pose_sampler4.sample_object_pose_uniform,
        #                                            max_tries=1000, min_distance=0.3, max_distance=0.8,
        #                                            up_direction=np.array([0.0, 0.0, 1.0]),
        #                                            check_all_bb_corners_over_surface=True)
        radius = np.random.uniform(1.6, 2.0)
        camera_pose_sampler.sample_camera_poses_circular_table(num_poses=1, radius=radius,
                                                               poi=table.table_surface.center,
                                                               height=1.4)
        #camera_pose_sampler2.sample_circular_poses(num_poses=1, radius=1.3, poi=table2.table_surface.center, height=1.4)
        camera_pose_sampler3.sample_circular_cam_poses_shelves(1, radius, shelf.center, 1.33,
                                                               np.array([1.88852, -0.400101, 1.13]))

        data = bproc.renderer.render()
        seg_data = bproc.renderer.render_segmap(map_by=["instance", "class", "name"])
        bproc.writer.write_coco_annotations(
            os.path.join("/home/sorin/code/SUTURO-blenderproc/SUTURO-blenderproc/output",
                         'coco_data'),
            instance_segmaps=seg_data["instance_segmaps"],
            instance_attribute_maps=seg_data["instance_attribute_maps"],
            colors=data["colors"],
            color_file_format="JPEG", mask_encoding_format="polygon")
        bproc.writer.write_hdf5("/home/sorin/code/SUTURO-blenderproc/SUTURO-blenderproc/output",
                                data)
        blenderproc.utility.reset_keyframes()


def pipeline():
    start_time = time.time()
    number_of_iterations = config.get_number_of_iterations()
    scene_initializer = suturo_blenderproc.scene_init.SceneInitializer(yaml_config=config,
                                                                       path_id2name=config.get_id2name_path())
    scene_initializer.initialize_scene()
    # Sollte intern im scene initializer gemacht werden
    # for item in scene_initializer.iterate_through_yaml_obj():
    #     objects.append(item)
    deploy_scene(number_of_iterations, scene_initializer)
    # Endezeit erfassen
    end_time = time.time()

    # if yolo = True -> create_yolo_dataset()

    # Gesamtdauer berechnen
    total_duration = end_time - start_time

    # Die Gesamtdauer in Stunden, Minuten und Sekunden umrechnen
    hours = int(total_duration // 3600)
    minutes = int((total_duration % 3600) // 60)
    seconds = int(total_duration % 60)

    # Die Gesamtdauer ausgeben
    print(f"Gesamtdauer: {hours} Stunden, {minutes} Minuten, {seconds} Sekunden")


pipeline()
