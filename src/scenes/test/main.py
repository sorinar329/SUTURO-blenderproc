import blenderproc as bproc
import sys
from pathlib import Path
import numpy as np

p = Path.cwd()
while p.stem != "src":
    p = p.parent
import os

sys.path.append(str(p))
import scenes.argparser
import utils.yaml_config
import utils.path_utils
import suturo_blenderproc.scene_init

args = scenes.argparser.get_argparse()
config = utils.yaml_config.YAMLConfig(filename=args.config_yaml)
scene_initializer = suturo_blenderproc.scene_init.SceneInitializer(yaml_config=config)
scene_initializer.initialize_scene()
objs = scene_initializer.get_objects2annotate()
tables = scene_initializer.get_table_surfaces_round()
bproc.object.sample_poses(
    objs,
    sample_pose_func=scene_initializer.sample_object_positions_gaussian,
    objects_to_check_collisions=objs,
    max_tries=500
)

os.abort()
