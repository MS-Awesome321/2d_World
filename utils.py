import time
import numpy as np
from skimage.color import lab2rgb, rgb2gray, rgb2lab
from skimage.morphology import disk

def lab_separate(img, l_factor = 1, l_midpoint=50, a_factor = 1, a_midpoint=50, b_factor = 1, b_midpoint = 50):
    lab = rgb2lab(img)
    lab[:,:,0] = lab[:,:,0] + l_factor*(lab[:,:,0] - l_midpoint*np.ones_like(lab[:,:,0]))
    lab[:,:,1] = lab[:,:,1] + a_factor*(lab[:,:,1] - a_midpoint*np.ones_like(lab[:,:,1]))
    lab[:,:,2] = lab[:,:,2] + b_factor*(lab[:,:,2] - b_midpoint*np.ones_like(lab[:,:,2]))
    over = lab[:,:,0] > 100
    under = lab[:,:,0] < 0
    lab[:,:,0][over] = 100
    lab[:,:,0][under] = 0
    return lab2rgb(lab)

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

class Stopwatch():
    def __init__(self):
        self.prev = None

    def clock(self):
        if type(self.prev) == type(None):
            self.prev = time.time()
        else:
            current = time.time()
            print(current - self.prev)
            self.prev = current

def focus_disk(img, radius=200, invert=False):
    d = disk(radius)
    d = d[radius - img.shape[0]//2 : radius + img.shape[0]//2, :]
    pad = np.zeros((img.shape[0], img.shape[1]//2 - radius))
    d = np.concatenate([d, pad], axis=1)
    d = np.concatenate([pad, d], axis=1)  
    d = d[:, 0:img.shape[1]]

    if invert:
        return np.logical_not(d)
    else:
        return d