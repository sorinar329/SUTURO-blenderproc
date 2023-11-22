import os
# from natsort import natsorted
import os
import shutil
from yolo.annotations.convert_to_yolo import create_list_from_categories

import re


# Key function for sorting
def natural_sort_key(filename):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]


# Sort the files in the given folder naturally
def sort_files_naturally(folder_path):
    if not os.path.isdir(folder_path):
        raise ValueError(f"The provided path '{folder_path}' is not a valid directory.")

    files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
    sorted_files = sorted(files, key=natural_sort_key)

    return sorted_files


# Creates a new directory for the combined dataset
def create_new_dir(parent_dir, name):
    new_dir = os.path.join(parent_dir + name)
    try:
        os.makedirs(new_dir, exist_ok=True)
        print("Directory '%s' created successfully" % name)
    except OSError as error:
        print("Directory '%s' can not be created" % name)
    os.mkdir(new_dir + "/train")
    os.mkdir(new_dir + "/train/labels")
    os.mkdir(new_dir + "/train/images")
    os.mkdir(new_dir + "/val")
    os.mkdir(new_dir + "/val/images")
    os.mkdir(new_dir + "/val/labels")


# Rename the images, to avoid problems, where two datasets contain files with the same name
def rename_images(path, i=0):
    print(path)
    data = sort_files_naturally(path)

    for d in data:
        os.rename(path + d,
                  path + "image" + str(i) + ".jpg")
        i = i + 1


# Rename the labels, to avoid problems, where two datasets contain files with the same name
def rename_labels(path, i=0):
    data = sort_files_naturally(path)
    for d in data:
        os.rename(path + d,
                  path + "image" + str(i) + ".txt")
        i = i + 1


# Combining the given datasets, creating new subfolders for the train/val files, as well as the data which
# are important for the data.yaml.
def combine_datasets(first, second, parent_dir, name, path_to_json_for_id):
    t1 = 0
    t2 = 0
    v1 = 0
    v2 = 0
    index1 = 0
    index2 = 0
    new_folder = os.path.join(parent_dir + name)
    create_new_dir(parent_dir, name)
    obj_list = create_list_from_categories(path_to_json_for_id)

    f = open(new_folder + "/data.yaml", "w+")
    f.write("train: " + str(new_folder + "/train/images \n"))
    f.write("val: " + str(new_folder + "/val/images \n"))
    f.write("nc: " + str(len(obj_list)) + "\n")
    f.write("names: " + str(obj_list))
    if "train" in os.listdir(first):
        t1 = t1 + len(os.listdir(first + "/train/images"))
        index1 = index1 + len(os.listdir(first + "/train/images"))

    if "train" in os.listdir(second):
        t2 = t1 + len(os.listdir(second + "/train/images"))
        index2 = index2 + len(os.listdir(second + "/test/images"))

    if "val" in os.listdir(first):
        v1 = v1 + len(os.listdir(first + "/val/images"))
        index1 = index1 + len(os.listdir(first + "/val/images"))

    if "val" in os.listdir(second):
        v2 = v1 + len(os.listdir(second + "/val/images"))
        index2 = index2 + len(os.listdir(second + "/val/images"))

    if "test" in os.listdir(first):
        v2 = v1 + len(os.listdir(first + "/test/images"))
        index1 = index1 + len(os.listdir(first + "/test/images"))

    if "test" in os.listdir(second):
        v2 = v1 + len(os.listdir(second + "/test/images"))
        index2 = index2 + len(os.listdir(second + "/test/images"))

    for item in os.listdir(second + "/train/images"):
        shutil.copy(second + "/train/images/" + item, new_folder + "/train/images")

    for item in os.listdir(second + "/train/labels"):
        shutil.copy(second + "/train/labels/" + item, new_folder + "/train/labels")

    for item in os.listdir(second + "/val/images"):
        shutil.copy(second + "/val/images/" + item, new_folder + "/val/images")

    for item in os.listdir(second + "/val/labels"):
        shutil.copy(second + "/val/labels/" + item, new_folder + "/val/labels")

    rename_images(new_folder + "/train/images/", i=index1)
    rename_images(new_folder + "/val/images/", i=index1)
    rename_labels(new_folder + "/train/labels/", i=index1)
    rename_labels(new_folder + "/val/labels/", i=index1)

    for item in os.listdir(first + "/train/images"):
        shutil.copy(first + "/train/images/" + item, new_folder + "/train/images")

    for item in os.listdir(first + "/train/labels"):
        shutil.copy(first + "/train/labels/" + item, new_folder + "/train/labels")

    for item in os.listdir(first + "/val/images"):
        shutil.copy(first + "/val/images/" + item, new_folder + "/val/images")

    for item in os.listdir(first + "/val/labels"):
        shutil.copy(first + "/val/labels/" + item, new_folder + "/val/labels")

    rename_images(new_folder + "/train/images/")
    rename_images(new_folder + "/val/images/")
    rename_labels(new_folder + "/train/labels/")
    rename_labels(new_folder + "/val/labels/")
