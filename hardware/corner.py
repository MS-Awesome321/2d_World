import cv2
import numpy as np

cap = cv2.VideoCapture('test_video.mp4')
shrink = 2
radius = 6
pad = 50

def get_angle(p1, p2, p3):
    """
    Returns the angle (in degrees) at point p2 formed by p1-p2-p3.
    """
    v1 = p1 - p2
    v2 = p3 - p2
    angle_rad = np.arccos(
        np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1.0, 1.0)
    )
    return np.degrees(angle_rad)

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = frame[100:-100, 300:-260, :]
        frame = cv2.resize(frame, (int(frame.shape[1]/shrink), int(frame.shape[0]/shrink)), cv2.INTER_NEAREST)
        # gray =  cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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

        if corners is not None:
            num_inner_corners = 0
            true_corners = []

            for i in range(len(corners)):
                x, y = corners[i][0]
                if (x > pad and x < frame.shape[1] - pad) or (y > pad and y < frame.shape[0] - pad):
                    num_inner_corners += 1

                    if (x > pad and x < frame.shape[1] - pad) and (y > pad and y < frame.shape[0] - pad):
                        cv2.circle(frame, (x, y), radius, (255, 0, 0), -1)
                        true_corners.append(i)
                    else:
                        cv2.circle(frame, (x, y), radius, (0, 255, 0), -1)
                else:
                    cv2.circle(frame, (x, y), radius, (0, 0, 255), -1)

            # Draw contours 
            if num_inner_corners == 3 and len(true_corners) == 1:
                cv2.drawContours(frame, max_contour, -1, (0, 255, 0), 2)
            else:
                cv2.drawContours(frame, max_contour, -1, (0, 0, 255), 2)

        frame = cv2.putText(frame, 'Corners = '+str(true_corners), org, font, fontScale, color, thickness, cv2.LINE_AA)

        cv2.imshow('Line Test', frame)
        cv2.waitKey(1)

except KeyboardInterrupt:
    pass
cv2.destroyAllWindows()