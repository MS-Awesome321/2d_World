from PIL import Image
import numpy as np
from material import GrapheneEdgeMethod, lab_separate
from skimage.morphology import area_closing, binary_closing, closing, label
from skimage.feature import canny, peak_local_max
from scipy.ndimage import gaussian_filter, distance_transform_edt, label, maximum_filter, gaussian_gradient_magnitude
from skimage.filters import sobel, farid, scharr, prewitt, gabor, roberts
from skimage.filters.rank import entropy
from skimage.morphology import disk, white_tophat, black_tophat
from skimage.color import lab2rgb, rgb2gray, rgb2lab
import skimage.restoration as restoration
from skimage.segmentation import watershed
import matplotlib.pyplot as plt
import cv2
import warnings
import sys
import os
from material import EntropyEdgeMethod

warnings.simplefilter('ignore', UserWarning)

def lab_correct(lab_img, current_avg_lab, target_avg_lab=[55.96122403, 28.28108621, -3.12392236]):
  result = np.ones_like(lab_img)
  result[:,:,0] = lab_img[:,:,0] - (current_avg_lab[0] - target_avg_lab[0])*np.ones_like(lab_img[:,:,0])
  result[:,:,1] = lab_img[:,:,1] - (current_avg_lab[1] - target_avg_lab[1])*np.ones_like(lab_img[:,:,1])
  result[:,:,2] = lab_img[:,:,2] - (current_avg_lab[2] - target_avg_lab[2])*np.ones_like(lab_img[:,:,2])
  return result

def rgb_lab_correct(img, current_avg_lab, target_avg_lab=[55.96122403, 28.28108621, -3.12392236]):
  return lab2rgb(lab_correct(rgb2lab(img), current_avg_lab, target_avg_lab))

# g1_PIL = Image.open('../monolayerGraphene/monolayer_Graphene/24-04-03_GR181_Flake3_M100_BoLeft_0.5B0.9L_.JPG')
# g1_PIL = Image.open('../monolayerGraphene/monolayer_Graphene_Labeled/Inputs/5.jpg')
# g1_from_PIL = np.array(g1_PIL)
# print(g1_from_PIL)
# print(g1_from_PIL.dtype)
# print(np.max(g1_from_PIL))
# print(np.min(g1_from_PIL))
# print(g1_from_PIL.shape)

# for i in range(4):
#     next(mono_graphene_iter)
# g1_from_iter = next(mono_graphene_iter)['image']
# print(g1_from_iter)
# print(g1_from_iter.dtype)
# print(np.max(g1_from_iter))
# print(np.min(g1_from_iter))
# print(g1_from_iter.shape)

# plt.imshow(GrapheneEdgeMethod()(g1_from_iter))
# plt.show()

image_path = os.listdir("../monolayerGraphene/monolayer_Graphene/")[int(sys.argv[1])]
g1 = cv2.imread(f'../monolayerGraphene/monolayer_Graphene/{image_path}')
g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)

def sobel_advanced(img):
    e0 = farid(rgb2gray(lab_separate(img, l_factor=2, a_factor=1.5, b_factor=2, l_midpoint=50, a_midpoint=50, b_midpoint=-100)))
    e1 = farid(rgb2gray(lab_separate(img, l_factor=2, l_midpoint=60)))
    e2 = farid(rgb2gray(lab_separate(img, a_factor=1.5, a_midpoint=50)))
    e3 = farid(rgb2gray(lab_separate(img, b_factor=2, b_midpoint=-100)))
    # e2 = sobel(rgb2gray(lab_separate(img, 2, l_midpoint=50)))
    # e2b = sobel(rgb2gray(lab_separate(img, 2, l_midpoint=60)))
    # e2total = np.multiply(e2, e2b)
    # combined = np.add(e1_5, e2total)
    # combined = np.add(combined, e1)
    return np.pow(np.abs(e0) + np.abs(e1) + np.abs(e2) + np.abs(e3), 1.75)

edges = farid(rgb2gray(g1))
edges = edges/np.max(edges)
# edges = (edges/np.max(edges))
# edges = (10000*edges)
# ret3,th3 = cv2.threshold(edges,0,255, cv2.THRESH_OTSU)
# print(ret3)
# blurred = gaussian_filter(edges, sigma=3)

# kernel = np.array(
#         [[1,1,1], 
#          [1,0,1], 
#          [1,1,1]]
#     )
# eroded1 = cv2.filter2D(edges, -1, kernel)

def make_masks(edges, threshold=90):
    cutoff = np.percentile(cleaned, threshold)
    filled_map = edges > cutoff
    # filled_map = filled_map.astype('float32')
    # filled_map = area_closing(filled_map, area_threshold = self.min_area)
    filled_map = np.logical_not(filled_map)
    masks = label(filled_map, connectivity=1)
    return masks

def threshold_clip(img, threshold=90):
    cutoff = np.percentile(img, threshold)
    return img > cutoff

# kernel = np.array(
#         [[0,0,0,0,1,0,0,0,0],
#          [0,0,0,1,1,1,0,0,0],
#          [0,0,1,1,1,1,1,0,0],
#          [0,1,1,1,1,1,1,1,0],
#          [1,1,1,1,1,1,1,1,1],
#          [0,1,1,1,1,1,1,1,0],
#          [0,0,1,1,1,1,1,0,0],
#          [0,0,0,1,1,1,0,0,0],
#          [0,0,0,0,1,0,0,0,0]]
#     )

kernel = np.array(
        [[0,0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0,0],
         [0,0,1,1,1,1,1,0,0],
         [0,0,1,1,1,1,1,0,0],
         [0,0,1,1,1,1,1,0,0],
         [0,0,1,1,1,1,1,0,0],
         [0,0,1,1,1,1,1,0,0],
         [0,0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0,0],]
    )

# kernel = np.array(
#         [[0,0,0,0,1,1,1,1,1],
#          [0,0,0,1,1,1,1,1,0],
#          [0,0,1,1,1,1,1,0,0],
#          [0,1,1,1,1,1,0,0,0],
#          [1,1,1,1,1,0,0,0,0],
#          [0,1,1,1,1,1,0,0,0],
#          [0,0,1,1,1,1,1,0,0],
#          [0,0,0,1,1,1,1,1,0],
#          [0,0,0,0,1,1,1,1,1],]
#     )

k = 4
expanded = cv2.resize(g1, (k*g1.shape[1], k*g1.shape[0]))
entropied = entropy(rgb2gray(expanded), disk(3))
entropied = (entropied/np.max(entropied))
cleaned = np.pow(entropied, 2.5)
cleaned = cleaned/np.max(cleaned)
# cleaned = (255*cleaned).astype('uint8')
blur_cleaned = gaussian_filter(cleaned, 5)
# blur_cleaned[blur_cleaned < 10] = 0

def e_function(input, k = 2.5):
    result = np.exp(k*input) - np.ones_like(input)
    result /= np.exp(k) - 1
    return result

def shifted_sigmoid(input, k = -5, a = 0.5):
    result = np.ones_like(input) + k*(input - a*np.ones_like(input))
    return np.pow(result, -1)

kernel = np.array(
        [[0,0,0], 
         [0,0,0], 
         [0,0,1]]
    )
filtered1 = cv2.filter2D(entropied, -1, kernel)
filtered1 = cv2.filter2D(filtered1, -1, kernel)
filtered1 = cv2.filter2D(filtered1, -1, kernel)
filtered1 = cv2.filter2D(filtered1, -1, kernel)
kernel = np.array(
        [[0,0,1], 
         [0,0,0], 
         [0,0,0]]
    )
filtered2 = cv2.filter2D(entropied, -1, kernel)
filtered2 = cv2.filter2D(filtered2, -1, kernel)
filtered2 = cv2.filter2D(filtered2, -1, kernel)
filtered2 = cv2.filter2D(filtered2, -1, kernel)
kernel = np.array(
        [[1,0,0], 
         [0,0,0], 
         [0,0,0]]
    )
filtered3 = cv2.filter2D(entropied, -1, kernel)
filtered3 = cv2.filter2D(filtered3, -1, kernel)
filtered3 = cv2.filter2D(filtered3, -1, kernel)
filtered3 = cv2.filter2D(filtered3, -1, kernel)
kernel = np.array(
        [[0,0,0], 
         [0,0,0], 
         [1,0,0]]
    )
filtered4 = cv2.filter2D(entropied, -1, kernel)
filtered4 = cv2.filter2D(filtered4, -1, kernel)
filtered4 = cv2.filter2D(filtered4, -1, kernel)
filtered4 = cv2.filter2D(filtered4, -1, kernel)
# filtered = cv2.filter2D(filtered, -1, kernel)

shift_filtered = entropied * (filtered1 + filtered2 + filtered3 + filtered4)

# eroded = cv2.erode(cleaned, np.ones((3,3), np.uint8))

print(np.unique(entropied.astype('int')))

def get_coords(edge_map, size=3):
    distance = maximum_filter(-edge_map, size=size)
    coords = peak_local_max(distance, footprint=np.ones((3, 3)), min_distance=10)
    return distance, coords

def watershed_segment(edge_map, size=3):
    distance, coords = get_coords(edge_map, size=size)
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers, _ = label(mask)
    labels = watershed(-distance, markers)
    return labels

fig, axs = plt.subplots(2, 2, figsize=(10,10))

axs[0,0].imshow(g1, cmap='inferno')
axs[0,0].axis('off')

# edges[edges<0.1] = 0
cleaned[blur_cleaned > 0.3] = 0
axs[0,1].imshow(cleaned, cmap='inferno')
axs[0,1].axis('off')

# edges = edges > 1
# blurred[blurred<0.1] = 0

def refine(input):
    return maximum_filter(input, size=1, mode='nearest')

def staged_refine(input, num):
    kernel = np.array(
        [[1, 1, 1],
        [1, 9, 1],
        [1, 1, 1]]
    )
    for i in range(num):
        input = refine(input)
        input /= np.max(input)
        input[input < 0.2] = 0
        # input = cv2.filter2D(input, -1, kernel=kernel)
    return input

def rgb2gray_custom(image):
    return 0.25*image[:,:,0] + 0.25*image[:,:,1] + 0.5*image[:,:,2]

def magnitude(input):
    return np.sqrt(np.pow(input[:,:,0], 2) + np.pow(input[:,:,1], 2) +np.pow(input[:,:,2], 2))

first_derivative = gaussian_gradient_magnitude(rgb2lab(g1) [:,:,0], 1)
first_derivative /= np.max(first_derivative)

def hessian_determinant(image, sigma=1):
    """
    Calculate the determinant of the Hessian matrix at each point in the image.
    Args:
        image: 2D numpy array (grayscale image)
        sigma: Gaussian smoothing parameter
    Returns:
        det_H: 2D numpy array of the same shape as image
    """
    # Second derivatives
    Ixx = gaussian_filter(image, sigma=sigma, order=(2, 0))
    Iyy = gaussian_filter(image, sigma=sigma, order=(0, 2))
    Ixy = gaussian_filter(image, sigma=sigma, order=(1, 1))
    # Determinant of Hessian
    det_H = Ixx * Iyy - Ixy ** 2
    return det_H

second_derivative = hessian_determinant(blur_cleaned, sigma=0.25)
second_derivative[second_derivative<0] = 0
# result = np.logical_and(np.abs(first_derivative) < 0.07, second_derivative > 20)

# second_derivative[second_derivative<10] = 0
cleaned = cv2.resize(cleaned, first_derivative.shape[::-1])
final_edges = first_derivative + 1.5*cleaned
result, _ = label(final_edges < 0.1)



axs[1,0].imshow(final_edges, cmap='inferno')
axs[1,0].axis('off')


axs[1,1].imshow(result, cmap='inferno')
axs[1,1].axis('off')

plt.tight_layout()
plt.show()