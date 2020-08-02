import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
import matplotlib
from matplotlib import pyplot as plt
from PIL import Image
import cv2
import json
import requests

import label_map_util
import visualization_utils as vis_util

import glob




# Path of trained model and pbtxt
MODEL_NAME = './weights'

PATH_TO_CKPT = MODEL_NAME + '/road.pb'
PATH_TO_LABELS = os.path.join(MODEL_NAME, 'labelmap.pbtxt')
NUM_CLASSES = 5

threshold = 50

# Path of image directory
PATH_TO_TEST_IMAGES_DIR = "./images_test"


# Load frozen model
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.compat.v2.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
        
# Load label Map        
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)    

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

# Making list of all images in folder
# ALL_IMAGES = os.listdir(PATH_TO_TEST_IMAGES_DIR)

# TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR, FILE) for FILE in ALL_IMAGES]

def detectObjectFromPathList(TEST_IMAGE_PATHS):
    finalBoxes = []
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

        
            for image_path in TEST_IMAGE_PATHS:
                pothole = 0
                longitudinal = 0
                transverse = 0
                background = 0
                aligator = 0
                
                img_sh = cv2.imread(image_path)
                height_img = img_sh.shape[0]
                width_img = img_sh.shape[1]
                
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
                vis_util.visualize_boxes_and_labels_on_image_array(
                                                                image_np,
                                                                np.squeeze(boxes),
                                                                np.squeeze(classes).astype(np.int32),
                                                                np.squeeze(scores),
                                                                category_index,
                                                                use_normalized_coordinates=True,
                                                                line_thickness=8,
                                                                min_score_thresh=.7)
                                                            
                percentage_confidence = scores[0]*100
                
                # Checking number of detected object above threshold
                
                for i in range(percentage_confidence.shape[0]):
                    if percentage_confidence[i]>threshold:
                        value = (i,percentage_confidence[i])
                        finalBoxes.append(value)
                number_total_detected = len(finalBoxes)
                
                classes_len = list(classes[0][:number_total_detected])
                
                # If there is no detection pass
                if number_total_detected != 0:
                        # Finding class of detected objects and making a dictionary
                        for c in classes_len:
                            c = int(c)
                            try:
                                if category_index[c]["name"]=='Longitudinal_crack':
                                    longitudinal = longitudinal + 1
                                if  category_index[c]["name"]== 'Transverse_crack':
                                    transverse = transverse + 1
                                if category_index[c]["name"]=='Aligator_crack':
                                    aligator = aligator + 1
                                if  category_index[c]["name"]== 'Pothole':
                                    pothole = pothole + 1  
                                if  category_index[c]["name"]== 'Background':
                                    pass
                            except:
                                continue


                        total = {'Longitudinal_crack': longitudinal, 'Transverse_crack': transverse, 'Aligator_crack': aligator
                                    ,'Pothole': pothole  }     

                        box_len = list(boxes[0][:number_total_detected])

                        # Croping the detected object and calculating the severity of defect
                        counter = 0
                        Severity = []
                        class_val = 0

                        for b in box_len:
                            y1 = int(b[0]*height_img)
                            x1 = int(b[1]*width_img)
                            y2 = int(b[2]*height_img)
                            x2 = int(b[3]*width_img)
                            img_sh = img_sh[y1:y2, x1:x2]
                            try:
                                if int(classes_len[counter])==1:
                                        img_r_1 = cv2.cvtColor(img_sh, cv2.COLOR_BGR2GRAY)
                                        img_1 = cv2.GaussianBlur(img_r_1,(3,3),0)
                                        lap_1 = cv2.Laplacian(img_1, cv2.CV_64F, ksize=3)
                                        lap_1 = np.uint8(np.absolute(lap_1))
                                        _, mask_1 = cv2.threshold(lap_1, 50,255, cv2.THRESH_BINARY)
                                        pixel_1 = mask_1.reshape(-1)
                                        pixel_1 = list(pixel_1)
                                        n_1 = pixel_1.count(255)
                                        m_1  = pixel_1.count(0)
                                        ratio_1 = n_1/m_1

                                        if ratio > 0.1:
                                            val = "Large_Longitudinal_Crack"
                                            lc_qual = 1
                                        if ratio < 0.1 and ratio > 0.009:
                                            val = "Medium_Longitudinal_Crack"
                                            lc_qual = 2
                                        if ratio<0.009:
                                            val = "Small_Longitudinal_Crack"
                                            lc_qual = 3

                                if int(classes_len[counter])==2:
                                        img_r_1 = cv2.cvtColor(img_sh, cv2.COLOR_BGR2GRAY)
                                        img_1 = cv2.GaussianBlur(img_r_1,(3,3),0)
                                        lap_1 = cv2.Laplacian(img_1, cv2.CV_64F, ksize=3)
                                        lap_1 = np.uint8(np.absolute(lap_1))
                                        _, mask_1 = cv2.threshold(lap_1, 50,255, cv2.THRESH_BINARY)
                                        pixel_1 = mask_1.reshape(-1)
                                        pixel_1 = list(pixel_1)
                                        n_1 = pixel_1.count(255)
                                        m_1  = pixel_1.count(0)
                                        ratio = n_1/m_1

                                        if ratio > 0.15:
                                            val = "Large_Transeverse_Crack"
                                            tc_qual = 1
                                        if ratio < 0.15 and ratio > 0.06:
                                            val = "Medium_Transverse_Crack"
                                            tc_qual = 2
                                        if ratio<0.06:
                                            val = "Small_Transeverse_Crack"  
                                            tc_qual = 3

                                if int(classes_len[counter])==3:
                                        img_r_1 = cv2.cvtColor(img_sh, cv2.COLOR_BGR2GRAY)
                                        img_1 = cv2.GaussianBlur(img_r_1,(3,3),0)
                                        lap_1 = cv2.Laplacian(img_1, cv2.CV_64F, ksize=3)
                                        lap_1 = np.uint8(np.absolute(lap_1))
                                        _, mask_1 = cv2.threshold(lap_1, 50,255, cv2.THRESH_BINARY)
                                        pixel_1 = mask_1.reshape(-1)
                                        pixel_1 = list(pixel_1)
                                        n_1 = pixel_1.count(255)
                                        m_1  = pixel_1.count(0)
                                        ratio = n_1/m_1

                                        if ratio > 0.05:
                                            val =  "Large_Aligator_crack"
                                            ac_qual = 1
                                        if ratio < 0.05 and ratio > 0.008:
                                            val = "Medium_Aligator_crack"
                                            ac_qual = 2
                                        if ratio<0.008:
                                            val = "Small_Aligator_crack"  
                                            ac_qual = 3


                                if int(classes_len[counter])==4:
                                        img_r_1 = cv2.cvtColor(img_sh, cv2.COLOR_BGR2GRAY)
                                        img_1 = cv2.GaussianBlur(img_r_1,(3,3),0)
                                        lap_1 = cv2.Laplacian(img_1, cv2.CV_64F, ksize=3)
                                        lap_1 = np.uint8(np.absolute(lap_1))
                                        _, mask_1 = cv2.threshold(lap_1, 50,255, cv2.THRESH_BINARY)
                                        pixel_1 = mask_1.reshape(-1)
                                        pixel_1 = list(pixel_1)
                                        n_1 = pixel_1.count(255)
                                        m_1  = pixel_1.count(0)
                                        ratio = n_1/m_1

                                        if ratio > 0.05:
                                            val = "Large_Pothole"
                                            ph_qual = 1
                                        if ratio < 0.05 and ratio > 0.008:
                                            val = "Medium_Pothole"
                                            ph_qual = 2
                                        if ratio<0.008:      
                                            val = "Small_Pothole"
                                            ph_qual = 3
                            except:
                                continue

                            Severity.append(val)          

                            counter = counter + 1  
                else:
                    total = {}
                    Severity = {}

                meta_data = [image_path,total, Severity]

                issues = []
                tot_qual = 0
                if longitudinal > 0:
                    lc = {
                        'issue_id': 'Longitudinal_crack',
                        'count': longitudinal,
                        'quality': lc_qual
                    }
                    issues.append(lc)
                    tot_qual += lc_qual
                # if transverse > 0:
                #     tc = {
                #         'issue_id': 'Transverse_crack',
                #         'count': transverse,
                #         'quality': tc_qual
                #     }
                #     issues.append(tc)
                if aligator > 0:
                    ac = {
                        'issue_id': 'Aligator_crack',
                        'count': aligator,
                        'quality': ac_qual
                    }
                    issues.append(ac)
                    tot_qual += ac_qual
                if pothole > 0:
                    ph = {
                        'issue_id': 'Pothole',
                        'count': pothole,
                        'quality': ph_qual
                    }
                    issues.append(ph)
                    tot_qual += ph_qual

                # print(meta_data)
                # print(issues)

                if len(issues) == 0:
                    image_qual = 5
                else:
                    image_qual = tot_qual//len(issues)
                result = {
                    'image': image_np,
                    'quality': image_qual,
                    'issues': str(issues)
                }
                # print(result)
                return result

# detectObjectFromPathList(['./images_test\\1003.png', './images_test\\1003.png', './images_test\\1004.jpg'])

CREATE_ROAD_URL = 'http://localhost:8000/api/create_road/'
UPDATE_IMAGE_URL = 'http://localhost:8000/api/update_road_image/'

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

        result = detectObjectFromPathList(IMAGE_PATH)

        result_image = result['image']

        result_image_path = os.path.join(RESULT_IMAGES_PATH, image)
        matplotlib.image.imsave(result_image_path, result_image)

        files = {'image': open(result_image_path, 'rb')}

        print(image.split('.')[0])
        image_json = {
            'image_id': image.split('.')[0],
            'road_id': road_json['road_id'],
            'quality': result['quality'],
            'issues': result['issues'],
        }
        print(image_json)

        r = requests.post(UPDATE_IMAGE_URL, data=image_json, files=files)
        print(r.text)
