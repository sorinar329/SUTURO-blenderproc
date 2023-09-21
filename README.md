# SUTURO-blenderproc
Blenderproc implementation for the SUTURO Project
# About

## Object Sampling

## Camera Sampling

# Install
Pls put the SUTURO-blenderproc and the the project with scenes in a workspace. 

To run the test pipeline you can type the following command in the CLI:

`blenderproc run main.py --config_yaml toy_config`

where config_yaml should be any yaml file located at data/yaml. Which scene
you wish to render, should be set in yaml file with the file `scene`. Take a look
at `data/yaml/toy_config.yaml`
# User Configuration
Within the configuration.yaml file you can tweak all neeeded parameters that are required for the synthetic data generation.

- objects: A list of objects that should be in the scene and annotated.
- number of camera poses/iterations: Set the number of camera poses and how many times the object sampling should be executed

