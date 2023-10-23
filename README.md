# SUTURO-blenderproc
Blenderproc implementation for the SUTURO Project
# About
The Suturo Blenderproc Synthetic Data-generation is a tool created for the Suturo project, based on the blenderproc framework, that generates a dataset for model training by considering some parameters.
This method should ease the process of acquiring annotated data in a high amount, relatively fast and without manually annotation. The output of this tool is a dataset that contains segmentation masks and bounding boxes for all objects in the data. The parameters that can be configured are for example the wanted objects, the scene, lighting strength and more, this can be read in the User Configuration section.
## Object Sampling
- Randomization Sampling bla bla ToDo: Naser
## Camera Sampling
- POI, Rotation, Position, bla bla bla, ToDo: Naser
# Install
This framework was tested on Ubuntu 20.04

## Set Up Workspace
In order to run the framework, you need to create a new directory and clone two repositories into it, both repos has to be in the same directory.

`mkdir ~/workspace/Suturo_blenderproc`

`cd ~/workspace/Suturo_blenderproc`

- git clone https://github.com/sorinar329/SUTURO-blenderproc

- git clone https://gitlab.informatik.uni-bremen.de/sorin/suturo-blenderproc_data

## Create a new Virtual Environment (optional)
Optionally you can create a new virtual env for this project. 

`python3 -m venv ~/workspace/Suturo_blenderproc/SUTURO-blenderproc/YOURENVNAME`

activate your new created virtual environment

`source ~/workspace/Suturo_blenderproc/SUTURO-blenderproc/YOURENVNAME/bin/activate`

Now you can install the required packages from the requirments.txt

`pip install -r ~/workspace/Suturo_blenderproc/SUTURO-blenderproc/requirements.txt`
# HowTo
ToDo: Sorin
## How to see which objects are already in the scene
To see which objects are already in the scene you should look at the blender scene itself and the objects folder `~/workspace/Suturo_blenderproc/suturo_blenderproc_data/objects`.
Standartwise we will inlcude all relevant YCB-Objects into the scenes.
## Where do i get more objects?
There are plenty of sources availabe for different type of objects.
- For furnitures you should take a look at the blender library https://www.blenderkit.com/.
- For the YCB objects we used http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com/
- If you want to scan your own products we advise you to use the App https://poly.cam/
- Also the PolyCam library can be a good source for different objects which are scanned by other users.
## How to import new objects into the synthetic data generation?
To include new objects into the scene, simply paste the objects into `~/workspace/Suturo_blenderproc/suturo_blenderproc_data/objects`.
If not already inlcuded in the id2name.json you have to include it there as well with the same name as the object.
At the moment only "*.glb" files are supported for import, this is the file format you will get when scanning objects with PolyCAM.

## How to start the process of synthetic data generation?
To run the pipeline you have to configure the configuration.yaml file situated in `~/workspace/Suturo_blenderproc/SUTURO-blenderproc/data/yaml` , please refer to the User Configuration section for more information regarding the configuration.
After everything is set up you can run the following command in the Command Line Interface:

`blenderproc run main.py --config_yaml toy_config`
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


# TODO:
- Dieses Duplicate einbauen
- Relative Pfade für die YAML erstellen
- Exception für die Materialänderung falls dieses Material nicht existiert.
- Requirments.txt an richtige Stelle bringen.
- Textures applyien auf die fehlenden Objekte
- Die Materialien einbauen für die einzelnen Objekte die das benötigen.
