import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
import os
from segmenter2 import Segmenter
from material import graphene
import warnings
from utils import Stopwatch, focus_disk
from scipy.ndimage import gaussian_filter
from skimage.filters.edges import sobel

watch = Stopwatch()

warnings.simplefilter('ignore', UserWarning)

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0, # Blue
    'bilayer': np.array([29,255,0])/255.0, # Green
    'trilayer': np.array([198,22,22])/255.0, # Red
    'fewlayer': np.array([255,165,0])/255.0, # Orange
    'manylayer': np.array([255,165,0])/255.0, # Orange
    'bulk': np.array([152,7,235])/255.0, # Purple
    'dirt': np.array([255, 255, 0])/255.0, # Yellow
    'bg': np.array([0, 0, 0])/255.0, # Uncolored
}

# image_path = os.listdir("../monolayerGraphene/monolayer_Graphene/")[int(sys.argv[1])]
filename = sys.argv[1]

if 'M100' in filename or 'm100' in filename:
    magnification = 100
    rad = 425
    blur_factor = 3
    segment_edges = False
elif 'M50' in filename:
    magnification = 50
    segment_edges = False
elif 'M20' in filename:
    magnification = 20
    segment_edges = True
elif 'M10' in filename:
    magnification = 10
    segment_edges = True
elif 'M5' in filename:
    magnification = 5
    segment_edges = True
else:
    magnification = 10
    segment_edges = True
    rad = 425
    blur_factor = 0.5

def blur(img, sigma):
    r = gaussian_filter(img[:,:,0], sigma)
    g = gaussian_filter(img[:,:,1], sigma)
    b = gaussian_filter(img[:,:,2], sigma)
    return np.stack([r, g, b], axis=-1)

g1 = cv2.imread(f'C:/Users/admin/Desktop/2d_World/hardware/photo_dir/{filename}')
g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)
grow = 2
g1 = cv2.resize(g1, (int(g1.shape[1]*grow), int(g1.shape[0]*grow)))
g1 = blur(g1, blur_factor)
rad *= grow
rad = int(rad)
f = focus_disk(g1, rad, invert=True)
f2 = focus_disk(g1, rad - 10, invert=True)

# Initialize Segmenter
watch.clock()
segmenter = Segmenter(g1, graphene, colors=colors_by_layer, magnification=magnification, min_area=50, focus_disks=[(f, rad), (f2, rad - 10)], k=3)
print(segmenter.edge_method.mag)
# watch.clock()
segmenter.make_masks(
    segment_edges=segment_edges
)
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

try:
    i = int(sys.argv[2])
except:
    i = None
    
if i is not None and i <= segmenter.num_masks:
    print(segmenter.avg_labs[i])
    print(segmenter.mask_labels[i])
    print(segmenter.mask_areas[i])
    print(segmenter.avg_bg_lab)
    for label, layer in segmenter.layer_labels.items():
        print(f'{layer}: {np.stack(label)}')

print(segmenter.num_masks)

# Show Results
fig, axs = plt.subplots(2, 2, figsize=(10,10))

def format_coord(x, y):
    col = int(x + 0.5) # Round to the nearest integer
    row = int(y + 0.5)
    z = segmenter.masks[row, col]
    return f'x={col}, y={row}, mask_num={z}'

axs[0,0].imshow(g1, cmap='inferno')
axs[0,0].axis('off')
axs[0,0].format_coord = format_coord

axs[0,1].imshow(result, cmap='inferno')
axs[0,1].axis('off')
axs[0,1].format_coord = format_coord

if i is not None and i <= segmenter.num_masks:
    centroid = segmenter.mask_coords(i)
    print(centroid)
    axs[1,1].scatter(*centroid[::-1])

axs[1,0].imshow(segmenter.lab[:,:,0], cmap='inferno')
axs[1,0].axis('off')
axs[1,0].format_coord = format_coord

# watch.clock()
# r = segmenter.direct_lab_label()
# watch.clock()
# r = sobel(np.pow(segmenter.lab[:,:,0], 0.5))
axs[1,1].imshow(segmenter.edges, cmap='inferno')
# axs[1,1].scatter(points[:, 1], points[:, 0])
axs[1,1].axis('off')
axs[1,1].format_coord = format_coord

plt.show()