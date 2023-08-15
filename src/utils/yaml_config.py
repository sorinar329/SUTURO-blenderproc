import yaml
from utils import path_utils


class YAMLConfig(object):
    def __init__(self, filename):
        config = str(path_utils.get_path_yaml_config(filename))
        with open(config, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        self._data = data_loaded

    def print(self):
        print(self._data)

    def get_list_object_positions(self):
        pos_dict = self._data['object_positions']
        return [v for k, v in pos_dict.items()]

    def get_list_camera_positions(self):
        locations_dict = self._data['camera_positions']
        return [v for k, v in locations_dict.items()]

    def get_position_of_interest(self):
        return self._data['position_of_interest']

    def get_objects(self):
        return self._data['objects']

    def get_scene(self):
        return self._data['scene']
