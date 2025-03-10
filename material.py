from skimage.feature import canny
from skimage.color import lab2rgb, rgb2gray, rgb2lab
import numpy as np

class EdgeMethod():
  def __init__(self, canny_sigma = 0.7):
    self.canny_sigma = canny_sigma
  
  def __call__(self, img):
    return canny(rgb2gray(img), sigma=self.canny_sigma).astype('float32')

def lab_separate(img, l_factor, l_midpoint=50, a_factor = 1, a_midpoint=50, b_factor = 1, b_midpoint = 50):
    lab = rgb2lab(img)
    lab[:,:,0] = lab[:,:,0] + l_factor*(lab[:,:,0] - l_midpoint*np.ones_like(lab[:,:,0]))
    lab[:,:,1] = lab[:,:,1] + a_factor*(lab[:,:,1] - a_midpoint*np.ones_like(lab[:,:,1]))
    lab[:,:,2] = lab[:,:,2] + b_factor*(lab[:,:,2] - b_midpoint*np.ones_like(lab[:,:,2]))
    over = lab[:,:,0] > 100
    under = lab[:,:,0] < 0
    lab[:,:,0][over] = 100
    lab[:,:,0][under] = 0
    return lab2rgb(lab)

class GrapheneEdgeMethod(EdgeMethod):
  def __call__(self, img):
    e1 = canny(rgb2gray(lab_separate(img, l_factor=1.5, a_factor=1, b_factor=2, l_midpoint=50, a_midpoint=-47, b_midpoint=-50)), sigma=1.75)
    e1_5 = canny(rgb2gray(lab_separate(img, 1.5, l_midpoint=50)), sigma=1.4)
    e2 = canny(rgb2gray(lab_separate(img, 2, l_midpoint=50)), sigma=0.5)
    e2b = canny(rgb2gray(lab_separate(img, 2, l_midpoint=60)), sigma=1.4)
    e2total = np.logical_and(e2, e2b)
    combined = np.logical_or(e1_5, e2total)
    combined = np.logical_or(combined, e1)
    return combined

class Material():
  def __init__(self, name, target_bg_lab, layer_labels, sigma=0.7, fat_threshold=0.1, edge_method = EdgeMethod()):
    self.name = name
    self.target_bg_lab = target_bg_lab
    self.layer_labels = layer_labels
    self.recommended_sigma = sigma
    self.recommended_fat_threshold = fat_threshold
    self.edge_method = edge_method




# Make each material

wte2_labels = { # cielab colorspace
                  (56, 40, -10): 'monolayer',
                  (46, 50, -20): 'bilayer',
                  (39, 60, -30): 'trilayer',
                  (31, 54, -32): 'fewlayer',
                  (70, 20, -30): 'manylayer',
                  (80, 5, 10): 'bulk',
                  (0, 0, 0): 'dirt',
                  (30, 20, -10): 'dirt',
              }

wte2 = Material('WTe2', [58.50683594, 28.57762527, -2.79295444], layer_labels=wte2_labels)

graphene_labels = { # cielab colorspace
                  (50, 14, 4): 'monolayer',
                  (48, 17, 3): 'bilayer',
                  (37, 31, -2): 'trilayer',
                  (30, 30, -27): 'fewlayer',
                  (50, 0, -15): 'manylayer',
                  (80, 5, 10): 'bulk',
                  (53, -8, -12): 'bluish_layers',
                  (50, 1, -10): 'bluish_layers',
                  (48.1, 4.7, 10.4): 'dirt',
                  (30, 20, -10): 'dirt',
                  (0,0,0): 'bg'
              }

graphene = Material(
    'Graphene',
    [49.62793933, 12.17574073,  5.43972594],
    layer_labels=graphene_labels,
    sigma=3,
    fat_threshold=0.005,
    edge_method = GrapheneEdgeMethod()
  )


hBN_labels = { # cielab colorspace
                  (37.4, 16.6, -8.3): '0-10',
                  (43.9, 25.6, -64.8): '10-20',
                  (62.2, -11.6, -41.3): '20-30',
                  (72.8, -35, -15.1): '30+',
                  (71.8, -25.5, 0): '35+',
                  # (69.4, -3.5, 50.8): 'bulk',
                  # (53, -8, -12): 'bluish_layers',
                  # (50, 1, -10): 'more_bluish_layers',
                  (30, 20, -10): 'dirt',
              }

hBN = Material(
    'hBN', 
    [39.43335796, 14.2159274,  -4.54227961], 
    layer_labels=hBN_labels, 
    sigma=0.7, 
    fat_threshold=0.1,
    edge_method=GrapheneEdgeMethod(),
  )