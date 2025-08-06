import cv2
import numpy as np
from scipy.ndimage import label
import matplotlib.pyplot as plt
from skimage.morphology import disk

def opencv_rank_gradient(image, selem):
    """
    Mimics skimage.filters.rank.gradient using OpenCV and NumPy.

    Args:
        image (np.ndarray): Grayscale input image (uint8).
        selem (np.ndarray): Structuring element (binary mask, e.g., from skimage.morphology.disk).

    Returns:
        np.ndarray: Gradient image (uint8).
    """
    # Ensure image is uint8
    if image.dtype != np.uint8:
        image = (255 * (image - np.min(image)) / (np.ptp(image) + 1e-8)).astype(np.uint8)

    # Use OpenCV to compute local min and max
    kernel = selem.astype(np.uint8)
    local_max = cv2.dilate(image, kernel)
    local_min = cv2.erode(image, kernel)
    gradient = local_max - local_min
    return gradient

class ChipFinder():
    def __init__(self, img, threshold = 25, min_area = 100000, labels = None):
        self.img = img
        self.lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.int16)
        self.lab[:,:,0] = self.lab[:,:,0] * 100.0/255.0
        self.lab[:,:,1] -= 128
        self.lab[:,:,2] -= 128
        self.threshold = threshold
        self.min_area = min_area

        if labels is None:
            self.labels = {
                (74.6, 26.9, -14.6): 1,
                (0,0,0): 0,
                (39.1, 24.9, 18.7): 0,
            }
        else:
            self.lables = labels

    def segment(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)

        self.saved_edges = opencv_rank_gradient(gray, disk(7))
        self.edges = self.saved_edges > self.threshold
        self.masks, self.num_masks = label(np.logical_not(self.edges))
        self.mask_ids, self.mask_areas = np.unique(self.masks, return_counts=True)
        self.mask_ids = self.mask_ids[self.mask_areas > self.min_area]
        return self.masks
    
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
        return avg_labs, var_labs
    
    def label_masks(self):
        self.mask_labels = []

        # Prepare layer label LABs and types as arrays/lists
        base_labs = np.array(list(self.labels.keys()))
        layer_types = list(self.labels.values())

        # Compute all pairwise distances (masks x base_labs)
        dists = np.linalg.norm(self.avg_labs[:, None, :] - base_labs[None, :, :], axis=2)
        min_indices = np.argmin(dists, axis=1)

        for idx in self.mask_ids:
            label = layer_types[min_indices[idx]]
            self.mask_labels.append(label)

    def prettify(self):
        self.colored_masks = np.zeros_like(self.masks)

        for i, idx in enumerate(self.mask_ids):
            if self.mask_labels[i] == 1:
                self.colored_masks[self.masks == idx] = 255

        self.colored_masks[self.edges] = 255
        return self.colored_masks
    
    def get_lines(self):
        edges = cv2.Canny(mask, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges,1,np.pi/36,50)
        if lines is None:
            return []
        return lines[:2]
    

if __name__ == '__main__':
    cap = cv2.VideoCapture('test_video.mp4')
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = frame[100:-100, 350:1000, :]
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        test = ChipFinder(img)
        test.segment()
        test.get_all_avg_lab()
        test.label_masks()
        mask = test.prettify().astype('uint8')

        # Convert mask to RGB for visualization
        mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

        lines = test.get_lines()

        # Draw Hough lines
        line_params = []
        intersections = []

        for line in lines[:2]:
            rho,theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 2000*(-b))
            y1 = int(y0 + 2000*(a))
            x2 = int(x0 - 2000*(-b))
            y2 = int(y0 - 2000*(a))

            cv2.line(mask_rgb,(x1,y1),(x2,y2),(0,255,0),2)

            A = y2 - y1
            B = x1 - x2
            C = A * x1 + B * y1
            line_params.append((A, B, C))

        # Find intersection of the two lines
        (A1, B1, C1), (A2, B2, C2) = line_params
        determinant = A1 * B2 - A2 * B1
        if determinant != 0:
            x = int((B2 * C1 - B1 * C2) / determinant)
            y = int((A1 * C2 - A2 * C1) / determinant)
            intersections.append((x, y))
            cv2.circle(mask_rgb, (x, y), 10, (255, 0, 0), -1)

        cv2.imshow("Corner Finder", mask_rgb)
        cv2.waitKey(1)