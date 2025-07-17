import cv2
import numpy as np
from scipy.ndimage import label

class Segmenter():
    def __init__(self, img, material, colors=None, numbers=None, min_area = 50, max_area = 10000000, magnification=100, k=3, min_var = 0, max_var = 15):
        self.img = img
        self.size = img.shape[:2]
        self.target_bg_lab = material.target_bg_lab
        self.layer_labels = material.layer_labels
        self.edge_method = material.Edge_Method(k=k, magnification=magnification)
        self.colors = colors
        self.numbers = numbers
        self.min_area = min_area
        self.max_area = max_area
        self.min_var = min_var
        self.max_var = max_var
        
        self.lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.int16)
        self.lab[:,:,0] = self.lab[:,:,0] * 100.0/255.0
        self.lab[:,:,1] -= 128
        self.lab[:,:,2] -= 128

    def make_masks(self, black_zone_mask = None, segment_edges = False):
        self.segment_edges = segment_edges

        self.edges = self.edge_method(self.img)
        if black_zone_mask is not None:
            if segment_edges:
                old_copy = self.edges.copy()
            self.edges[black_zone_mask] = 1
        self.masks, self.num_masks = label(np.logical_not(self.edges))
        self.mask_ids, self.mask_areas = np.unique(self.masks, return_counts=True)

        # Get BG mask
        self.bg_mask_id = np.argmax(self.mask_areas[1:]) + 1

        if segment_edges:
            self.bg_mask = self.masks == self.bg_mask_id

            # Relabel masks 
            sin_bg = np.logical_not(self.edges)
            sin_bg[self.masks == self.bg_mask_id] = 0
            self.mask_template = np.logical_or(old_copy, sin_bg)
            self.mask_template[black_zone_mask] = 0
            self.masks, self.num_masks = label(self.mask_template)
            self.mask_ids, self.mask_areas = np.unique(self.masks, return_counts=True)
            

    def get_all_avg_lab(self):
        # Flatten masks and lab arrays
        flat_masks = self.masks.ravel()
        flat_lab = self.lab.reshape(-1, 3)
        num_masks = self.num_masks + 1

        # Prepare output arrays
        avg_labs = np.zeros((num_masks, 3), dtype=np.float32)
        var_labs = np.zeros((num_masks, 3), dtype=np.float32)

        # Compute mean and variance for each channel using bincount
        for c in range(3):
            sums = np.bincount(flat_masks, weights=flat_lab[:, c], minlength=num_masks)
            means = sums / self.mask_areas
            avg_labs[:, c] = means

            # Variance: E[x^2] - (E[x])^2
            sq_sums = np.bincount(flat_masks, weights=flat_lab[:, c]**2, minlength=num_masks)
            mean_sq = sq_sums / self.mask_areas
            var_labs[:, c] = mean_sq - means**2

        self.avg_labs = avg_labs
        self.var_labs = np.linalg.norm(var_labs, axis=1)
        return avg_labs, var_labs

    def adjust_layer_labels(self):
        if self.segment_edges:
            l = np.mean(self.lab[:,:,0][self.bg_mask])
            a = np.mean(self.lab[:,:,1][self.bg_mask])
            b = np.mean(self.lab[:,:,2][self.bg_mask])
            self.avg_bg_lab = np.array([l, a, b])
        else:
            self.avg_bg_lab = self.avg_labs[self.bg_mask_id]

        adjustment_factor = self.avg_bg_lab - np.array(self.target_bg_lab)
        new_layer_labels = {}
        for key, value in self.layer_labels.items():
            new_key = tuple(key + adjustment_factor)
            new_layer_labels[new_key] = value
        
        self.layer_labels = new_layer_labels
        # Add bg lab
        self.layer_labels[tuple(self.avg_bg_lab)] = 'bg'
        second_bg_lab = (self.avg_bg_lab[0] - 10, self.avg_bg_lab[1] + 1.5, self.avg_bg_lab[2] + 0.5)
        self.layer_labels[second_bg_lab] = 'bg'
        # third_bg_lab = (self.avg_bg_lab[0] + 3, self.avg_bg_lab[1], self.avg_bg_lab[2])
        # self.layer_labels[third_bg_lab] = 'bg'
        # third_bg_lab = (self.avg_bg_lab[0] - 1, self.avg_bg_lab[1] - 1, self.avg_bg_lab[2] - 0.1)
        # self.layer_labels[third_bg_lab] = 'bg'

    def label_masks(self):
        self.adjust_layer_labels()
        self.mask_labels = []

        # Prepare layer label LABs and types as arrays/lists
        base_labs = np.array(list(self.layer_labels.keys()))
        layer_types = list(self.layer_labels.values())

        # Compute all pairwise distances (masks x base_labs)
        dists = np.linalg.norm(self.avg_labs[:, None, :] - base_labs[None, :, :], axis=2)
        min_indices = np.argmin(dists, axis=1)

        for idx, i in enumerate(self.mask_ids):
            area = self.mask_areas[i]
            variance = self.var_labs[i]
            if i==0:
                # Don't label edge mask
                self.mask_labels.append('bg')
            elif area < self.min_area:
                self.mask_labels.append('dirt')
            else:
                label = layer_types[min_indices[idx]]
                if ('mono' in label or 'bi' in label or 'tri' in label) and (variance > self.max_var or variance < self.min_var):
                    label = 'dirt'
                self.mask_labels.append(label)

    def process_frame(self, black_zone_mask=None, segment_edges=False):
        self.make_masks(black_zone_mask, segment_edges)
        self.get_all_avg_lab()
        self.label_masks()

    def prettify(self):
        # Prepare a lookup table for colors for all mask ids
        color_table = np.zeros((np.max(self.mask_ids) + 1, 3))
        # Assign colors for valid masks, black for others
        for idx, i in enumerate(self.mask_ids):
            area = self.mask_areas[idx]
            label = self.mask_labels[idx]
            if (area > self.min_area and area < self.max_area):
                color_table[i] = self.colors[label]
            else:
                color_table[i] = np.array([0, 0, 0])

        # Map each pixel in self.masks to its color using the lookup table
        colored_masks = color_table[self.masks]
        self.colored_masks = colored_masks
        return colored_masks

    def numberify(self):
        # Prepare a lookup table for numbers for all mask ids
        number_table = np.zeros(np.max(self.mask_ids) + 1)
        for idx, i in enumerate(self.mask_ids):
            area = self.mask_areas[idx]
            label = self.mask_labels[idx]
            if (area > self.min_area and area < self.max_area):
                number_table[i] = self.numbers[label]
            else:
                number_table[i] = 0

        # Map each pixel in self.masks to its number using the lookup table
        result = number_table[self.masks]
        self.numbered_masks = result
        return result
    
    def variance_map(self):
        # Prepare a lookup table for numbers for all mask ids
        var_table = np.zeros((np.max(self.mask_ids) + 1))
        for i in self.mask_ids:
            var_table[i] = self.var_labs[i]

        # Map each pixel in self.masks to its number using the lookup table
        result = var_table[self.masks]
        self.variance_masks = result
        return result
    
    def labelify(self, shrink=1):
        """
        Returns a 2D array where each pixel contains the string label of its segment.
        """
        # Prepare a lookup table for labels for all mask ids
        label_table = np.array(self.mask_labels, dtype=object)
        # Map each pixel in self.masks to its label using the lookup table
        new_size = (int(shrink*self.size[1]), int(shrink*self.size[0]))
        resized_masks = cv2.resize(self.masks.astype('uint8'), new_size, interpolation=cv2.INTER_NEAREST)
        result = label_table[resized_masks]
        self.labeled_masks = result
        return result


    def largest_flakes(self, layer_type):
        """
        Find the size and locations of the largest {layer_type} flakes in the frame
        """
        
        idxs = np.array(self.mask_labels) == layer_type
        flake_areas = self.mask_areas[idxs]
        flake_locations = np.stack([self.mask_coords(mask_id) for mask_id in self.mask_ids[idxs]], axis=-1)
        return flake_areas, flake_locations
    
    def mask_coords(self, mask_id):
        """
        Returns the (row, col) coordinates of the centroid of the given mask id.
        """
        coords = np.argwhere(self.masks == mask_id)
        if coords.size == 0:
            return None  # Mask id not found
        centroid = coords.mean(axis=0)
        return tuple(centroid)