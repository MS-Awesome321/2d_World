from stage import Stage
from turret import Turret
import numpy as np
from PIL import ImageGrab
import cv2

x = '27503936'
y = '27503951'

stage = Stage(x, y, focus_comport='COM5', magnification=10)
lens = Turret('COM7')

shrink = 2
radius = 6
pad = 50

def corner_coords(frame):
    gray = cv2.blur(frame[:,:,0], (10,10))
    ret, thresh_image = cv2.threshold(gray, 155, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    max_contour = None
    for contour in contours:
        a = cv2.contourArea(contour)
        if a > max_area:
            max_area = a
            max_contour = contour

    perimeter = cv2.arcLength(max_contour, True)
    corners = cv2.approxPolyDP(max_contour, 0.05 * perimeter, True)
    return corners

def quadrant(v):
    x, y = v[0], v[1]
    if x >= 0 and y >= 0:
        return 1
    elif x < 0 and y >= 0:
        return 2
    elif x < 0 and y < 0:
        return 3
    else:
        return 4

def process_corners(corners, frame, prev_direction):
    # Is a Corner?
    inner_corners = []
    true_corners = []

    for i in range(len(corners)):
        x, y = corners[i][0]
        if (x > pad and x < frame.shape[1] - pad) or (y > pad and y < frame.shape[0] - pad):
            inner_corners.append(np.array([x,y]))

            if (x > pad and x < frame.shape[1] - pad) and (y > pad and y < frame.shape[0] - pad):
                cv2.circle(frame, (x, y), radius, (255, 0, 0), -1)
                true_corners.append(np.array([x,y]))
            else:
                cv2.circle(frame, (x, y), radius, (0, 255, 0), -1)
        else:
            cv2.circle(frame, (x, y), radius, (0, 0, 255), -1)

    is_corner = (len(inner_corners) == 3 and len(true_corners) == 1)

    if is_corner:
        true_corner = true_corners[0]
        v0 = true_corner - inner_corners[0]
        v1 = true_corner - inner_corners[1]
        v2 = true_corner - inner_corners[2]
        v = v0 + v1 + v2
        
        move_direction = np.rad2deg(np.arctan(v[1]/v[0])) + 135
    else:
        move_direction = prev_direction

    return move_direction, is_corner

found_corners = 0
move_direction = 90

while found_corners < 4:
    frame = np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = frame[100:-100, 300:-260, :]
    frame = cv2.resize(frame, (int(frame.shape[1]/shrink), int(frame.shape[0]/shrink)), cv2.INTER_NEAREST)

    corners = corner_coords(frame)
    move_direction, is_corner = process_corners(corners, frame, move_direction)
    stage.jog_in_direction(move_direction, quick_stop=False)
    
    found_corners += 1