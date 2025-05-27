import cv2
from time import time
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage.morphology import disk
from skimage.filters.rank import entropy
from scipy.ndimage import label
import warnings
import concurrent.futures

warnings.simplefilter('ignore', UserWarning)

def subdivide(image, n):
    """
    Splits the input image into n^2 equal subsections.

    Args:
        image (np.ndarray): Input image (2D or 3D array).
        n (int): Number of subdivisions per axis.

    Returns:
        list: A list of n^2 image subsections (as numpy arrays).
    """
    h, w = image.shape[:2]
    h_step = h // n
    w_step = w // n
    sections = []
    for i in range(n):
        for j in range(n):
            section = image[i*h_step:(i+1)*h_step, j*w_step:(j+1)*w_step]
            sections.append(section)
    return sections

def combine_sections(sections, n):
    """
    Combines a list of n^2 image subsections into the original image.

    Args:
        sections (list): List of n^2 numpy arrays (subsections).
        n (int): Number of subdivisions per axis.

    Returns:
        np.ndarray: The reconstructed image.
    """
    # Get the shape of each subsection
    h_sub, w_sub = sections[0].shape[:2]
    # Determine if image is grayscale or color
    if sections[0].ndim == 3:
        channels = sections[0].shape[2]
        image = np.zeros((n * h_sub, n * w_sub, channels), dtype=sections[0].dtype)
    else:
        image = np.zeros((n * h_sub, n * w_sub), dtype=sections[0].dtype)
    # Place each section in the correct position
    idx = 0
    for i in range(n):
        for j in range(n):
            image[i*h_sub:(i+1)*h_sub, j*w_sub:(j+1)*w_sub] = sections[idx]
            idx += 1
    return image


# Subdivide and parallerl process entropy of image
if __name__ == '__main__':
    image_path = os.listdir("../monolayerGraphene/monolayer_Graphene/")[int(sys.argv[1])]
    g1 = cv2.imread(f'../monolayerGraphene/monolayer_Graphene/{image_path}')
    g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)
    shrink = 2.5
    g1 = cv2.resize(g1, (int(g1.shape[1]/shrink), int(g1.shape[0]/shrink)))

    input = rgb2gray(g1)
    n = 3
    sections = subdivide(input, n)
    footprint = disk(15)

    check1 = time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(entropy, section, footprint) for section in sections]
        entropied_sections = [f.result() for f in futures]
    
    check2 = time()
    print(check2 - check1)

    entropied = combine_sections(entropied_sections, n)
    entropied = (entropied/np.max(entropied))
    entropied = np.pow(entropied, 2.5)

    
    masks, num_masks = label(entropied < 0.09)
    print(num_masks)
    plt.imshow(masks, cmap='inferno')
    plt.show()