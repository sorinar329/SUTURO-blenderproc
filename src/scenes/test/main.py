import blenderproc as bproc
import sys
from pathlib import Path

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
objs = bproc.loader.load_blend(utils.path_utils.get_path_blender_scene(args.scene))
config = utils.yaml_config.YAMLConfig(filename=args.config_yaml)
scene_initializer = suturo_blenderproc.scene_init.SceneInitializer(yaml_config=config, mesh_objects=objs)
for o in objs:
    print(o.get_name())
os.abort()
