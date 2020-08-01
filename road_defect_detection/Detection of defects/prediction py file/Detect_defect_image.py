

# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import sys

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")

# Import utilites
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'inference_graph'
IMAGE_NAME = 'test2.jpg'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH,'road.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'labelmap.pbtxt')

# Path to image
PATH_TO_IMAGE = os.path.join(CWD_PATH,IMAGE_NAME)

# Number of classes the object detector can identify
NUM_CLASSES = 5

# Load the label map.
# Label maps map indices to category names, so that when our convolution
# network predicts `5`, we know that this corresponds to `king`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Load image using OpenCV and
# expand image dimensions to have shape: [1, None, None, 3]
# i.e. a single-column array, where each item in the column has the pixel RGB value


dirs = ["High_Pothole","Medium_Pothole","Low_Pothole","High_Aligator_crack","Medium_Aligator_crack","Low_Aligator_crack"]
for d in dirs:
    try:
        os.mkdir(d)
    except:
        continue    

import os
path_test = "./images_test"

lists = os.listdir("./images_test")

for l in lists:
    path  = os.path.join(path_test, l)

    image = cv2.imread(path)
    image_expanded = np.expand_dims(image, axis=0)

    # Perform the actual detection by running the model with the image as input
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: image_expanded})

    # Draw the results of the detection (aka 'visulaize the results')

    vis_util.visualize_boxes_and_labels_on_image_array(
        image,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.60)
    coordinates = vis_util.return_coordinates(
                    image,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8,
                    min_score_thresh=0.60)
    

    for coordinate in coordinates:
            (y1, y2, x1, x2, acc, label_obj) = coordinate
            height = y2-y1
            width = x2-x1
    if coordinates!=[]:
        image = image[y1:y1+height,x1:x1+width ]   
        img = cv2.GaussianBlur(image,(3,3),0)
        lap = cv2.Laplacian(img, cv2.CV_64F, ksize=3)
        lap = np.uint8(np.absolute(lap))
        _, mask = cv2.threshold(lap, 50,255, cv2.THRESH_BINARY)
        pixel = mask.reshape(-1)
        pixel = list(pixel)
        n = pixel.count(255)
        m  = pixel.count(0)
        ratio = n/m
        if label_obj =="Pothole":
            if ratio > 0.15:
                    path = "./High_Pothole/"+str(l)+".jpg"
                    cv2.imwrite(path,image )
            if ratio < 0.06:
                    path = "./Medium_Pothole/"+str(l)+".jpg"
                    cv2.imwrite(path,image )
            if ratio>0.15 and ratio<0.06:
                    path = "./Low_Pothole/"+str(l)+".jpg"
                    cv2.imwrite(path,image )      
        if label_obj =='Aligator_crack':
            if ratio > 0.05:
                    path = "./High_Aligator_crack/"+str(l)+".jpg"
                    cv2.imwrite(path,image )
            if ratio < 0.008:
                    path = "./Medium_Aligator_crack/"+str(l)+".jpg"
                    cv2.imwrite(path,image )
            if ratio>0.05 and ratio<0.008:
                    path = "./Low_Aligator_crack/"+str(l)+".jpg"
                    cv2.imwrite(path,image )  
            ######################################## Rest will be added ######################                    
    # All the results have been drawn on image. Now display the image.
    cv2.imshow('Object detector', image)

    # Press any key to close the image
    cv2.waitKey(0)

    # Clean up
    cv2.destroyAllWindows()
