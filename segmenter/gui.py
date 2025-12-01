import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton as mb
import cv2
import numpy as np
import os

"""
GUI for manually selecting masks for layer types 
in images to train segmenter. 
"""

shrink = 5

plt.ion()
plt.show()

pts_list = []

try:
    def on_key_press(event):
        pass

    for dirpath, dirnames, filenames in os.walk("test_images/Segmentation_Training"):
        if len(filenames) > 0:
            if "100X" in dirpath:
                magnification = 100
            elif "10X" in dirpath:
                magnification = 10
            else:
                raise ValueError("No Magnification Present in dirpath")

            _, label = os.path.split(dirpath)
            label = label[:-2]

            if "40" in label:
                label = "40+"
            
            for fname in filenames:
                img = cv2.imread(f"{dirpath}/{fname}", cv2.IMREAD_COLOR_RGB)
                # fig.canvas.mpl_connect('key_press_event', on_key_press)
                if img is None:
                    print("Failed to Load Image.")
                else:
                    img = cv2.resize(img, (img.shape[1]//shrink, img.shape[0]//shrink))
                    plt.title(fname)
                    plt.imshow(img)
                    points = np.asarray(plt.ginput(-1, mouse_add=mb.RIGHT, mouse_pop=None, timeout=-1))
                    pts_list.append(points)
                    plt.draw()

    plt.close()

except KeyboardInterrupt:
    print()

for points in pts_list:
    print(points)