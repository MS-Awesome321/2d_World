from corner import calibrate_corners
from homography import extract_features, identify_corner_with_ransac
import cv2
import numpy as np
from stage import Stage
from turret import Turret

def get_theta_homography(H):
    a, b = H[0, 0], H[0, 1]
    return np.arctan2(b, a)

def get_exact_location(coord, flake_location, frame_dims):
    coord[0] += 103_900*(flake_location[1]/frame_dims[1] - 0.5)
    coord[1] += 57_700*(flake_location[0]/frame_dims[0] - 0.5)
    return coord

print("Enter mode (p or f): ")
mode = input()
if mode == 'p':
    corner_imgs = []
    for i in range(4):
        corner_imgs.append(cv2.imread(f"corner_observed{i}.png"))

    x = '27503936'
    y = '27503951'

    stage = Stage(x, y, focus_comport='COM5', magnification=10)
    stage.x_speed = 70_000
    stage.y_speed = 70_000
    stage.x_accl = 700_000
    stage.y_accl = 700_000
    lens = Turret('COM7')
    lens.rotate_to_position(1)
else:
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

if mode != 'p':
    stage.move_to(corner_postitions[correct_corner_idx], wait=True)

print(H)
a, b, tx = H[0, 0], H[0, 1], H[0, 2]
c, d, ty = H[1, 0], H[1, 1], H[1, 2]
theta = np.arctan2(b, a)
translation = (tx, ty)

tx /= target_corner.shape[0]
ty /= target_corner.shape[0]

tx *= -103_900
ty *= -103_900


print(theta)
print(translation)
print(tx, ty)

if mode == 'p':
    stage.move_by([tx, ty], wait=True)
else:
    target_pos = np.array([tx, ty, z_corners[correct_corner_idx]])
    stage.move_by(target_pos, wait=True)
    stage.set_home()
    stage.set_chip_dims(*chip_dims)
    stage.set_direction(get_theta_homography(H))
    stage.get_snake()