import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

import glob
import json
import requests
import random
import cv2

from io import StringIO
import matplotlib
from matplotlib import pyplot as plt
from PIL import Image

from collections import defaultdict



import label_map_util

import visualization_utils as vis_util

# What model to download.
MODEL_NAME = './weights'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/road.pb'

# List of the strings that is used to add correct label for each box.
# PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

PATH_TO_LABELS = os.path.join(MODEL_NAME, 'labelmap.pbtxt')


NUM_CLASSES = 90


detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')


# ## Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)




def detectObjectFromPathList(TEST_IMAGE_PATHS, detection_graph=detection_graph, category_index=category_index):
    predictionList = []
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
        # Definite input and output Tensors for detection_graph
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            fig = plt.figure()

            for image_path in TEST_IMAGE_PATHS:
                image = Image.open(image_path)
          # the array based representation of the image will be used later in order to prepare the
          # result image with boxes and labels on it.
                # image_np = load_image_into_numpy_array(image)
                image_np = cv2.imread(image_path, 1)
          # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
          # Actual detection.
                (boxes, scores, classes, num) = sess.run(
                   [detection_boxes, detection_scores, detection_classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})
                values = image_path,image_np,boxes,classes,scores,category_index
                predictionList.append(values)
                
    detected_image = []
    for i in range(len(predictionList)):
        image_path,image_np,boxes,classes,scores,category_index = predictionList[i]
        # Visualization of the results of a detection.
        vis_util.visualize_boxes_and_labels_on_image_array(
          image_np,
          np.squeeze(boxes),
          np.squeeze(classes).astype(np.int32),
          np.squeeze(scores),
          category_index,
          use_normalized_coordinates=True,
          line_thickness=12)

        #plt.figure(figsize=(4,4))
        #plt.imshow(image_np)
        detected_image.append(image_np)

        # Send Image data to server

    return detected_image


CREATE_ROAD_URL = 'http://amanchande.co/api/create_road/'
UPDATE_IMAGE_URL = 'http://amanchande.co/api/update_road_image/'

PATH_TO_UNTESTED_ROAD_DIR = './road_images/untested/'

# Size, in inches, of the output images.
IMAGE_SIZE = (8,8)

# Loop through all folders containing Road Images
for folder in os.listdir(PATH_TO_UNTESTED_ROAD_DIR):
    FOLDER_PATH = os.path.join(PATH_TO_UNTESTED_ROAD_DIR, folder)
    IMAGES_PATH = os.path.join(FOLDER_PATH, 'images')
    RESULT_IMAGES_PATH = os.path.join(FOLDER_PATH, 'results')

    # Read Road JSON
    ROAD_JSON_PATH = os.path.join(FOLDER_PATH, 'road.json')
    road_json_file = open(ROAD_JSON_PATH, "r")
    road_json = json.load(road_json_file)
    road_json_file.close()

    # Calculate total images
    images_list = os.listdir(IMAGES_PATH)
    image_jsons_num = len(images_list)
    road_json['total_images'] = image_jsons_num
    print(image_jsons_num, images_list)

    r = requests.post(CREATE_ROAD_URL, data=road_json)
    print(r.text)

    # Test Images
    for image in images_list:
        IMAGE_PATH = glob.glob(os.path.join(IMAGES_PATH, image))

        image_array = detectObjectFromPathList(IMAGE_PATH, detection_graph, category_index)
        result_image = image_array[0]

        result_image_path = os.path.join(RESULT_IMAGES_PATH, image)
        matplotlib.image.imsave(result_image_path, result_image)

        files = {'image': open(result_image_path, 'rb')}

        print(image.split('.')[0])
        image_json = {
            'image_id': image.split('.')[0],
            'road_id': road_json['road_id'],
            'quality': random.randint(1, 5),
            'issues':'[]',
        }
        print(image_json)

        r = requests.post(UPDATE_IMAGE_URL, data=image_json, files=files)
        print(r.text)


