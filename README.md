# SUTURO-blenderproc
Blenderproc implementation for the SUTURO Project
# About
- Einleitung, ToDo: Sorin

The Suturo Blenderproc Synthetic Data-generation is a tool created for the Suturo project, based on the blenderproc framework, that generates a dataset for model training by considering some parameters.
This method should ease the process of acquiring annotated data in a high amount, relatively fast and without manually annotation. The output of this tool is a dataset that contains segmentation masks and bounding boxes for all objects in the data. The parameters that can be configured are for example the wanted objects, the scene, lighting strength and more, this can be read in the User Configuration section.
## Object Sampling
- Randomization Sampling bla bla ToDo: Naser
## Camera Sampling
- POI, Rotation, Position, bla bla bla, ToDo: Naser
# Install
ToDo: Sorin
- git clone this one
- git clone the data folder

In order to run the tool, you need to create a new directory and clone two repositories into it, both repos has to be in the same directory.
~ mkdir ~/workspace/Suturo_blenderproc
~ cd ~/workspace/Suturo_blenderproc
~ git clone this
~ git clone data

HIER ORDNERSTRUKTUR ERKLÄREN?

To run the pipeline you have to configure the configuration.yaml file situated in PATHTOCONFIG, please refer to the User Configuration section for more information regarding the configuration.
After everything is set up you can run the following command in the Command Line Interface:

`blenderproc run main.py --config_yaml toy_config`
# HowTo
ToDo: Sorin
## How to include new objects into the synthetic data generation?

## How to start the process of synthetic data generation?

## How to train on the newly generated data

# User Configuration
Within the configuration.yaml file you can tweak all neeeded parameters that are required for the synthetic data generation.

- scene: Choose the scene you want to use for the generation process
- objects: A list of objects that should be in the scene and annotated.
- obj_source: path to the objects you want to import into blender.
- number of camera poses/iterations: Set the number of camera poses and how many times the object sampling should be executed
- path_to_id2name: Path to the json file containing the id's of objects
- lighting_strength: Set the lighting strength for the scene (default 50)
- output_path: The path were the images/annotations will be saved.
- yolo_train: Boolean if you want to train automatically after the dataset is generated (default False).
- combine_with_existing_dataset: Boolean Combine the converted yolo dataset with an already existing one, only working when yolo_train is set on True.
- path_to_dataset_that_has_to_be_combined: path to the dataset that you want to combine with the newly generated yolo dataset, only working when combine_with_existing_dataset=True


