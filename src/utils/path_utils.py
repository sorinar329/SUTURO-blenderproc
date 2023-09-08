from pathlib import Path


def get_project_root():
    p = get_suturo_blenderproc_path()
    return p.parent


def get_suturo_blenderproc_path():
    """Return the root directory of the project."""
    p = get_project_src_dir()
    return p.parent


def get_path_id2name_json():
    p = Path.cwd().joinpath(get_suturo_blenderproc_path(), "data", "id2name.json")
    if not p.exists():
        raise Exception("id2name.json doesn't exist")
    return p


def get_path_yaml_config(filename):
    p = Path.cwd().joinpath(get_suturo_blenderproc_path(), "data/yaml", filename)
    if p.suffix != ".yaml":
        p = p.with_suffix(".yaml")
        if p.is_file():
            return p
        else:
            raise Exception("File doesn't exist")

    if not p.is_file():
        raise Exception("File doesn't exist")
    return p


def get_project_src_dir():
    p = Path.cwd()
    while p.stem != "src":
        p = p.parent

    return p


def get_path_output_dir():
    p = Path.cwd().joinpath(get_suturo_blenderproc_path(), "output")
    if not p.exists():
        Path(p).mkdir(parents=True)
    return p


def get_path_blender_scene(scene):
    p = Path.cwd().joinpath(get_project_root(), "suturo-blenderproc_data/scenes", scene)
    if not p.exists():
        print("Doesn't exist")
        return Path.cwd().joinpath(get_project_root(), "suturo-blenderproc_data/scenes", f"{scene}.blend")

    return p
