from corner import calibrate_corners
from homography import extract_features, identify_corner_with_ransac
import cv2
import numpy as np
from stage import Stage

def get_theta_homography(H):
    a, b = H[0, 0], H[0, 1]
    return np.arctan2(b, a)

def get_exact_location(coord, flake_location, frame_dims):
    coord[0] += 103_900*(flake_location[1]/frame_dims[1] - 0.5)
    coord[1] += 57_700*(flake_location[0]/frame_dims[0] - 0.5)
    return coord

z_corners, chip_dims, angle, stage, lens, corner_imgs, corner_postitions = calibrate_corners(ret_corner_imgs=True, is_main=True)
lens.rotate_to_position(1)

for i in range(len(corner_imgs)):
    cv2.imwrite(f"corner_observed{i}.png", corner_imgs[i])

target_corner = cv2.imread('corner1.png', cv2.IMREAD_COLOR_BGR)

# Initialize the ORB feature detector and BFMatcher.
orb = cv2.ORB_create(nfeatures=1000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

known_labels = [0,1,2,3]
known_corner_features = extract_features(corner_imgs, orb)
correct_corner_idx, inliers, features, matches, H = identify_corner_with_ransac(target_corner, known_corner_features, known_labels, orb, bf)


mid_translation = (H - np.identity(3)) @ (np.array([0.5, 0.5, 1]))
mid_translation = np.array([
    51_950 * mid_translation[0],
    28_850 * mid_translation[1]
])
print(H)
print(mid_translation)

print("Move?")
if input() == 'y':
    stage.move_to(corner_postitions[correct_corner_idx] + mid_translation, wait=True)

    stage.set_home()
    stage.set_chip_dims(*chip_dims)
    stage.set_direction(get_theta_homography(H))
    stage.get_snake()