import cv2
import numpy as np
from scipy.ndimage import label
from scipy.interpolate import LinearNDInterpolator
from skimage.morphology import disk
from skimage.color import lab2rgb
import time

class Segmenter():
    def __init__(self, img, material, colors=None, numbers=None, min_area = 50, max_area = 10000000, magnification=100, k=3, focus_disks=[], thickness=40, surround_bg=None):
        self.img = img
        self.size = img.shape[:2]
        self.target_bg_lab = material.target_bg_lab
        self.layer_labels = material.layer_labels
        self.edge_method = material.Edge_Method(k=k, magnification=magnification, args=material.args)
        self.colors = colors
        self.numbers = numbers
        self.min_area = min_area
        self.max_area = max_area
        self.focus_disks = focus_disks
        self.mag = magnification

        self.lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.int16)
        self.lab[:,:,0] = self.lab[:,:,0] * 100.0/255.0
        self.lab[:,:,1] -= 128
        self.lab[:,:,2] -= 128

        self.thickness = thickness
        if surround_bg is None:
            surround_bg = magnification==20
        if surround_bg:
            self.lab = self._border(self.lab, thickness)
        
        self.surround_bg = surround_bg


    def make_masks(self, segment_edges = False, erode_masks=0):
        if len(self.focus_disks)>0:
            black_zone_mask = self.focus_disks[0][0]
        else:
            black_zone_mask = None

        self.segment_edges = segment_edges

        self.edges = self.edge_method(self)

        if self.surround_bg:
            t = self.thickness//2
            self.edges[:t, :] = 0
            self.edges[-t:, :] = 0
            self.edges[:, :t] = 0
            self.edges[:, -t:] = 0

        if segment_edges:
                old_copy = self.edges.copy()
        if black_zone_mask is not None:
            self.edges[black_zone_mask] = 1

        template = np.logical_not(self.edges)
        self.masks, self.num_masks = label(template)
        self.mask_ids, self.mask_areas = np.unique(self.masks, return_counts=True)

        # Get BG mask
        masked = self.mask_areas.copy()
        masked[0] = 0
        self.bg_mask_id = np.argmax(masked)
        self.bg_mask = self.masks == self.bg_mask_id

        if erode_masks > 0:
            template = self.masks.copy()
            template[template > 0] = 1
            fp = disk(5)
            template = cv2.erode(template.astype('uint8'), fp, iterations=erode_masks)
            template = cv2.dilate(template, fp, iterations=erode_masks)

            if not segment_edges:
                self.masks, self.num_masks = label(template)
                self.mask_ids, self.mask_areas = np.unique(self.masks, return_counts=True)

        if segment_edges:
            # Relabel masks 
            sin_bg = np.logical_not(self.edges)
            sin_bg[self.masks == self.bg_mask_id] = 0
            self.mask_template = np.logical_or(old_copy, sin_bg)

            if black_zone_mask is not None:
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

        self.avg_labs = avg_labs
        # self.var_labs = np.linalg.norm(var_labs, axis=1)
        return avg_labs, var_labs
    
    def lab_equalize(self, num_points = 2000):
        points = []
        values = []

        # Inner Points
        while len(points) < 3*num_points//4:
            x = np.random.randint(low=0, high=self.lab.shape[1])
            y = np.random.randint(low=0, high=self.lab.shape[0])
            if self.bg_mask[y,x] != 0:
                points.append(np.array([y, x]))
                values.append(self.lab[y, x, :])

        if len(self.focus_disks) > 0:
            # Outer Circle Points
            i = 0
            while len(points) < num_points:
                r = self.focus_disks[0][1]
                theta = i * np.pi / (num_points // 4)
                x = int(r * np.cos(theta)) + self.lab.shape[1] // 2
                y = int(r * np.sin(theta)) + self.lab.shape[0] // 2
                i += 1

                if not((x < 0 or x >= self.lab.shape[1]) or (y < 0 or y >= self.lab.shape[0])):
                    if self.bg_mask[y,x] != 0:
                        points.append(np.array([y, x]))
                        values.append(self.lab[y, x, :])
                    else:
                        i -= 0.5

            # Corner points
            x0 = self.lab.shape[1] // 2 - np.sqrt(np.pow(r, 2) - np.pow(self.lab.shape[0] // 2, 2))
            y0 = 0
            x0 = int(x0)
            x1 = self.lab.shape[1] - x0
            y1 = self.lab.shape[0] - 1

            points.append(np.array([y0, x0]))
            points.append(np.array([y0, x1]))
            points.append(np.array([y1, x0]))
            points.append(np.array([y1, x1]))

            values.append(self.lab[y0, x0, :])
            values.append(self.lab[y0, x1, :])
            values.append(self.lab[y1, x0, :])
            values.append(self.lab[y1, x1, :])
        else:
            # Rest of the Inner Points
            while len(points) < num_points - 4:
                x = np.random.randint(low=0, high=self.lab.shape[1])
                y = np.random.randint(low=0, high=self.lab.shape[0])
                if self.bg_mask[y,x] != 0:
                    points.append(np.array([y, x]))
                    values.append(self.lab[y, x, :])

            # Corner Points
            for i in [0, self.lab.shape[0] - 1]:
                for j in [0, self.lab.shape[1] - 1]:
                    points.append(np.array([i, j]))
                    values.append(self.lab[i, j, :])

        # Interpolation
        points = np.stack(points, axis=0)
        self.interpolation_points = points
        values = np.stack(values, axis=0)
        grid_y, grid_x = np.mgrid[0:self.lab.shape[0], 0:self.lab.shape[1]]
        grid_points = np.stack([grid_y.ravel(), grid_x.ravel()], axis=-1)

        interpolator = LinearNDInterpolator(points, values, fill_value = 0)
        lab_bg = interpolator(grid_points).reshape(self.lab.shape[0], self.lab.shape[1], 3)

        l_bg = lab_bg[:,:,0]
        a_bg = lab_bg[:,:,1]
        b_bg = lab_bg[:,:,2]

        # Return Result
        l_bg[l_bg < 0] = 0
        # l_bg = l_bg.astype('int16')
        # a_bg = a_bg.astype('int16')
        # b_bg = b_bg.astype('int16')
        self.lab = self.lab.astype('float64')
        self.lab[:,:,0] -= l_bg - int(self.target_bg_lab[0])
        self.lab[:,:,1] -= a_bg - int(self.target_bg_lab[1])
        self.lab[:,:,2] -= b_bg - int(self.target_bg_lab[2])

        if len(self.focus_disks) > 0:
            f2 = self.focus_disks[-1][0]
            self.lab[f2] = 0
        self.l_bg = l_bg

        if self.surround_bg:
            t = self.thickness
            self.img = self.img[t:-t, t:-t, :]
            self.lab = self.lab[t:-t, t:-t, :]
            self.edges = self.edges[t:-t, t:-t]
            self.masks = self.masks[t:-t, t:-t]
            self.bg_mask = self.bg_mask[t:-t, t:-t]
        
        return l_bg

    def adjust_layer_labels(self):
        l = np.mean(self.lab[:,:,0][self.bg_mask])
        a = np.mean(self.lab[:,:,1][self.bg_mask])
        b = np.mean(self.lab[:,:,2][self.bg_mask])
        self.avg_bg_lab = np.array([l, a, b])

        adjustment_factor = self.avg_bg_lab - np.array(self.target_bg_lab)
        new_layer_labels = {}
        for key, value in self.layer_labels.items():
            new_key = tuple(key + adjustment_factor)
            new_layer_labels[new_key] = value
        
        self.layer_labels = new_layer_labels
        # Add bg lab
        self.layer_labels[tuple(self.avg_bg_lab)] = 'bg'

    def label_masks(self):
        self.mask_labels = []

        # Prepare layer label LABs and types as arrays/lists
        base_labs = np.array(list(self.layer_labels.keys()))
        layer_types = list(self.layer_labels.values())

        # Compute all pairwise distances (masks x base_labs)
        dists = np.linalg.norm(self.avg_labs[:, None, :] - base_labs[None, :, :], axis=2)
        min_indices = np.argmin(dists, axis=1)

        for idx, i in enumerate(self.mask_ids):
            area = self.mask_areas[i]
            if i==0 or i==self.bg_mask_id:
                # Don't label edge or bg mask
                self.mask_labels.append('bg')
            elif area < self.min_area:
                self.mask_labels.append('dirt')
            else:
                label = layer_types[min_indices[idx]]
                self.mask_labels.append(label)

    def process_frame(self, segment_edges=False, erode_masks = 0):
        self.make_masks(segment_edges, erode_masks)
        self.lab_equalize()
        self.get_all_avg_lab()
        self.adjust_layer_labels()
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
        to_stack = [self.mask_coords(mask_id) for mask_id in self.mask_ids[idxs]]
        if len(to_stack) > 0:
            flake_locations = np.stack(to_stack, axis=0)
            return flake_areas, flake_locations
        else:
            return flake_areas, None
    
    def mask_coords(self, mask_id):
        """
        Returns the (row, col) coordinates of the centroid of the given mask id.
        """
        coords = np.argwhere(self.masks == mask_id)
        if coords.size == 0:
            return None  # Mask id not found
        centroid = coords.mean(axis=0)
        return np.array(centroid)
    
    def direct_lab_label(self, window_size=(2,2)):
        """
        Labels each pixel in self.lab by layer type, according to self.layer_labels,
        and returns a prettified RGB image using self.colors.
        """
        m, n = window_size
        # Pad lab image for sliding window
        pad_h = m // 2
        pad_w = n // 2
        lab_padded = np.pad(self.lab, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='reflect')

        # Efficient sliding window mean using convolution
        kernel = np.ones((m, n), dtype=np.float32) / (m * n)
        avg_l = cv2.filter2D(lab_padded[:,:,0], -1, kernel)[pad_h:-pad_h, pad_w:-pad_w]
        avg_a = cv2.filter2D(lab_padded[:,:,1], -1, kernel)[pad_h:-pad_h, pad_w:-pad_w]
        avg_b = cv2.filter2D(lab_padded[:,:,2], -1, kernel)[pad_h:-pad_h, pad_w:-pad_w]
        avg_lab = np.stack([avg_l, avg_a, avg_b], axis=-1)

        # Prepare LAB keys and corresponding layer types
        lab_keys = np.array(list(self.layer_labels.keys()))
        layer_types = np.array(list(self.layer_labels.values()))

        # Compute distances and assign labels in a vectorized way
        avg_lab_flat = avg_lab.reshape(-1, 3)
        dists = np.linalg.norm(avg_lab_flat[:, None, :] - lab_keys[None, :, :], axis=2)
        label_indices = np.argmin(dists, axis=1)
        labels_flat = np.array(layer_types)[label_indices]

        # Map layer types to colors
        color_table = np.zeros((labels_flat.size, 3))
        for idx, label in enumerate(labels_flat):
            color_table[idx] = self.colors[label]
        prettified_img = color_table.reshape(self.lab.shape[0], self.lab.shape[1], 3)

        self.direct_lab_pretty = prettified_img
        return prettified_img
    
    def find_match(self, template_flake, template_mag=None, error_bound = 0.1):
        if template_mag is None:
            template_mag = self.mag

        target_area = np.sum(template_flake)
        target_area *= (self.mag/template_mag)**2
        error_bound *= target_area
        similar_area_masks = self.mask_ids[self.mask_areas >= target_area - error_bound and self.mask_areas <= target_area + error_bound]

        min_diff = 1
        result = None
        for i in similar_area_masks:
            mask = np.zeros_like(self.masks)
            mask[self.masks == i] = 1
            diff = flake_match (mask, template_flake)

            if diff < min_diff:
                min_diff = diff
                result = mask

        return result

    def _border(self, lab, thickness=30, n=10, threshold=40):
        dims = [lab.shape[0] + 2*thickness, lab.shape[1] + 2*thickness, lab.shape[2]]
        result = np.ones(dims, dtype=lab.dtype)
        h, w = lab.shape[0], lab.shape[1]
        hs = [int(i*h/n) for i in range(n)] + [h]
        ws = [int(i*w/n) for i in range(n)] + [w]

        hr = [int(i*result.shape[0]/n) for i in range(n)] + [result.shape[0]]
        wr = [int(i*result.shape[1]/n) for i in range(n)] + [result.shape[1]]

        ms = np.zeros([n,n, lab.shape[2]])
        for i in range(n):
            for j in range(n):
                    region = lab[hs[i]:hs[i+1], ws[j]:ws[j+1], :]
                    ms[i, j, :] = np.median(region, axis=(0,1))

        # ms_m = np.median(ms, axis=(0,1))
        
        mask = np.linalg.norm(ms - self.target_bg_lab, ord=1, axis=2) > threshold
        ms[mask] = self.target_bg_lab

        for i in range(n):
            for j in range(n):       
                if i == 0 or i == n-1 or j==0 or j == n-1: 
                    result[hr[i]:hr[i+1], wr[j]:wr[j+1], :] = ms[i, j, :]

        result[thickness:-thickness,thickness:-thickness,:] = lab
        return result

def flake_match(flake1: np.ndarray, flake2: np.ndarray) -> float:
    contour1, _ = cv2.findContours(flake1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour2, _ = cv2.findContours(flake2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return cv2.matchShapes(contour1[0], contour2[0], cv2.CONTOURS_MATCH_I1, 0) # Hu Moments

