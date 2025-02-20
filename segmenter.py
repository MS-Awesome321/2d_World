from skimage.transform import resize, downscale_local_mean
from skimage.morphology import area_closing, binary_closing, closing, label
from skimage.color import lab2rgb, rgb2gray, rgb2lab
from skimage.segmentation import flood_fill
from scipy.ndimage import gaussian_filter, shift, binary_erosion, distance_transform_edt, binary_fill_holes
from skimage.filters import sobel, farid, scharr, prewitt, gabor, roberts
from skimage.feature import canny, peak_local_max
from skimage.segmentation import watershed
from skimage.exposure import adjust_gamma
from tqdm import tqdm
from copy import deepcopy
from material import Material, wte2
import numpy.ma as ma
import numpy as np

class Segmenter():
  def __init__(self, img, material=wte2, size = (560, 840), magnification = None, mask_colors = {}, mask_numbers = {}):
    if len(size) != 2:
      raise ValueError("Received size: "+str(size)+". Expected 2 dimensions.")

    self.size = size

    if img.shape[:2] != self.size:
      raise ValueError("Incorrect image size")

    if type(magnification) != type(None):
      self.set_magnification(magnification)


    self.mask_colors = mask_colors
    self.mask_numbers = mask_numbers
    self.l_separation_factor = material.recommended_l_factor
    self.l_midpoint = material.recommended_l_midpoint
    self.img = img
    self.canny_sigma = material.recommended_canny_sigma
    self.num_segments = 0
    self.tolerance = 0
    self.sigma = material.recommended_sigma
    self.fat_threshold = material.recommended_fat_threshold
    self.shift_multiplier = 48 #for images take through circular lens
    self.masks = []
    self.mask_labels = {}
    self.mask_areas = []
    self.edge_mode = material.recommended_edge_mode
    self.max_area = 15000
    self.min_area = 5
    self.interest_lightness_range = 15
    self.lab = rgb2lab(self.img)
    self.gamma = 0.5
    self.gain = 1

    self.target_lab = deepcopy(material.target_bg_lab)
    self.layer_labels = deepcopy(material.layer_labels)

  def adjust_layer_labels(self):
    self.avg_bg_lab = self.get_lab(self.bg_mask_id)

    adjustment_factor = self.avg_bg_lab - np.array(self.target_lab)
    for key, value in self.layer_labels.items():
      new_value = value + adjustment_factor
      self.layer_labels[key] = new_value
    # Add bg lab
    self.layer_labels['bg'] = self.avg_bg_lab

  def set_magnification(self, mag, max_area=1600, min_area = 1, units='um'):
    self.magnification = mag
    pixel_per_um = (6720.0 / 255.0) * (mag / 100.0)
    og_area = 4480 * 6720
    current_area = self.size[0] * self.size[1]
    max_area = max_area * (pixel_per_um ** 2) * (current_area/og_area)
    min_area = min_area * (pixel_per_um ** 2) * (current_area/og_area) * 0.7

    self.max_area = int(max_area)
    self.min_area = int(min_area)

    return self.max_area, self.min_area

  def l_separate(self, factor, midpoint=50):
    lab = rgb2lab(self.img)
    lab[:,:,0] = lab[:,:,0] + factor*(lab[:,:,0] - midpoint*np.ones_like(lab[:,:,0]))
    over = lab[:,:,0] > 100
    under = lab[:,:,0] < 0
    lab[:,:,0][over] = 100
    lab[:,:,0][under] = 0
    self.l_separated = lab2rgb(lab)
    return self.l_separated

  def get_edges(self, mode='normal', factor = 0, midpoint=0):
    if mode == 'normal':
      edges = canny(rgb2gray(self.img), sigma=self.canny_sigma).astype('float32')
    elif mode == 'sensitive':
      if factor==0:
        factor = self.l_separation_factor
      if midpoint==0:
        midpoint = self.l_midpoint
      self.l_separate(factor, midpoint)
      edges = canny(rgb2gray(self.l_separated), sigma=self.canny_sigma).astype('float32')
    else:
      raise ValueError("Invalid Mode: "+mode)

    shift_factor = self.sigma * self.shift_multiplier * (self.img.shape[1]//840)
    temp_black = np.logical_or(shift(self.black_zone.astype('int8'), (0,shift_factor)), shift(self.black_zone.astype('int8'), (0,-shift_factor)))
    self.black_zone = np.logical_or(self.black_zone, temp_black)

    edges[self.black_zone] = 0
    self.edges = edges.astype('float32')
    self.black_edges = sobel(self.black_zone.astype('int8')).astype('bool')
    self.edges = np.logical_or(self.edges, self.black_edges).astype('float32')

    fat_edges = gaussian_filter(self.edges, sigma=self.sigma)
    self.fat_edges = fat_edges > self.sigma*self.fat_threshold

    return self.edges, self.fat_edges

  def make_masks(self, mode='advanced', bg_mode='normal'):
    if mode=='simple':
      filled_map = self.edges
      filled_map = filled_map.astype('float32')
      filled_map = area_closing(filled_map, area_threshold = self.min_area)
      filled_map = np.logical_not(filled_map)

      self.masks, self.num_masks = label(filled_map, connectivity=1, return_counts=True)

      self.mask_ids, mask_areas = np.unique(self.masks, return_counts=True)
      self.mask_areas = {self.mask_ids[i]: mask_areas[i] for i in range(len(self.mask_ids))}

      return filled_map

    elif mode=='watershed':
      filled_map = np.logical_not(self.edges)
      distance = distance_transform_edt(filled_map)
      coords = peak_local_max(distance, footprint=np.ones((3, 3)), labels=filled_map)
      mask = np.zeros(distance.shape, dtype=bool)
      mask[tuple(coords.T)] = True
      markers, _ = label(mask)

      self.masks = watershed(-distance, markers, mask=filled_map)

      self.mask_ids, mask_areas = np.unique(self.masks, return_counts=True)
      self.mask_areas = {self.mask_ids[i]: mask_areas[i] for i in range(len(self.mask_ids))}
      self.num_masks = len(self.mask_ids)

      return filled_map

    elif mode=='advanced':
      filled_map = np.logical_not(self.edges)
      distance = distance_transform_edt(filled_map)
      coords = peak_local_max(distance, footprint=np.ones((3, 3)), labels=filled_map)
      mask = np.zeros(distance.shape, dtype=bool)
      mask[tuple(coords.T)] = True
      markers = label(mask)

      self.raw_masks = watershed(-distance, markers, mask=filled_map, watershed_line=True)

      watershed_edges = self.raw_masks == 0
      self.corrected_edges = np.logical_and(watershed_edges, self.fat_edges)

      self.unlabeled_masks = np.logical_not(self.corrected_edges).astype('int8')
      self.masks, self.num_masks = label(self.unlabeled_masks, connectivity=1, return_num=True)

      self.masks = self.masks + np.ones_like(self.masks)
      self.masks[self.black_zone] = 0
      self.masks[self.black_edges] = 0
      self.masks[self.edges.astype('bool')] = 0

      self.mask_ids, mask_areas = np.unique(self.masks, return_counts=True)
      self.mask_ids = self.mask_ids[2:]
      mask_areas = mask_areas[2:]
      self.mask_areas = {self.mask_ids[i]: mask_areas[i] for i in range(len(self.mask_ids))}

      if bg_mode=='normal':
        self.bg_mask_id = max(self.mask_areas, key=self.mask_areas.get)
        self.bg_mask = self.masks == self.bg_mask_id
      elif bg_mode=='assume':
        min_dist = 100
        min_id = 0
        sorted_areas = np.argsort(self.mask_areas.values())
        for i in range(5):
          bg_mask_id = max(self.mask_areas, key=self.mask_areas.get)
          lab = self.get_lab(bg_mask_id)
          dist = np.linalg.norm(lab - self.target_lab)
          if dist < min_dist:
            min_dist = dist
            min_id = bg_mask_id
          self.mask_areas[bg_mask_id] *= -1
            
        self.bg_mask_id = min_id
        self.bg_mask = self.masks == self.bg_mask_id

        for i in range(5):
          bg_mask_id = min(self.mask_areas, key=self.mask_areas.get)
          self.mask_areas[bg_mask_id] *= -1
      else:
        raise ValueError("Invalid Mode: "+bg_mode)
      return filled_map

    else:
      raise ValueError("Invalid Mode: "+mode)

  def get_black_zone(self):
    self.black_zone = self.lab[:,:,0] < 7
    return self.black_zone

  def get_lab(self, i, mode='mean'):
    mask = self.masks == i

    if mode=='mean':
      avg_lightness = np.sum(self.lab[:,:,0][mask]) / self.mask_areas[i]
      avg_A = np.sum(self.lab[:,:,1][mask]) / self.mask_areas[i]
      avg_B = np.sum(self.lab[:,:,2][mask]) / self.mask_areas[i]
      lab = np.array([avg_lightness, avg_A, avg_B])
      return lab

    elif mode=='median':
      mask = np.logical_not(mask)
      masked_l = ma.array(self.lab[:,:,0], mask=mask)
      masked_a = ma.array(self.lab[:,:,1], mask=mask)
      masked_b = ma.array(self.lab[:,:,2], mask=mask)
      med_lightness = ma.median(masked_l)
      med_A = ma.median(masked_a)
      med_B = ma.median(masked_b)
      lab = np.array([med_lightness, med_A, med_B])
      return lab

    else:
      raise ValueError("Invalid Mode: "+mode)

  def make_labels(self, mode='full_lab'):
    self.adjust_layer_labels()

    for i in self.mask_ids:
      lab = self.get_lab(i)

      min_dist = 5000
      #Catch dirt by size
      if self.mask_areas[i] < self.min_area:
        self.mask_labels[i] = 'dirt'
      else:
        for layer_type, base_lab in self.layer_labels.items():
          if mode=='full_lab':
            distance = np.linalg.norm(lab - base_lab)
          elif mode=='lightness':
            distance = np.linalg.norm(lab[0] - base_lab[0])
          else:
            raise ValueError("Invalid Mode: "+mode)
          if distance < min_dist:
            min_dist = distance
            label = layer_type
        self.mask_labels[i] = label

  def go(self, mask_mode='advanced', label_mode='full_lab', edge_mode='', bg_mode='normal'):
    if edge_mode=='':
      edge_mode = self.edge_mode
    self.get_black_zone()
    self.get_edges(mode=edge_mode)
    self.make_masks(mode=mask_mode, bg_mode=bg_mode)
    self.make_labels(mode=label_mode)

  def prettify(self):
    r = np.zeros((self.size[0], self.size[1]))
    g = np.zeros((self.size[0], self.size[1]))
    b = np.zeros((self.size[0], self.size[1]))
    for i in self.mask_ids:
      area = self.mask_areas[i]
      label = self.mask_labels[i]
      if (area > self.min_area and area < self.max_area):
        color = self.mask_colors[label]
      else:
        color = np.array([0,0,0])
      mask = self.masks == i
      r[mask] = color[0]
      g[mask] = color[1]
      b[mask] = color[2]

    self.colored_masks = np.stack([r,g,b], axis=-1)
    return self.colored_masks
  
  def number(self):
    result = np.zeros((self.size[0], self.size[1]))
    for i in self.mask_ids:
      area = self.mask_areas[i]
      label = self.mask_labels[i]
      if (area > self.min_area and area < self.max_area):
        id = self.mask_numbers[label]
      else:
        id = 0
      mask = self.masks == i
      result[mask] = id

    self.numbered_masks = result
    return result