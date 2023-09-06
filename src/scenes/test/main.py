import blenderproc as bproc

import sys
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


def init_objects(object_names: [], mesh_objects: []):
    mesh_objects = [m for m in mesh_objects if isinstance(m, blenderproc.types.MeshObject)]
    return [bproc.filter.by_attr(mesh_objects, "name", f"{o}.*", regex=True) for o in object_names]


def hide_object(mesh_objects: [blenderproc.types.MeshObject]):
    print(type(mesh_objects))
    for mesh_object in mesh_objects:
        if isinstance(mesh_object, list):
            for o in mesh_object:
                print(o.get_name())
                o.blender_obj.hide_render = True
        else:
            print(mesh_object.get_name())
            mesh_object.blender_obj.hide_render = True


def hide_render_objects(blender_objects, render):
    for b_object in blender_objects:
        b_object.blender_obj.hide_render = render


def set_homogeneous_lighting(locations, strength: float):
    for location in locations:
        light = bproc.types.Light()
        light.set_location(location)
        light.set_energy(strength)


args = scenes.argparser.get_argparse()
config = utils.yaml_config.YAMLConfig(filename=args.config_yaml)
scene_initializer = suturo_blenderproc.scene_init.SceneInitializer(yaml_config=config)
scene_initializer.initialize_scene()
tables = scene_initializer.get_shelf_floors()
walls = scene_initializer.get_walls()
camera_pose_sampler = suturo_blenderproc.sampler.pose_sampler.CameraPoseSampler(walls=walls[0])
object_pose_sampler = suturo_blenderproc.sampler.pose_sampler.ObjectPoseSampler(surface=tables[0])
light_pose_sampler = suturo_blenderproc.sampler.pose_sampler.LightPoseSampler(walls=walls[0])
furnitures = bproc.filter.by_attr(scene_initializer.get_all_mesh_objects(), "name", "Furniture.*", regex=True)

partitions = ObjectPartition(num_partitions=3,objects=scene_initializer.get_objects2annotate(),)
partitions.create_partition(partition_type=PartitionType.UNIQUE_OBJECTS, probability_reduction_factor=0.1)


# locations = [[4.4598, -3.395, 1.5], [5.44598, -3.395, 1.5], [4.64598, -2.595, 1.5], [4.64598, -4.195, 1.5],
#              [3.84598, -3.395, 1.5]]
# set_homogeneous_lighting(locations=locations, strength=22)


# centroid of table = 5.40737, -3.2758
# plate dimension = 0.26,0.26, 0,02
# bowl dimension = 0.168, 0.168, 0.055
def deploy_scene(x, objects):
    for i in range(x):
        subset = np.random.choice(objects, size=2)
        print(subset.shape)
        hide_render_objects(subset, False)
        light_pose_sampler.sample_homogenous_lights_around_center(200)
        blenderproc.object.sample_poses_on_surface(subset, tables[0].mesh_object,
                                                   object_pose_sampler.sample_object_pose_uniform,
                                                   max_tries=333,
                                                   min_distance=0.3, max_distance=0.7, up_direction=None,
                                                   check_all_bb_corners_over_surface=True)
        radius = np.random.uniform(1.2, 1.8)
        camera_pose_sampler.get_sampled_circular_cam_poses(num_poses=2, radius=radius,
                                                           center=np.array([5.40, -3.2758]),
                                                           poi=config.get_position_of_interest(), height=1.4)
        hide_render_objects(furnitures, False)
        # Render the scene

        data = bproc.renderer.render()
        # Write the rendering into an hdf5 file
        hide_render_objects(furnitures, True)

        seg_data = bproc.renderer.render_segmap(map_by=["instance", "class", "name"])

        bproc.writer.write_coco_annotations(
            os.path.join("/home/naser/workspace/SUTURO/SUTURO_WSS/SUTURO-Blenderproc/SUTURO-blenderproc/output",
                         'coco_data'),
            instance_segmaps=seg_data["instance_segmaps"],
            instance_attribute_maps=seg_data["instance_attribute_maps"],
            colors=data["colors"],
            color_file_format="JPEG")
        bproc.writer.write_hdf5("/home/naser/workspace/SUTURO/SUTURO_WSS/SUTURO-Blenderproc/SUTURO-blenderproc/output",
                                data)
        hide_render_objects(subset, True)
        blenderproc.utility.reset_keyframes()


def pipeline():
    hide_render_objects(scene_initializer.get_all_mesh_objects(), True)
    hide_render_objects(scene_initializer.get_objects2annotate(), False)
    objects = scene_initializer.get_objects2annotate()
    hide_render_objects(objects, True)
    deploy_scene(3, objects)


pipeline()
