# Written by Brian Zhou

import os
import sys
import matplotlib.pyplot as plt
import cv2
import numpy as np
import re

def process_files(directory_path):
    """
    Iterates through all files in the specified directory and performs an action on each file.

    Args:
        directory_path (str): The path to a directory, such as a folder of images.

    Returns:
        files (list): A list containing the full paths to each file in the directory.
    """
    files = []
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            # Helps us ensur
            if os.path.isfile(file_path):
                print(f"Successfully loaded: {filename}")
                files.append(file_path)
        return files
    except FileNotFoundError:
        sys.exit(f"Error: Directory not found: {directory_path}")

    except Exception as e:
        sys.exit(f"An error occurred while loading in files: {e}")

def check_images(images):
    """
    Checks if a list of images was loaded in correctly.

    Args:
        images (list): A list of cv2 images (i.e. from cv2.imread) to check

    Returns: none
    """
    for idx, image in enumerate(images):
        # Check if the image loaded correctly
        if image is None:
            print("Image ", idx, " did not load. Check the file path.")
        else:
            # Convert from BGR to RGB for proper display in matplotlib
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            plt.imshow(image_rgb)
            plt.title("Corner " + str(idx))
            plt.axis('off')
            plt.show()

def extract_features(images, detector):
    """
    Extract keypoints and descriptors from an image.

    Args:
        images (list): A list of input images in BGR format (e.g. after cv2.imread).
        detector (cv2.Feature2D): An OpenCV feature detector (e.g. SIFT, SURF, ORB, etc).

    Returns:
        features (list): A list of tuples where each element is in the format (keypoints, descriptors).
    """
    features = []
    for image in images:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = detector.detectAndCompute(gray, None)
        features.append((keypoints, descriptors))

    return features

def match_features(des1, des2, matcher, ratio=0.75):
    """
    Match feature descriptors between two images using k-nearest neighbors matching (i.e. returns k best matches)
    and Lowe's ratio test (removes outliers past a threshold).

    Args:
        des1 (np.ndarray): Descriptors from the first image.
        des2 (np.ndarray): Descriptors from the second image.
        matcher (cv2.DescriptorMatcher): An OpenCV matcher instance (e.g., BFMatcher, FLANN).

        ratio (float): Ratio threshold for Lowe's test, defaulting to 0.75.

    Returns:
        good_matches (list): List of the matches that pass Lowe's ratio test.
    """
    matches = matcher.knnMatch(des1, des2, k=2)
    good_matches = []

    for m, n in matches:
        if m.distance < ratio * n.distance:
            good_matches.append(m)

    return good_matches

def identify_corner_with_ransac(unknown_img, known_features, known_labels, detector, matcher, ratio=0.75):
    """
    Identify the corresponding known corner for an unknown corner image by matching features
    and using RANSAC to filter out outliers.

    Args:
        unknown_img (np.ndarray): The unknown corner image in BGR format.
        known_features (list of tuples): A list where each element is a tuple (keypoints, descriptors)
                                          corresponding to a known corner image.
        known_labels (list): List of labels corresponding to the known features (e.g., ['A', 'B', 'C', 'D']).
        detector (cv2.Feature2D): Feature detector instance for extracting features from the unknown image.
        matcher (cv2.DescriptorMatcher): Descriptor matcher instance to match features.
        ratio (float): Ratio threshold for Lowe's test, defaulting to 0.75.

    Returns:
        best_label (str or None): The label of the known corner that best matches the unknown image.
        best_inliers (int): The number of inlier matches after RANSAC for the best match.
        unknown_features (list of tuples): The (keypoints, descriptors) of the unknown image.
        good_matches (list): The list of cv2.DMatches between the images.
        best_H (np.ndarray): The homography matrix computed from the best match.
    """
    # Extract features from the unknown image
    gray = cv2.cvtColor(unknown_img, cv2.COLOR_BGR2GRAY)
    kp_unknown, des_unknown = detector.detectAndCompute(gray, None)

    best_label = None
    best_inliers = 0
    best_H = None
    best_good_matches = None

    idx = 0
    # Iterate over each set of pre-extracted known features and their label
    for (kp_known, des_known) in known_features:
        good_matches = match_features(des_unknown, des_known, matcher, ratio)

        # We need at least 4 matches to compute a homography using RANSAC
        if len(good_matches) >= 4:
            pts_unknown = np.float32([kp_unknown[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            pts_known = np.float32([kp_known[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # Compute homography using RANSAC to filter out outliers
            H, mask = cv2.findHomography(pts_known, pts_unknown, cv2.RANSAC)
            if mask is not None:
                inliers = int(mask.sum())
                print(f"Corner {idx}: {len(good_matches)} good matches, {inliers} inliers.")
                if inliers > best_inliers:
                    best_inliers = inliers
                    best_label = idx
                    best_H = H
                    best_good_matches = good_matches
        else:
            # Optionally, log or skip this candidate if there aren't enough matches.
            print(f"Not enough good matches for corner {idx}. Found only {len(good_matches)} matches.")
        idx += 1
    return best_label, best_inliers, (kp_unknown, des_unknown), best_good_matches, best_H

def compute_homography(matches, kp1, kp2):
    """
    Returns a homography matrix given matched features and their corresponding keypoints.

    Args:
        matches (cv2.DMatch): Matched features from two images.
        kp1 (list): List of keypoints from source image.
        kp2 (list): List of keypoints from destimation image.

    Returns:
        H (np.ndarray): The computed 3x3 homography matrix.

    """
    # Ensure we have enough matches for homography (need at least 4)
    if len(matches) >= 4:
        # Extract the coordinates of the good matches.
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape((-1, 1, 2))
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape((-1, 1, 2))
        print("Source: ", src_pts, "\nDestination: ", dst_pts)

        # Compute the homography using RANSAC
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    else:
        raise ValueError("Not enough good matches (>= 4) to perform RANSAC.")
    H, status = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC)

    return H

def transform_flake_coordinates(flake_vector, H, corner_new):
    """
    Given a flake vector relative to an old corner, compute its new vector relative to the new corner.

    Args:
        flake_vector (tuple): The vector to flake from old corner.
        H (np.ndarray): Homography matrix mapping old coordinates to new.
        corner_new (tuple): Coordinates of the new reference corner.

    Returns:
        new_position (tuple): The vector to the flake relative to new corner.
    """
    # Extract the linear part of the homography
    A = H[:2, :2]

    # Convert the relative vector into a 2x1 column vector
    relative_vec = np.array(flake_vector, dtype=np.float32).reshape(2, 1)

    # Transform the relative vector using the linear part of H
    transformed_vec = A.dot(relative_vec)

    # Add the new corner's coordinates to get the absolute new position
    new_position = (corner_new[0] + transformed_vec[0, 0],
                    corner_new[1] + transformed_vec[1, 0])

    return new_position

def organize_images(known_corners, new_corners, known_images):
    """
    Collects all relevant images and preprocesses them into the correct formats for corner-matching and homography.

    Args:
        known_corners (str): The path to a folder containing the 4 known corners. The folder must only contain
                              known corners, in consecutive order (i.e. ABCD, BCDA, CDAB, or DABC are ok, but
                              not ACBD or BADC etc).
        new_corners (str): The path to a folder containing unknown potential corners. The folder may contain
                            other random images in addition. Additional images increase required computation,
                            but will not prevent accurate results.
        known_images (str): The path to a folder containing all images of interest (i.e. flakes) on the old chip
                            that you want to "refind" on the new chip orientation. The overall system will apply
                            the best homography transformation to these coordinates.
    Returns:
        known_corner_paths (list): A list of 4 paths to the contents of known_corners. Indexed same way.
        known_corner_imgs (list): A list of 4 images (BGR format, e.g. from cv2.imread) of the paths in known_corners. Indexed same way.
        known_corner_coords (list): A list of 4 coordinates corresponding to the images in known_corners. Indexed same way.
        new_corner_paths (list): A list of paths to the images in new_corners. Indexed same way.
        new_corner_imgs (list): A list of images (BGR format) of the paths in new_images. Indexed same way.
        new_corner_coords (list): A list of coordinates to unknown potential corners. Indexed same way.
        known_paths (list): A list of paths to the contents of known_images. Indexed same way.
        known_imgs (list): A list of images (BGR format) of the paths in known_images. Indexed same way.
        known_coords (list): A list of coordinates to known images. Indexed same way.
    """

    # Extract numbers inside parentheses and separated by a comma
    pattern = r'\(([-\d\.]+),([-\d\.]+)\)'

    # Preprocess known corners
    known_corner_paths = process_files(known_corners)
    known_corner_imgs = []
    for idx, path in enumerate(known_corner_paths):
        # if idx > 3:
        #     raise ValueError("There should only be 4 images in the known corners folder:", known_corners)
        known_corner_imgs.append(cv2.imread(path))

    known_corner_coords = []
    for path in known_corner_paths:
        match = re.search(pattern, path)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            known_corner_coords.append((x, y))
        else:
            raise ValueError("No coordinates found in filename:", path)

    # Preprocess new corners
    new_corner_paths = process_files(new_corners)
    new_corner_imgs = []
    new_corner_coords = []

    for path in new_corner_paths:
        new_corner_imgs.append(cv2.imread(path))

        match = re.search(pattern, path)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            new_corner_coords.append((x, y))
        else:
            # raise ValueError("No coordinates found in filename:", path)
            pass

    # Preprocess known images
    known_paths = process_files(known_images)
    known_imgs = []
    known_coords = []

    for path in known_paths:
        known_imgs.append(cv2.imread(path))

        match = re.search(pattern, path)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            known_coords.append((x, y))
        else:
            raise ValueError("No coordinates found in filename:", path)

    return known_corner_paths, known_corner_imgs, known_corner_coords, new_corner_paths, new_corner_imgs, new_corner_coords, known_paths, known_imgs, known_coords


# Main Method tests efficacy of Homography Matrix Finding Algorithm
if __name__ == '__main__':
    img_og = cv2.imread('photo_dir/test_49.jpg', cv2.IMREAD_COLOR_BGR)
    shape = np.array(img_og.shape[:2][::-1])
    
    # Rotate and translate image
    R = cv2.getRotationMatrix2D(0.5 * shape, 45, 1)
    img_rotated = cv2.warpAffine(img_og, R, shape)

    tx = 100
    ty = 50 
    T = np.float32([[1, 0, tx], [0, 1, ty]])
    img_translated = cv2.warpAffine(img_rotated, T, shape)

    cv2.imshow("Image", img_og)
    cv2.imshow("Image Rotated", img_rotated)
    cv2.imshow("Image Translated", img_translated)

    # Initialize the ORB feature detector and BFMatcher.
    orb = cv2.ORB_create(nfeatures=1000)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    # Get a bunch of other images to see if RANSAC is fooled
    knockoff_paths = [f'photo_dir/test_{i}.jpg' for i in range(2, 15, 5)]
    varied_imgs = [cv2.imread(path) for path in knockoff_paths]
    varied_imgs.append(img_og)

    known_labels = [0,1,2,3]
    known_corner_features = extract_features(varied_imgs, orb)
    label, inliers, features, matches, H = identify_corner_with_ransac(img_translated, known_corner_features, known_labels, orb, bf)

    print(H) # Does not get fooled!

    result = cv2.warpPerspective(varied_imgs[label], H, shape)
    cv2.imshow("Result", result)
    cv2.waitKey(0)