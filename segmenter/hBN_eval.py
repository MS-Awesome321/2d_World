import os
from tqdm import tqdm 
import numpy as np
import cv2
from segmenter import Segmenter
from material import hBN
import shutil

# Sort Files
# hBN_pics = []
# for folder in ["1", "2", "3", "4"]:
#     for file in os.listdir(f"/Users/mayanksengupta/Desktop/hBN-new{folder}"):
#         hBN_pics.append(f"/Users/mayanksengupta/Desktop/hBN-new{folder}/{file}")

# hBN_pics = np.array(hBN_pics)
# np.random.shuffle(hBN_pics)

# limit = 150


# hBN_20 = []
# hBN_10 = []
# hBN_5 = []

# for filename in hBN_pics:
#     if 'M20' in filename:
#         if len(hBN_20) < limit:
#             hBN_20.append(filename)

#     elif 'M10' in filename:
#         if len(hBN_10) < limit:
#             hBN_10.append(filename)

#     elif 'M5' in filename:
#         if len(hBN_5) < limit:
#             hBN_5.append(filename)



# Evaluate Images
colors_by_layer = {
    '0-10': np.array([0,163,255])/255.0, # Blue
    '10-20': np.array([29,255,0])/255.0, # Green
    '20-30': np.array([198,22,22])/255.0, # Red
    '30-40': np.array([255,165,0])/255.0, # Orange
    '40+': np.array([152,7,235])/255.0, # Purple
    'dirt': np.array([0, 0, 0])/255.0, # Uncolored
    'bg': np.array([0, 0, 0])/255.0, # Uncolored
}
grow = 1/2

folders = [
    ("/Users/mayanksengupta/Desktop/hBN/Images/M20/", "/Users/mayanksengupta/Desktop/hBN/Results/M20/", 20),
    # ("/Users/mayanksengupta/Desktop/hBN/Images/M10/", "/Users/mayanksengupta/Desktop/hBN/Results/M10/", 10),
    # ("/Users/mayanksengupta/Desktop/hBN/Images/M5/", "/Users/mayanksengupta/Desktop/hBN/Results/M5/", 5),
]

for img_dest_folder, result_dest_folder, mag in folders:
    for filename in tqdm(os.listdir(img_dest_folder)):
        try:
            img = cv2.imread(img_dest_folder+filename)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (int(img.shape[1]*grow), int(img.shape[0]*grow)))

            segmenter = Segmenter(img, hBN, colors=colors_by_layer, magnification=mag, min_area=50, k=3)
            segmenter.process_frame()
            result = segmenter.prettify()
            result = (255 * result).astype('uint8')
            result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

            cv2.imwrite(result_dest_folder+filename, result)

        except Exception as e:
            print(e)
