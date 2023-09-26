import os
import json
import shutil
from sklearn.model_selection import train_test_split


# Generates a list of objects from the id2namejson
def create_list_from_categories(path_to_json):
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    l = []
    val = list(data.values())
    for v in val:
        new_val = v.replace("suturo:", "").replace("soma:", "").replace("soma_home", "").replace("'", "")
        l.append(new_val)
    return l


# Computes the BBox format for YOLO from COCO-Format
def convert_bbox_coco2yolo(img_width, img_height, bbox):
    # YOLO bounding box format: [x_center, y_center, width, height]
    # (float values relative to width and height of image)

    x_tl = bbox[0]
    y_tl = bbox[1]
    w = bbox[2]
    h = bbox[3]

    dw = 1.0 / img_width
    dh = 1.0 / img_height

    x_center = x_tl + w / 2.0
    y_center = y_tl + h / 2.0

    x = x_center * dw
    y = y_center * dh
    w = w * dw
    h = h * dh

    return [x, y, w, h]


# Converts the annotations from the coco.json into one annotation.txt for every image.
# This is required for YOLO training.
def convert_coco_to_yolo(path_to_coco_annotation, new_dir, j=0):
    f = open(path_to_coco_annotation)
    data = json.load(f)
    anns = data["annotations"]
    lines = []
    i = 0
    os.makedirs(new_dir + "/labels/")
    for ann in anns:
        img_id = ann["image_id"]
        if img_id == i:
            bbox = ann["bbox"]
            c = convert_bbox_coco2yolo(640, 480, bbox)
            coordinates = str(c).replace('[', '').replace(']', '').replace(',', '')
            id = ann["category_id"]
            line = str(id) + " " + str(coordinates) + "\n"
            lines.append(line)
        elif img_id == i + 1:
            with open(new_dir + '/labels/image' + str(img_id - 1 + j) + '.txt', 'w') as f:
                for line in lines:
                    f.write(line)
            lines = []
            bbox = ann["bbox"]
            c = convert_bbox_coco2yolo(640, 480, bbox)
            coordinates = str(c).replace('[', '').replace(']', '').replace(',', '')
            id = ann["category_id"]

            line = str(id) + " " + str(coordinates) + "\n"
            lines.append(line)
            i = i + 1
        else:

            i = i + 1


#Moves the images from an old directory to the target directory
def move_images_to_new_dir(old_dir, new_dir):
    os.makedirs(new_dir + "/images")
    for item in sorted(os.listdir(old_dir)):
        shutil.copy(old_dir + item, new_dir + "/images/" + item)
    os.remove(new_dir + "/images/" + sorted(os.listdir(new_dir + "/images"))[len(sorted(os.listdir(old_dir))) - 1])



def move_files_to_folder(list_of_files, destination_folder):
    for f in list_of_files:
        try:
            shutil.move(f, destination_folder)
        except:
            assert False


#Splits the dataset into Train/Validation/Test subsets
def trainsplit(path_source):
    os.makedirs(path_source + "train/images")
    os.makedirs(path_source + "val/images")
    os.makedirs(path_source + "test/images")
    os.makedirs(path_source + "train/labels")
    os.makedirs(path_source + "val/labels")
    os.makedirs(path_source + "test/labels")
    images = [os.path.join(path_source + "images/", x) for x in
              os.listdir(path_source + "images/") if x[-3:] == "jpg"]
    annotations = [os.path.join(path_source + "labels/", x) for x in
                   os.listdir(path_source + "labels/") if x[-3:] == "txt"]
    images.sort()
    annotations.sort()

    # Split the dataset into train-valid-test splits
    train_images, val_images, train_annotations, val_annotations = train_test_split(images, annotations, test_size=0.05,
                                                                                    random_state=1)
    val_images, test_images, val_annotations, test_annotations = train_test_split(val_images, val_annotations,
                                                                                  test_size=0.05, random_state=1)

    move_files_to_folder(train_images, path_source + "train/images")
    move_files_to_folder(val_images, path_source + "val/images")
    move_files_to_folder(test_images, path_source + "test/images")
    move_files_to_folder(train_annotations, path_source + "train/labels")
    move_files_to_folder(val_annotations, path_source + "val/labels")
    move_files_to_folder(test_annotations, path_source + "test/labels")


def rename_images(path_to_new_dir, i=0):
    data = sorted(os.listdir("/home/sorin/data/storing_groceries/images/"))
    for d in data:
        os.rename("/home/sorin/data/storing_groceries/images/" + d,
                  "/home/sorin/data/storing_groceries/images/" + "image" + str(i) + ".jpg")
        i = i + 1


# Generates the data.yaml according to the data for the YOLO training.
def write_data_yaml(path_to_json_for_id, new_folder):
    obj_list = create_list_from_categories(path_to_json_for_id)
    f = open(new_folder + "/data.yaml", "w+")
    f.write("train: " + str(new_folder + "/train/images \n"))
    f.write("val: " + str(new_folder + "/val/images \n"))
    f.write("nc: " + str(len(obj_list)) + "\n")
    f.write("names: " + str(obj_list))


def create_yolo_dataset(id2name_json, coco_annotations, old_dir, new_dir):
    convert_coco_to_yolo(coco_annotations, new_dir)
    move_images_to_new_dir(old_dir, new_dir)
    rename_images(path_to_new_dir=new_dir + "/images/", i=0)
    trainsplit(new_dir + "/")
    write_data_yaml(id2name_json, new_dir)
