import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
import os
from skimage.morphology import disk
from skimage.filters.rank import entropy
from skimage.color import rgb2gray, lab2rgb, rgb2lab
from scipy.ndimage import gaussian_filter, gaussian_gradient_magnitude, label
from skimage.exposure import adjust_gamma
from segmenter2 import Segmenter
from material import graphene
import warnings
from time import time
from material import EntropyEdgeMethod
from utils import Stopwatch

s = Stopwatch()

warnings.simplefilter('ignore', UserWarning)

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0, # Blue
    'bilayer': np.array([29,255,0])/255.0, # Green
    'trilayer': np.array([198,22,22])/255.0, # Red
    'fewlayer': np.array([255,165,0])/255.0, # Orange
    'manylayer': np.array([255,165,0])/255.0, # Orange
    'bluish_layers': np.array([255,165,0])/255.0, # Orange
    'bulk': np.array([152,7,235])/255.0, # Purple
    'dirt': np.array([0, 0, 0])/255.0, # Yellow
    'more_bluish_layers': np.array([255, 255, 0])/255.0, # Yellow
    'bg': np.array([0, 0, 0])/255.0, # Uncolored
}

image_path = os.listdir("../monolayerGraphene/monolayer_Graphene/")[int(sys.argv[1])]
g1 = cv2.imread(f'../monolayerGraphene/monolayer_Graphene/{image_path}')
g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)
shrink = 2
g1 = cv2.resize(g1, (int(g1.shape[1]/shrink), int(g1.shape[0]/shrink)))

# Initialize Segmenter
s.clock()
segmenter = Segmenter(g1, graphene, colors=colors_by_layer)
s.clock()
segmenter.make_masks()
s.clock()
segmenter.get_all_avg_lab()
s.clock()
segmenter.label_masks()
s.clock()
segmenter.prettify()
s.clock()

# Show Results
fig, axs = plt.subplots(1, 2, figsize=(10,10))

axs[0].imshow(g1, cmap='inferno')
axs[0].axis('off')

axs[1].imshow(segmenter.colored_masks, cmap='inferno')
axs[1].axis('off')

plt.tight_layout()
plt.show()