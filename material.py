import numpy as np

class Material():
  def __init__(self, name, target_bg_lab, layer_labels, sigma=0.7, fat_threshold=0.1, edge_mode='normal', factor=3.5, midpoint=50, canny_sigma=0):
    self.name = name
    self.target_bg_lab = target_bg_lab
    self.layer_labels = layer_labels
    self.recommended_sigma = sigma
    self.recommended_fat_threshold = fat_threshold
    self.recommended_edge_mode = edge_mode
    self.recommended_l_factor = factor
    self.recommended_l_midpoint = midpoint
    self.recommended_canny_sigma = canny_sigma

wte2_labels = { # cielab colorspace
                  'monolayer': np.array([56, 40, -10]),
                  'bilayer': np.array([46, 50, -20]),
                  'trilayer': np.array([39, 60, -30]),
                  'fewlayer': np.array([31, 54, -32]),
                  'manylayer': np.array([70, 20, -30]),
                  'bulk': np.array([80, 5, 10]),
                  'dirt': np.array([30, 20, -10]),
              }

wte2 = Material('WTe2', [58.50683594, 28.57762527, -2.79295444], layer_labels=wte2_labels)

graphene_labels = { # cielab colorspace
                  'monolayer': np.array([50, 14, 4]),
                  'bilayer': np.array([48, 17, 3]),
                  'trilayer': np.array([37, 31, -2]),
                  'fewlayer': np.array([30, 30, -27]),
                  'manylayer': np.array([50, 0, -15]),
                  'bulk': np.array([80, 5, 10]),
                  'bluish_layers': np.array([53, -8, -12]),
                  'more_bluish_layers': np.array([50, 1, -10]),
                  'dirt': np.array([30, 20, -10]),
              }

graphene = Material(
    'Graphene', 
    [49.62793933, 12.17574073,  5.43972594], 
    layer_labels=graphene_labels, 
    sigma=1, 
    fat_threshold=0.02,
    edge_mode='sensitive',
  )