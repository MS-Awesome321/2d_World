import cv2
import numpy as np
from PIL import ImageGrab
from stage import Stage
import time
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from autofocus import incremental_check
from turret import Turret
import sys
sys.path.append('C:/Users/admin/Desktop/2d_World/')
from utils import Stopwatch
from typing import List, Any

def calibrate_corners(is_main: bool = False, ret_corner_imgs: bool = False) -> List[Any]:
    '''
    Traces edges of a silicon chip placed under the microscope to find the corners
    and calibrates the micrscope focus at 10x for each corner. 

    MUST be run before autosearch each time a new chip is placed under the microscope.

    Example:
    .. code-block:: python
        z_corners, chip_dims, angle = calibrate_corners()
        results_10x, results100x = autosearch(z_corners, angle, chip_dims, num_top_matches = 25)

    Arguments:
        is_main: True only if the main method of corner.py is run. If True, displays cv2 window
            with internal computations that are done in calibrate_corners.

        ret_corner_imgs: If true, returns the images of the 4 corners of the chip. Used for 
            corner matching during flake refinding in the transfer process.

    Returns:
        Result (tuple):
            z_corners: A list of 3 integers representing the z-values of the bottom left, top left, and
                top right corners in that order, with the z-value for the bottom right corner
                (fixed as the origin) assumed to be 0.

            angle: The angle, measured counterclockwise from the x-axis, at which the snake scan should 
                proceed from the origin.

            chip_dims: The length and width of the chip to be scanned, in inches.
    '''
    
    shrink = 4
    radius = 6
    pad = 10

    def get_angle(pt0, pt1):
        x0, y0 = pt0
        x1, y1 = pt1
        theta = np.arctan2((y0 - y1), (x1 - x0)) # trust, the inconsistency makes it work
        theta = float(np.rad2deg(theta))

        return theta
        # if theta > 0:
        #     return theta
        # else:
        #     return theta + 360
        
    try:
        x = '27503936'
        y = '27503951'

        stage = Stage(x, y, focus_comport='COM5', magnification=10)
        stage.x_speed = 80_000
        stage.y_speed = 80_000
        stage.x_accl = 700_000
        stage.y_accl = 700_000
        prev_direction = 0
        prev_popped_point = 0

        if is_main:
            watch = Stopwatch()
            watch.clock()
        
        lens = Turret('COM7')
        lens.rotate_to_position(1)

        points = []

        def make_gray(img):
            r = img[:,:,0]
            g = img[:,:,1]
            b = img[:,:,2]
            result = r + b - g
            result[result > 255] = 255
            result[result < 0] = 0
            return 255 - result


        while len(points) < 190:
            angles = []

            # Get Frame
            frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
            frame = frame[110:-110, 340:-300, :]
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (int(frame.shape[1]/shrink), int(frame.shape[0]/shrink)), cv2.INTER_NEAREST)
            gray = cv2.blur(make_gray(frame), (10,10))
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
                corners = cv2.approxPolyDP(max_contour, 0.06 * perimeter, True)

                frame_area = frame.shape[0] * frame.shape[1]

                if corners is not None:
                    # Determine corners outside of padding
                    inner_corners = []
                    for i in range(len(corners)):
                        x, y = corners[i][0]
                        if (x > pad and x < frame.shape[1] - pad) or (y > pad and y < frame.shape[0] - pad):
                            if is_main:
                                cv2.circle(frame, (x, y), radius, (0, 255, 0), -1)
                            inner_corners.append((x,y))

                        else:
                            if is_main:
                                cv2.circle(frame, (x, y), radius, (0, 0, 255), -1)

                    # Draw contours 
                    if is_main:
                        if len(corners) < 5 and (max_area > 0.5 * frame_area and max_area < 0.85 * frame_area):
                            cv2.drawContours(frame, max_contour, -1, (0, 255, 0), 2)
                        else:
                            cv2.drawContours(frame, max_contour, -1, (0, 0, 255), 2)
                    
                    # Draw arrows between each adjacent corner point
                    pts = corners.reshape(-1, 2)
                    for i in range(len(pts)):
                        pt1 = tuple(pts[i])
                        pt2 = tuple(pts[(i + 1) % len(pts)])
                        
                        if (pt1 in inner_corners and pt2 in inner_corners):
                            if is_main:
                                cv2.arrowedLine(frame, pt1, pt2, (0, 255, 255), 2, tipLength=0.1)
                            angles.append(round(get_angle(pt1, pt2), 2))
                
            # Show Frame
            if is_main:
                cv2.imshow('Corner Calibration', frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

            # Decide next motion
            temp = prev_direction
            if len(angles) > 0 and len(angles) <= 4 and (max_area > 0.5 * frame_area and max_area < 0.85 * frame_area):
                min_dif = 90
                min_angle = angles[0]
                target = prev_direction + 90
                for a in angles:
                    dif = abs(target - a)
                    if dif < min_dif:
                        min_dif = dif
                        min_angle = a

                if prev_direction != min_angle:
                    stage.jog_in_direction(min_angle + 90, quick_stop=False)
                    time.sleep(1.2)
                    for i in range(6):
                        if len(points) > prev_popped_point:
                            points.pop()
                    prev_popped_point = len(points)
                stage.jog_in_direction(min_angle, quick_stop=False)

                prev_direction = min_angle
            else:
                stage.jog_in_direction(prev_direction, quick_stop=False)

            points.append(stage.get_pos()[:2])

    except KeyboardInterrupt:
        pass

    if is_main:
        cv2.destroyAllWindows()
    stage.stop()

    points = np.stack(points, axis=0)
    plt.scatter(points[:,0], points[:,1])

    hull = ConvexHull(points)
    for simplex in hull.simplices:
        plt.plot(points[simplex, 0], points[simplex, 1], 'k-')

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

        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)

        cos_angle = np.clip(np.dot(v1, v2), -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))
        angles.append(angle)

    # Find indices of the 4 most acute angles (smallest angles)
    acute_indices = np.argsort(angles)[:4]

    # Rearrange acute_indices so that the points are in clockwise order starting from the bottom right
    acute_points = hull_pts[acute_indices]

    # Find bottom right (largest x, smallest y)
    start_idx = np.argmax(acute_points[:,1] - acute_points[:,0])  # prioritize largest x, then smallest y
    acute_points_ordered = np.roll(acute_points, start_idx, axis=0)

    # Compute angles for sorting clockwise
    center = np.mean(acute_points_ordered, axis=0)
    angles_cw = np.arctan2(acute_points_ordered[:,1] - center[1], acute_points_ordered[:,0] - center[0])
    acute_points_cw = acute_points_ordered[np.argsort(angles_cw)]  # negative for clockwise

    acute_indices_cw = [np.where((hull_pts == pt).all(axis=1))[0][0] for pt in acute_points_cw]
    acute_indices_cw = np.roll(acute_indices_cw, 2, axis=0)

    if is_main:
        watch.clock()

    if is_main:
        plt.scatter(hull_pts[acute_indices_cw,0], hull_pts[acute_indices_cw,1], color='red')
        plt.show()

    if is_main:
        watch.clock()

    stage.x_motor.setup_velocity(max_velocity=500_000, acceleration=1_000_000)
    stage.y_motor.setup_velocity(max_velocity=500_000, acceleration=1_000_000)

    z_corners = []
    corners = []
    corner_imgs = []
    for i in acute_indices_cw:
        corner = [hull_pts[i, 0], hull_pts[i, 1]]
        lens.rotate_to_position(1)

        stage.move_to(corner, wait=True)
        time.sleep(0.25)
        frame_5x, max_pos = incremental_check(stage.focus_motor, 0, 200, 6000, slope_threshold=-2**(-9), verbose=False, auto_direction=True)

        lens.rotate_to_position(5)
        time.sleep(1)
        frame_10x, max_pos = incremental_check(stage.focus_motor, 0, 50, 2000, slope_threshold=-2**(-8), verbose=False, auto_direction=True)

        z_corners.append(max_pos)
        corners.append(corner)
        corner_imgs.append(frame_5x)

    #  Move to starting point and calculate values
    z0 = z_corners[0]
    stage.move_to([corners[0][0], corners[0][1], z0], wait=False)
    z_corners = [z - z0 for z in z_corners]

    # if is_main:
    print(z_corners)

    corners_arr = np.array(corners)
    side_lengths = [np.linalg.norm(corners_arr[i] - corners_arr[(i+1)%4]) for i in range(4)]
    length = max(side_lengths)
    width = min(side_lengths)

    if is_main:
        print(f"Rectangle length: {length:.2f}, width: {width:.2f}")
        print(f"Rectangle length: {length/610_000:.2f}, width: {width/610_000:.2f}")

    delta_x = corners[1][0] - corners[0][0]
    delta_y = corners[1][1] - corners[0][1]

    angle = 180 - np.rad2deg(np.arctan(delta_y / delta_x))

    if is_main:
        watch.clock()

    if ret_corner_imgs:
        return [z_corners[1:], [length/610_000, width/610_000], angle, stage, lens, corner_imgs, corners]
    else:
        return [z_corners[1:], [length/610_000, width/610_000], angle, stage, lens]

if __name__ == '__main__':
    print(calibrate_corners(True))