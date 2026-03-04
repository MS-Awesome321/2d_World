import cv2
import numpy as np
import sys
import os
from segmenter import Segmenter
from material import wte2, graphene
import matplotlib.pyplot as plt
from utils import get_mag
from tqdm import tqdm
import pickle
import argparse

parser = argparse.ArgumentParser(description="Cluster Material Data")
parser.add_argument(
        'material', 
        help='wte2 or graphene',
)
args = parser.parse_args()


point_list = []
label_list = []
sizes_list = []
fnames = []
coord_list = []
mask_ids = []
binary_masks = []

if args.material == 'wte2':
    bg_lab = wte2.target_bg_lab
    mat = wte2
    d_name = 'pv_wte2_5k.pkl'
    target_dir = "/Users/mayanksengupta/Desktop/WTe2_M100"
elif args.material == 'graphene':
    bg_lab = graphene.target_bg_lab
    mat = graphene
    d_name = 'pv_graphene_5k.pkl'
    target_dir = "/Users/mayanksengupta/Desktop/monolayerGraphene/monolayer_Graphene"
else:
    raise ValueError("Invalid Material")

for filename in tqdm(os.listdir(target_dir)):
    img = cv2.imread(f'{target_dir}/{filename}')
    if img is None:
        continue

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if args.material == 'wte2':
        h, w = img.shape[0]//4, img.shape[1]//4
        img = img[h:-h, w:-w]
    elif args.material == 'graphene':
        grow = 1/2
        img = cv2.resize(img, (int(img.shape[1]*grow), int(img.shape[0]*grow)))

    min_area = 5_000
    max_area = 1_000_000
    segmenter = Segmenter(img, mat, magnification=get_mag(filename), min_area=min_area, k=3, surround_bg=True)
    segmenter.process_frame()

    for mask_num in range(1, segmenter.num_masks):
        area = segmenter.mask_areas[mask_num]
        if area > min_area and area < max_area and segmenter.mask_labels[mask_num] and segmenter.mask_labels[mask_num]!='black':
            point_list.append(segmenter.avg_labs[mask_num])
            label_list.append(segmenter.mask_labels[mask_num])
            sizes_list.append(area)
            fnames.append(filename)
            coord_list.append(segmenter.mask_coords(mask_num))
            mask_ids.append(mask_num)
            binary_masks.append(segmenter.masks == mask_num)

points = np.stack(point_list, axis=0)
sizes = np.array(sizes_list)
labels = np.array(label_list)


data = {"avg_labs": points, "labels":labels, "sizes":sizes, "raw_points":point_list, "raw_labels":label_list, "raw_sizes":sizes_list, "names":fnames, "coords": coord_list, "mask_ids":mask_ids, "masks":binary_masks}
with open("pv_graphene_5k.pkl", "wb") as file:
    pickle.dump(data, file)

# with open("pv_data.pkl", "rb") as file:
#     data = pickle.load(file)

# points = data["avg_labs"]
# labels = data["labels"]

fig, axs = plt.subplots(1, 2, figsize=(12, 8), subplot_kw={'projection': '3d'})
for ax in axs:
    ax.set_xlabel("L")
    ax.set_ylabel("A")
    ax.set_zlabel("B")
    ax.view_init(elev=30, azim=-130, roll=0)

types = ["monolayer", "bilayer", "trilayer", "fewlayer", "bulk", "bg", "dirt"]
label_colors = ['blue', 'green', 'red', 'orange', 'purple', 'magenta', 'yellow']

print(np.unique(labels))

for layer_type, color in zip(types, label_colors):
    plot_points = points[labels == layer_type]
    axs[0].scatter(plot_points[:, 0], plot_points[:, 1], plot_points[:, 2], alpha=0.05, color=color)

axs[1].scatter(points[:,0], points[:,1], points[:,2], alpha=0.05)

for ax in axs:
    ax.scatter(bg_lab[0], bg_lab[1], bg_lab[2], color="black", marker="*", label="BG Lab", s=100)
    ax.legend()

plt.show()
