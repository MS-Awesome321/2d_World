import cv2
import numpy as np
import os
from segmenter2 import Segmenter
from material import graphene
from tqdm import tqdm
import warnings

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

files = os.listdir("../monolayerGraphene/monolayer_Graphene/")

for filename in tqdm(files):
    if 'M100' in filename:
        magnification = 100
        folder = 'M100'
    elif 'M50' in filename:
        magnification = 50
        folder = 'M50'
    elif 'M20' in filename:
        magnification = 20
        folder = 'M20'
    elif 'M10' in filename:
        magnification = 10
        folder = 'M10'
    elif 'M5' in filename:
        magnification = 5
        folder = 'M5'
    else:
        magnification = 20
        folder = 'M20'

    g1 = cv2.imread(f'../monolayerGraphene/monolayer_Graphene/{filename}')
    g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)
    shrink = 2
    g1 = cv2.resize(g1, (int(g1.shape[1]/shrink), int(g1.shape[0]/shrink)))

    # Initialize Segmenter
    segmenter = Segmenter(g1, graphene, colors=colors_by_layer, magnification=magnification)
    segmenter.process_frame()
    result = segmenter.prettify()
    result = (255 * result).astype(np.uint8)
    result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

    cv2.imwrite(f'/Users/mayanksengupta/Desktop/monolayerGraphene/New_Graphene_Labeled/{folder}/{filename}', result)