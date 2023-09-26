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

    def get_number_of_iterations(self):
        return self._data['number_of_iterations']

    def get_id2name_path(self):
        return self._data["path_to_id2name"]

    def get_number_of_camera_samples(self):
        return self._data["number_of_camera_samples"]

    def get_yolo_training(self):
        return self._data["yolo_train"]

    def get_lighting_strength(self):
        return self._data["lighting_strength"]

    def get_combine_dataset(self):
        return self._data["combine_with_existing_dataset"]

    def get_path_to_combine_dataset(self):
        return self._data["path_to_dataset_that_has_to_be_combined"]

    def get_path_to_object_source(self):
        return self._data["obj_source"]

    def get_output_path(self):
        return self._data["output_path"]

    def get_yolo_save_path(self):
        return self._data["yolo_save_path"]