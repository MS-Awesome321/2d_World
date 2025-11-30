import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
import os
from segmenter2 import Segmenter
from material import graphene, hBN
import warnings
from utils import Stopwatch, focus_disk, blur
from skimage.exposure import adjust_gamma
from skimage.morphology import disk

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

# colors_by_layer = {
#     '0-10': np.array([0,163,255])/255.0, # Blue
#     '10-20': np.array([29,255,0])/255.0, # Green
#     '20-30': np.array([198,22,22])/255.0, # Red
#     '30-40': np.array([255,165,0])/255.0, # Orange
#     '40+': np.array([152,7,235])/255.0, # Purple
#     'dirt': np.array([255, 255, 0])/255.0, # Yellow
#     'bg': np.array([0, 0, 0])/255.0, # Uncolored
# }

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
    blur_factor = 3
elif 'M20' in filename:
    magnification = 20
    segment_edges = False
    blur_factor = 0
elif 'M10' in filename:
    magnification = 10
    segment_edges = False
    blur_factor = 0
elif 'M5' in filename:
    magnification = 5
    segment_edges = False
    blur_factor = 0
else:
    magnification = 20
    segment_edges = False
    rad = 425
    blur_factor = 1

current_dir = os.path.dirname(os.path.abspath(__file__))
g1 = cv2.imread(f'{current_dir}/{filename}')
# g1 = cv2.imread(f'/Users/mayanksengupta/Desktop/monolayerGraphene/monolayer_Graphene/24-08-21_Gr4_Flake2_M100_BoLeft_8x4y_.JPG')
g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)
grow = 1/2
g1 = cv2.resize(g1, (int(g1.shape[1]*grow), int(g1.shape[0]*grow)))
g1 = blur(g1, blur_factor)
# g1 = adjust_gamma(g1, 2, 1)
# rad *= grow
# rad = int(rad)
# f = focus_disk(g1, rad, invert=True)
# f2 = focus_disk(g1, rad - 10, invert=True)

# Initialize Segmenter
watch.clock()
# segmenter = Segmenter(g1, graphene, colors=colors_by_layer, magnification=magnification, min_area=50, focus_disks=[(f, rad), (f2, rad - 10)], k=3)
segmenter = Segmenter(g1, graphene, colors=colors_by_layer, magnification=magnification, min_area=50, k=3)
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

write_result = (255 * result).astype(np.uint8)
write_result = cv2.cvtColor(write_result, cv2.COLOR_RGB2BGR)
cv2.imwrite(f'{current_dir}/segmented_{os.path.basename(filename)}', write_result)

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
    col = int(x + 0.5)
    row = int(y + 0.5)
    z = segmenter.masks[row, col]
    return f'x={col}, y={row}, mask_num={z}'

def format_coord_lab(x, y):
    col = int(x + 0.5)
    row = int(y + 0.5)
    lab = segmenter.lab[row, col]
    return f'x={col}, y={row}, LAB={lab}'

axs[0,0].imshow(g1, cmap='inferno')
axs[0,0].axis('off')
axs[0,0].format_coord = format_coord_lab

axs[0,1].imshow(result, cmap='inferno')
axs[0,1].axis('off')
axs[0,1].format_coord = format_coord

if i is not None and i <= segmenter.num_masks:
    centroid = segmenter.mask_coords(i)
    print(centroid)
    axs[1,1].scatter(*centroid[::-1])

axs[1,0].imshow(segmenter.masks, cmap='inferno')
axs[1,0].axis('off')
axs[1,0].format_coord = format_coord

# watch.clock()

# blurred = blur(segmenter.lab, 2)

# mag = np.zeros_like(blurred[:,:,0]).astype('float64')

# for i in range(3):
#     grad_x = cv2.Sobel(blurred[:,:,i].astype(np.float32), cv2.CV_64F, 1, 0, ksize=5)
#     grad_y = cv2.Sobel(blurred[:,:,i].astype(np.float32), cv2.CV_64F, 0, 1, ksize=5)
#     mag += np.pow(grad_x, 2) + np.pow(grad_y, 2)
# mag = np.pow(mag, 2**(-2))

# footprint = np.ones((5,5))
# mag = cv2.dilate(mag, footprint, iterations=1)
# mag = cv2.erode(mag, footprint, iterations=1)

# threshold = 9.5
# mag[mag<=threshold] = 0

# if magnification < 20:
#     footprint = disk(4)
#     mag -= cv2.erode(mag, footprint, iterations=1)

# mag[mag<=threshold-1] = 0

axs[1,1].imshow(segmenter.edges, cmap='inferno')
# axs[1,1].scatter(points[:, 1], points[:, 0])
axs[1,1].axis('off')
axs[1,1].format_coord = format_coord

plt.show()