import blenderproc as bproc

import logging
import sys
import time
from pathlib import Path

p = Path.cwd()
while p.stem != "src":
    p = p.parent

sys.path.append(str(p))
import scenes.argparser
from utils.logger import Logger
import utils.yaml_config
import utils.path_utils
import suturo_blenderproc.scene_init
import suturo_blenderproc.sampler.pose_sampler
import suturo_blenderproc.types.shelf
from suturo_blenderproc.sampler.object_partitions import ObjectPartition, PartitionType, validate_partitions
import os

import blenderproc.python.types.MeshObjectUtility
import numpy as np

args = scenes.argparser.get_argparse()
config = utils.yaml_config.YAMLConfig(filename=args.config_yaml)

def hide_render_objects(blender_objects, render):
    for b_object in blender_objects:
        b_object.blender_obj.hide_render = render


def deploy_scene(x: int, scene_initializer: suturo_blenderproc.scene_init.SceneInitializer, logger: Logger):
    objects = scene_initializer.get_objects2annotate()
    #for obj in objects:
    #    scene_initializer._set_category_id(config.get_id2name_path(), obj)
    scene_collection = scene_initializer.get_scene_collection()
    scene_initializer._set_category_id(config.get_id2name_path(), objects)
    hide_render_objects(scene_initializer.get_all_mesh_objects(), True)
    furnitures = []
    room = scene_collection.get("Room")[0]

    furnitures.extend(room.get_mesh_objects_from_room())
    for table in scene_collection.get("Tables"):
        furnitures.extend(table.get_mesh_objects_from_table())
    for shelf in scene_collection.get("Shelves"):
        furnitures.extend(shelf.get_mesh_objects_from_shelf())

    hide_render_objects(furnitures, False)
    #num_partitions = -(len(objects) // -4)
    num_partitions = 3
    object_partitioner = suturo_blenderproc.sampler.object_partitions.ObjectPartition(num_partitions, objects)

    partitions = object_partitioner.create_partition(
        suturo_blenderproc.sampler.object_partitions.PartitionType.LESS_PROBABLE_OBJECTS,
        probability_reduction_factor=0.5)

    camera_pose_sampler = suturo_blenderproc.sampler.pose_sampler. \
        TableCameraPoseSampler(room=room, tables=scene_collection.get("Tables"))

    camera_pose_sampler2 = suturo_blenderproc.sampler.pose_sampler. \
        ShelfCameraPoseSampler(room=room, shelves=[scene_collection.get("Shelves")[0]])

    light_pose_sampler = suturo_blenderproc.sampler.pose_sampler.LightPoseSampler(room=room)

    object_pose_sampler = suturo_blenderproc.sampler.pose_sampler.ObjectPoseSampler(
        furnitures=scene_collection.get("Tables"))
    logger.log_component(iteration=0, component="Initialize")
    current_partition = 0
    surface = object_pose_sampler.get_current_surface()

    light_strength = np.random.choice([10, 20, 40, 30, 50])
    light_pose_sampler.set_light_for_furniture(surface, light_strength)
    for i in range(x):

        radius = np.random.uniform(1.6, 2.0)
        surfaces = [surface]
        if isinstance(surface, suturo_blenderproc.types.shelf.ShelfFloor):
            while object_pose_sampler.next_surface_same_parent():
                object_pose_sampler.next_surface()
                surface = object_pose_sampler.get_current_surface()
                surfaces.append(surface)
            print(surfaces)
            for surface in surfaces:
                print(surface.mesh_object.get_name())
            camera_pose_sampler2.sample_circular_cam_poses_shelves(shelf_floors=surfaces)
        else:
            camera_pose_sampler.sample_camera_poses_circular_table(table_surfaces=[surface], num_poses=3, radius=radius,
                                                                   height=1.5)
        for surface in surfaces:
            bproc.object.sample_poses_on_surface(partitions[current_partition],
                                                 surface.mesh_object,
                                                 object_pose_sampler.sample_object_pose_uniform,
                                                 max_tries=1000, min_distance=0.08, max_distance=0.5,
                                                 up_direction=np.array([0.0, 0.0, 1.0]),
                                                 check_all_bb_corners_over_surface=True
                                                 )
            validate_partitions(partitions[current_partition])
            hide_render_objects(partitions[current_partition], False)

            current_partition += 1
            if current_partition == num_partitions:
                current_partition = 0
                object_pose_sampler.next_surface()
                surface = object_pose_sampler.get_current_surface()
                break
        logger.log_component(i, "Start rendering")
        data = bproc.renderer.render()
        seg_data = bproc.renderer.render_segmap(map_by=["instance", "class", "name"])
        bproc.writer.write_coco_annotations(
            os.path.join(config.get_output_path(),
                         'coco_data'),
            instance_segmaps=seg_data["instance_segmaps"],
            instance_attribute_maps=seg_data["instance_attribute_maps"],
            colors=data["colors"],
            color_file_format="JPEG", mask_encoding_format="polygon")
        bproc.writer.write_hdf5(config.get_output_path(),
                                data)
        logger.log_component(i, "Finished rendering")
        for partition in partitions[current_partition - len(surfaces): current_partition]:
            hide_render_objects(partition, True)
        blenderproc.utility.reset_keyframes()


def pipeline():

    logger = Logger()
    args = scenes.argparser.get_argparse()
    config = utils.yaml_config.YAMLConfig(filename=args.config_yaml)

    scene_initializer = suturo_blenderproc.scene_init.SceneInitializer(yaml_config=config,
                                                                       path_id2name=config.get_id2name_path())
    scene_initializer.initialize_scene()
    # Sollte intern im scene initializer gemacht werden
    # for item in scene_initializer.iterate_through_yaml_obj():
    #     objects.append(item)

    deploy_scene(11, scene_initializer, logger)


pipeline()
