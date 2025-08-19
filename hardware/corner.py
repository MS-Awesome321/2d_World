import cv2
import numpy as np
from PIL import ImageGrab
from stage import Stage
import time
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from autofocus import incremental_check
from turret import Turret


# cap = cv2.VideoCapture('test_video.mp4')
shrink = 4
radius = 6
pad = 25

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

def get_angle(pt0, pt1):
    x0, y0 = pt0
    x1, y1 = pt1
    theta = np.arctan2((y0 - y1), (x1 - x0)) # trust, the inconsistency makes it work
    theta = float(np.rad2deg(theta))

    if theta >= 0:
        return theta
    else:
        return theta + 360
    
def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

try:
    x = '27503936'
    y = '27503951'

    stage = Stage(x, y, focus_comport='COM5', magnification=5)
    stage.x_speed = 100_000
    stage.y_speed = 100_000
    stage.x_accl = 700_000
    stage.y_accl = 700_000
    prev_direction = 0
    counter = 0
    limit = 0

    lens = Turret('COM7')
    lens.rotate_to_position(1)

    points = []

    while len(points) < 200:
        # ret, frame = cap.read()
        # if not ret:
        #     break

        angles = []
        frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
        frame = frame[110:-110, 340:-300, :]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (int(frame.shape[1]/shrink), int(frame.shape[0]/shrink)), cv2.INTER_NEAREST)
        # gray =  cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.blur(frame[:,:,0], (5,5))
        ret, thresh_image = cv2.threshold(gray, 155, 255, cv2.THRESH_OTSU)
        contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            max_area = 0
            max_contour = None
            for contour in contours:
                a = cv2.contourArea(contour)
                if a >= max_area:
                    max_area = a
                    max_contour = contour

            perimeter = cv2.arcLength(max_contour, True)
            corners = cv2.approxPolyDP(max_contour, 0.04 * perimeter, True)

            if corners is not None:
                inner_corners = []
                true_corners = []

                for i in range(len(corners)):
                    x, y = corners[i][0]
                    if (x > pad and x < frame.shape[1] - pad) ^ (y > pad and y < frame.shape[0] - pad):
                        cv2.circle(frame, (x, y), radius, (0, 255, 0), -1)
                        inner_corners.append((x,y))

                    elif (x > pad and x < frame.shape[1] - pad) and (y > pad and y < frame.shape[0] - pad):
                        cv2.circle(frame, (x, y), radius, (255, 0, 0), -1)
                        true_corners.append((x,y))

                    else:
                        cv2.circle(frame, (x, y), radius, (0, 0, 255), -1)

                # Draw contours 
                is_corner = (len(inner_corners) == 2 and len(true_corners) == 1)
                if is_corner:
                    cv2.drawContours(frame, max_contour, -1, (0, 255, 0), 2)
                else:
                    cv2.drawContours(frame, max_contour, -1, (0, 0, 255), 2)

                # Draw arrows between each adjacent corner point
                # if (len(inner_corners) <= 3 and len(true_corners) == 0) or (len(inner_corners) == 2 and len(true_corners) == 1):
                pts = corners.reshape(-1, 2)
                for i in range(len(pts)):
                    pt1 = tuple(pts[i])
                    pt2 = tuple(pts[(i + 1) % len(pts)])
                    if (pt1 in inner_corners and pt2 in inner_corners) or pt1 in true_corners or pt2 in true_corners:
                        cv2.arrowedLine(frame, pt1, pt2, (0, 255, 255), 2, tipLength=0.1)
                        angles.append(round(get_angle(pt1, pt2), 2))
                # cv2.putText(frame, f'{angles}', org, font, fontScale, color, thickness, cv2.LINE_AA)

        cv2.imshow('Line Test', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        
        if len(angles) == 1:
            stage.jog_in_direction(angles[0], quick_stop=False)
            prev_direction = angles[0]
        elif len(angles) >= 2 and is_corner:
            max_dif = 0
            min_dif = 90
            max_angle = 0
            min_angle = 0
            for a in angles:
                dif = abs(prev_direction - a)
                if dif > max_dif:
                    max_dif = dif
                    max_angle = a
                if dif < min_dif:
                    min_dif = dif
                    min_angle = a
            if is_corner:
                stage.jog_in_direction(max_angle, quick_stop=False)
                prev_direction = max_angle
                limit = counter + 30
            else:
                stage.jog_in_direction(min_angle, quick_stop=False)
                prev_direction = min_angle
        else:
            stage.jog_in_direction(prev_direction, quick_stop=False)


        if len(angles) < 4:
            stage.jog_in_direction(prev_direction + 90, quick_stop=False)
            time.sleep(0.33)
            stage.jog_in_direction(prev_direction, quick_stop=False)
        else:
            points.append(stage.get_pos()[:2])
        counter += 1

except KeyboardInterrupt:
    pass
cv2.destroyAllWindows()
stage.stop()

points = np.stack(points, axis=0)
plt.scatter(points[:,0], points[:,1])

hull = ConvexHull(points)
for simplex in hull.simplices:
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')

# Get hull vertices in order
hull_pts = points[hull.vertices]
num_hull = len(hull.vertices)

# Calculate angles at each hull vertex (using previous, current, next)
angles = []
for i in range(num_hull):
    prev_pt = hull_pts[i - 1]
    curr_pt = hull_pts[i]
    next_pt = hull_pts[(i + 1) % num_hull]
    v1 = prev_pt - curr_pt
    v2 = next_pt - curr_pt
    # Normalize vectors
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    # Compute angle in degrees
    cos_angle = np.clip(np.dot(v1, v2), -1.0, 1.0)
    angle = np.degrees(np.arccos(cos_angle))
    angles.append(angle)

# Find indices of the 4 most acute angles (smallest angles)
acute_indices = np.argsort(angles)[:4]

plt.scatter(hull_pts[acute_indices,0], hull_pts[acute_indices,1], color='red')
plt.show()

stage.x_motor.setup_velocity(max_velocity=200_000, acceleration=1_000_000)
stage.y_motor.setup_velocity(max_velocity=200_000, acceleration=1_000_000)

# lens.rotate_to_position(5)
for i in acute_indices:
    corner = [hull_pts[i, 0], hull_pts[i, 1]]
    print(corner)
    stage.move_to(corner, wait=True)
    time.sleep(0.25)
    frame, max_pos = incremental_check(stage.focus_motor, 0, 100, 6000, slope_threshold=-2**(-9), verbose=True, auto_direction=True)
    print(max_pos)
