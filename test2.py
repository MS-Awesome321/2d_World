import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
import os
from segmenter2 import Segmenter
from material import graphene
import warnings
from utils import Stopwatch, focus_disk

watch = Stopwatch()

warnings.simplefilter('ignore', UserWarning)

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0, # Blue
    'bilayer': np.array([29,255,0])/255.0, # Green
    'trilayer': np.array([198,22,22])/255.0, # Red
    'fewlayer': np.array([255,165,0])/255.0, # Orange
    'manylayer': np.array([255,165,0])/255.0, # Orange
    'bluish_layers': np.array([255,165,0])/255.0, # Orange
    'bulk': np.array([152,7,235])/255.0, # Purple
    'dirt': np.array([0, 0, 0])/255.0, # Uncolored
    'more_bluish_layers': np.array([255, 255, 0])/255.0, # Yellow
    'bg': np.array([0, 0, 0])/255.0, # Uncolored
}

# image_path = os.listdir("../monolayerGraphene/monolayer_Graphene/")[int(sys.argv[1])]
filename = sys.argv[1]

if 'M100' in filename:
    magnification = 100
elif 'M50' in filename:
    magnification = 50
elif 'M20' in filename:
    magnification = 20
elif 'M10' in filename:
    magnification = 10
elif 'M5' in filename:
    magnification = 5
else:
    magnification = 20

g1 = cv2.imread(f'../monolayerGraphene/monolayer_Graphene/{filename}')
g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)
shrink = 0.25
g1 = cv2.resize(g1, (int(g1.shape[1]/shrink), int(g1.shape[0]/shrink)))
f = focus_disk(g1, 1150, invert=True)
g1[f] = 0

# Initialize Segmenter
watch.clock()
segmenter = Segmenter(g1, graphene, colors=colors_by_layer, magnification=magnification)
print(segmenter.edge_method.mag)
watch.clock()
segmenter.make_masks()
watch.clock()
segmenter.get_all_avg_lab()
watch.clock()
segmenter.label_masks()
watch.clock()
result = segmenter.prettify()
watch.clock()

# print(segmenter.avg_labs[247])
# print(segmenter.mask_labels[247])
# print(segmenter.mask_areas[247])
# print(segmenter.avg_bg_lab)
# print(segmenter.layer_labels)

# Show Results
fig, axs = plt.subplots(1, 4, figsize=(10,10))

axs[0].imshow(g1, cmap='inferno')
axs[0].axis('off')

axs[1].imshow(result, cmap='inferno')
axs[1].axis('off')

axs[2].imshow(segmenter.edges, cmap='inferno')
axs[2].axis('off')

axs[3].imshow(segmenter.masks, cmap='inferno')
axs[3].axis('off')

plt.tight_layout()
plt.show()