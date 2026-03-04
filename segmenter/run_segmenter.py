import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
import os
from segmenter import Segmenter
from material import graphene, hBN, wte2
import warnings
from utils import Stopwatch, focus_disk, blur
from skimage.exposure import adjust_gamma
from skimage.morphology import disk
from scipy.ndimage import maximum_filter
import argparse
from utils import get_mag

watch = Stopwatch()

warnings.simplefilter('ignore', UserWarning)

parser = argparse.ArgumentParser(description="Segment an image")
parser.add_argument(
        'fname', 
        help='name of file',
)
parser.add_argument(
    "-w",
    help="WTe2",
    action='store_true'
)
parser.add_argument(
    "-g",
    help="Graphene",
    action='store_true'
)
parser.add_argument(
    "-hb",
    help="hBN",
    action='store_true'
)
parser.add_argument(
    '-m',
    metavar='mask_num', 
    help='id num of an individual flake',
    default=0,
    required=False,
    type=int
)
args = parser.parse_args()

arg_sum = args.w + args.g + args.hb
if arg_sum != 1:
    raise ValueError("Select only one material.")

if args.w or args.g:
    colors_by_layer = {
        'monolayer': np.array([0,163,255])/255.0, # Blue
        'bilayer': np.array([29,255,0])/255.0, # Green
        'trilayer': np.array([198,22,22])/255.0, # Red
        'fewlayer': np.array([255,165,0])/255.0, # Orange
        'manylayer': np.array([255,165,0])/255.0, # Orange
        'bulk': np.array([152,7,235])/255.0, # Purple
        'dirt': np.array([255, 255, 0])/255.0, # Yellow
        'bg': np.array([0, 0, 0])/255.0, # Uncolored
        'black': np.array([0, 0, 0])/255.0, # Uncolored
    }

if args.hb:
    colors_by_layer = {
        '0-10': np.array([0,163,255])/255.0, # Blue
        '10-20': np.array([29,255,0])/255.0, # Green
        '20-30': np.array([198,22,22])/255.0, # Red
        '30-40': np.array([255,165,0])/255.0, # Orange
        '40+': np.array([152,7,235])/255.0, # Purple
        'dirt': np.array([0, 0, 0])/255.0, # Uncolored
        'bg': np.array([0, 0, 0])/255.0, # Uncolored
        'black': np.array([0, 0, 0])/255.0, # Uncolored
    }

if args.hb:
    target_dir = "/Users/mayanksengupta/Desktop/hBN/Images"
    mat = hBN
if args.g:
    target_dir = "/Users/mayanksengupta/Desktop/monolayerGraphene/monolayer_Graphene"
    mat = graphene
if args.w:
    target_dir = "/Users/mayanksengupta/Desktop/WTe2_M100"
    mat = wte2

g1 = cv2.imread(f'{target_dir}/{args.fname}')
g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)

# g1 = np.roll(g1, -200, 1)
# g1 = np.roll(g1, -200, 0)

# if args.w:
h, w = g1.shape[0]//4, g1.shape[1]//4
g1 = g1[h:-h, w:-w]
# else:
#     grow = 1/2
#     g1 = cv2.resize(g1, (int(g1.shape[1]*grow), int(g1.shape[0]*grow)))

# Initialize Segmenter
watch.clock()
# segmenter = Segmenter(g1, graphene, colors=colors_by_layer, magnification=magnification, min_area=50, focus_disks=[(f, rad), (f2, rad - 10)], k=3)
segmenter = Segmenter(g1, mat, colors=colors_by_layer, magnification=get_mag(args.fname), min_area=500, k=3, surround_bg=True)
lab = segmenter.lab.copy()
print(segmenter.edge_method.mag)
# watch.clock()
segmenter.make_masks()
# watch.clock()
segmenter.lab_equalize()
# watch.clock()
segmenter.get_all_avg_lab()
# watch.clock()
segmenter.adjust_layer_labels()
# watch.clock()
segmenter.label_masks()
# watch.clock()
result = segmenter.prettify()
watch.clock()

print(g1.shape)
    
if hasattr(args, 'mask_num') and args.mask_num <= segmenter.num_masks:
    print(segmenter.avg_labs[args.mask_num])
    print(segmenter.mask_labels[args.mask_num])
    print(segmenter.mask_areas[args.mask_num])
    print(segmenter.avg_bg_lab)
    for label, layer in segmenter.layer_labels.items():
        print(f'{layer}: {np.stack(label)}')

print(f"Num Masks: {segmenter.num_masks}, Max: {np.max(segmenter.masks)}")

# Show Results
fig, axs = plt.subplots(2, 3, figsize=(10,10), sharex=True, sharey=True)

def format_coord(x, y):
    col = int(x + 0.5)
    row = int(y + 0.5)
    z = segmenter.masks[row, col]
    return f'x={col}, y={row}, mask_num={z}'

def format_coord_lab(x, y):
    col = int(x + 0.5)
    row = int(y + 0.5)
    lab = segmenter.lab[row, col]
    return f'x={col}, y={row}, LAB={lab}'

def format_avg_lab(x, y):
    col = int(x + 0.5)
    row = int(y + 0.5)
    mask_num = segmenter.masks[row, col]
    lab = segmenter.avg_labs[mask_num]
    label = segmenter.mask_labels[mask_num]
    area = segmenter.mask_areas[mask_num]
    return f'x={col}, y={row}, avg_lab={lab}, label={label}, area={area}, mask_num={mask_num}'

axs[0,0].imshow(segmenter.img, cmap='inferno')
axs[0,0].axis('off')
axs[0,0].format_coord = format_coord_lab

axs[0,1].imshow(result, cmap='inferno')
axs[0,1].axis('off')
axs[0,1].format_coord = format_avg_lab

if hasattr(args, 'mask_num') and args.mask_num <= segmenter.num_masks:
    centroid = segmenter.mask_coords(args.mask_num)
    print(centroid)
    axs[1,1].scatter(*centroid[::-1])

axs[1,0].imshow(segmenter.bg_mask, cmap='inferno')
axs[1,0].axis('off')
axs[1,0].format_coord = format_coord

# watch.clock()

axs[1,1].imshow(segmenter.edges, cmap='inferno')
# axs[1,1].scatter(points[:, 1], points[:, 0])
axs[1,1].axis('off')
axs[1,1].format_coord = format_avg_lab

axs[0,2].imshow(segmenter.lab[:,:,0], cmap='inferno')
axs[0,2].scatter(segmenter.interpolation_points[:,1], segmenter.interpolation_points[:,0], s=1)
axs[0,2].axis('off')
axs[1,2].imshow(segmenter.lab[:,:,1], cmap='inferno')
axs[1,2].axis('off')

plt.show()