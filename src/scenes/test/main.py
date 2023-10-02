import blenderproc as bproc
import random
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
from scripts.annotations.convert_to_yolo import create_yolo_dataset
from utils.blenderproc_utils import hide_mesh_objects
import blenderproc.python.types.MeshObjectUtility
import numpy as np

# import scripts.model.yolov8 as yolo

args = scenes.argparser.get_argparse()
config = utils.yaml_config.YAMLConfig(filename=args.config_yaml)


def deploy_scene(x: int, scene_initializer: suturo_blenderproc.scene_init.SceneInitializer, logger: Logger):
    hide_mesh_objects(scene_initializer.get_all_mesh_objects(), True)
    objects = scene_initializer.get_objects2annotate()
    objects = utils.blenderproc_utils.duplicate_objects(objects, config)
    hide_mesh_objects(objects, True)
    scene_collection = scene_initializer.get_scene_collection()
    furnitures = []
    room = scene_collection.get("Room")[0]

    furnitures.extend(room.get_mesh_objects_from_room())
    for table in scene_collection.get("Tables"):
        furnitures.extend(table.get_mesh_objects_from_table())
    for shelf in scene_collection.get("Shelves"):
        furnitures.extend(shelf.get_mesh_objects_from_shelf())

    hide_mesh_objects(furnitures, False)
    num_partitions = -(len(objects) // -4)
    object_partitioner = suturo_blenderproc.sampler.object_partitions.ObjectPartition(num_partitions, objects)

    partitions = object_partitioner.create_partition(
        suturo_blenderproc.sampler.object_partitions.PartitionType.LESS_PROBABLE_OBJECTS,
        probability_reduction_factor=0.5)
    camera_pose_sampler = suturo_blenderproc.sampler.pose_sampler.CameraPoseSampler(room=room)

    light_pose_sampler = suturo_blenderproc.sampler.pose_sampler.LightPoseSampler(room=room)

    object_pose_sampler = suturo_blenderproc.sampler.pose_sampler.ObjectPoseSampler(
        furnitures=scene_collection.get("Tables") + scene_collection.get("Shelves"))
    logger.log_component(iteration=0, component="Initialize")
    current_partition = 0
    surface = object_pose_sampler.get_current_surface()
    surfaces = [surface]
    partition_indices = []

    for i in range(x):
        utils.blenderproc_utils.randomize_materials(furnitures)
        lights_strength = np.random.choice([10, 30, 40, 50, 100])
        radius = np.random.choice(np.linspace(start=1.6, stop=2.2, num=20))
        height = np.random.choice(np.linspace(start=1.4, stop=1.8, num=8))
        if isinstance(surface, suturo_blenderproc.types.shelf.ShelfFloor):
            while object_pose_sampler.next_surface_same_parent():
                object_pose_sampler.next_surface()
                surfaces.append(object_pose_sampler.get_current_surface())
        light = light_pose_sampler.sample_light_for_furniture(surface, lights_strength)
        camera_pose_sampler.sample_circular_camera_poses_list(surfaces=[surface],
                                                              num_poses=3,
                                                              radius=radius,
                                                              height=height)
        for s in surfaces:
            bproc.object.sample_poses_on_surface(partitions[current_partition],
                                                 s.mesh_object,
                                                 object_pose_sampler.sample_object_pose_uniform,
                                                 max_tries=1000, min_distance=0.08, max_distance=0.4,
                                                 up_direction=np.array([0.0, 0.0, 1.0]),
                                                 check_all_bb_corners_over_surface=True
                                                 )
            validate_partitions(partitions[current_partition])
            hide_mesh_objects(partitions[current_partition], False)
            partition_indices.append(current_partition)
            current_partition += 1
            if current_partition == num_partitions:
                current_partition = 0
                object_pose_sampler.next_surface()
                surface = object_pose_sampler.get_current_surface()
                surfaces = [surface]
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
            color_file_format="JPEG",
            append_to_existing_output=True)

        logger.log_component(i, "Finished rendering")
        for index in partition_indices:
            hide_mesh_objects(partitions[index], True)
        light.delete()
        partition_indices = []
        blenderproc.utility.reset_keyframes()


def pipeline():
    logger = Logger()
    args = scenes.argparser.get_argparse()
    config = utils.yaml_config.YAMLConfig(filename=args.config_yaml)

    scene_initializer = suturo_blenderproc.scene_init.SceneInitializer(yaml_config=config,
                                                                       path_id2name=config.get_id2name_path())

    scene_initializer.initialize_scene()
    deploy_scene(50, scene_initializer, logger)

    if config.get_yolo_training():
        create_yolo_dataset(config.get_id2name_path(), config.get_output_path() + "/coco_data/coco_annotations.json",
                            config.get_output_path() + "/coco_data/images/", config.get_yolo_save_path())


pipeline()
