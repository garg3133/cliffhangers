import cv2
import numpy as np
import matplotlib.pyplot as plt

dim = (200,200)
img_real_1 = cv2.imread("l1.jpg")
img_r_1 = cv2.imread("l1.jpg",cv2.IMREAD_GRAYSCALE)
img_real_1 = cv2.resize(img_real_1, dim, interpolation = cv2.INTER_AREA)
img_r_1 = cv2.resize(img_r_1, dim, interpolation = cv2.INTER_AREA)
img_1 = cv2.GaussianBlur(img_r_1,(5,5),0)


lap_1 = cv2.Laplacian(img_1, cv2.CV_64F, ksize=5)
lap_1 = np.uint8(np.absolute(lap_1))
_, mask_1 = cv2.threshold(lap_1, 100,255, cv2.THRESH_BINARY)

img_real_2 = cv2.imread("l2.jpg")
img_r_2 = cv2.imread("l2.jpg",cv2.IMREAD_GRAYSCALE)
img_real_2 = cv2.resize(img_real_2, dim, interpolation = cv2.INTER_AREA)
img_r_2 = cv2.resize(img_r_2, dim, interpolation = cv2.INTER_AREA)
img_2 = cv2.GaussianBlur(img_r_2,(5,5),0)


lap_2 = cv2.Laplacian(img_2, cv2.CV_64F, ksize=5)
lap_2 = np.uint8(np.absolute(lap_2))
_, mask_2 = cv2.threshold(lap_2, 100,255, cv2.THRESH_BINARY)

img_real_3 = cv2.imread("l3.jpg")
img_r_3 = cv2.imread("l3.jpg",cv2.IMREAD_GRAYSCALE)
img_real_3 = cv2.resize(img_real_3, dim, interpolation = cv2.INTER_AREA)
img_r_3 = cv2.resize(img_r_3, dim, interpolation = cv2.INTER_AREA)
img_3 = cv2.GaussianBlur(img_r_3,(5,5),0)


lap_3 = cv2.Laplacian(img_3, cv2.CV_64F, ksize=5)
lap_3 = np.uint8(np.absolute(lap_3))
_, mask_3 = cv2.threshold(lap_3, 100,255, cv2.THRESH_BINARY)

pixel_1 = mask_1.reshape(-1)
pixel_1 = list(pixel_1)
n_1 = pixel_1.count(255)
m_1  = pixel_1.count(0)
ratio_1 = n_1/m_1

pixel_2 = mask_2.reshape(-1)
pixel_2 = list(pixel_2)
n_2 = pixel_2.count(255)
m_2  = pixel_2.count(0)
ratio_2 = n_2/m_2

pixel_3 = mask_3.reshape(-1)
pixel_3 = list(pixel_3)
n_3 = pixel_3.count(255)
m_3  = pixel_3.count(0)
ratio_3 = n_3/m_3


fig, axs = plt.subplots(2, 3)
axs[0, 1].set_title("L5, G(3,3)")
axs[0, 0].imshow(img_real_1)
axs[0, 1].imshow(img_real_2)
axs[0, 2].imshow(img_real_3)
axs[1, 0].imshow(mask_1)
print("Pixel wise ratio: ")
print(round(ratio_1,4),round(ratio_2,4),round(ratio_3,4))
axs[1, 1].imshow(mask_2)
axs[1, 2].imshow(mask_3)




fig, axs = plt.subplots(2, 3)
axs[0,0].imshow(img_real_1)
axs[0,1].imshow(img_r_1)
axs[0,2].imshow(img_1)
axs[1,0].imshow(lap_1)
axs[1,1].imshow(mask_1)

