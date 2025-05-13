from PIL import Image
import numpy as np
from material import GrapheneEdgeMethod, lab_separate
from skimage.morphology import area_closing, binary_closing, closing, label
from skimage.feature import canny
from scipy.ndimage import gaussian_filter
from skimage.filters import sobel, farid, scharr, prewitt, gabor, roberts
from skimage.filters.rank import entropy
from skimage.morphology import disk
from skimage.color import lab2rgb, rgb2gray, rgb2lab
import skimage.restoration as restoration
import matplotlib.pyplot as plt
import cv2
import warnings
import sys



warnings.simplefilter('ignore', UserWarning)

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


g1 = cv2.imread(f'../monolayerGraphene/monolayer_Graphene_Labeled/Inputs/{sys.argv[1]}.jpg')
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

kernel = np.array(
        [[0,0,0,0,1,0,0,0,0],
         [0,0,0,1,1,1,0,0,0],
         [0,0,1,1,1,1,1,0,0],
         [0,1,1,1,1,1,1,1,0],
         [1,1,1,1,1,1,1,1,1],
         [0,1,1,1,1,1,1,1,0],
         [0,0,1,1,1,1,1,0,0],
         [0,0,0,1,1,1,0,0,0],
         [0,0,0,0,1,0,0,0,0]]
    )

# kernel = np.array(
#         [[0,0,0,0,0,0,0,0,0],
#          [0,0,0,0,0,0,0,0,0],
#          [0,0,1,1,1,1,1,0,0],
#          [0,0,1,1,1,1,1,0,0],
#          [0,0,1,1,1,1,1,0,0],
#          [0,0,1,1,1,1,1,0,0],
#          [0,0,1,1,1,1,1,0,0],
#          [0,0,0,0,0,0,0,0,0],
#          [0,0,0,0,0,0,0,0,0],]
#     )

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
entropied = entropy(rgb2gray(g1), kernel)
# entropied = (entropied/np.max(entropied))
cleaned = np.pow(entropied, 2.5)
cleaned = cleaned/np.max(cleaned)
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

fig, axs = plt.subplots(2, 2, figsize=(10,10))

axs[0,0].imshow(g1, cmap='inferno')
axs[0,0].axis('off')

# edges[edges<0.1] = 0
im = axs[0,1].imshow(entropied, cmap='inferno')
axs[0,1].axis('off')
# fig.colorbar(im)

# edges = edges > 1
# blurred[blurred<0.1] = 0
axs[1,0].imshow(cleaned, cmap='inferno')
axs[1,0].axis('off')

axs[1,1].imshow(cleaned > 0.1, cmap='inferno')
axs[1,1].axis('off')

plt.show()