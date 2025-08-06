import cv2
import numpy as np

cap = cv2.VideoCapture('test_video.mp4')
shrink = 2
radius = 6
pad = 50

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
            inner_corners = []
            true_corners = []

            for i in range(len(corners)):
                x, y = corners[i][0]
                if (x > pad and x < frame.shape[1] - pad) or (y > pad and y < frame.shape[0] - pad):
                    inner_corners.append((x,y))

                    if (x > pad and x < frame.shape[1] - pad) and (y > pad and y < frame.shape[0] - pad):
                        cv2.circle(frame, (x, y), radius, (255, 0, 0), -1)
                        true_corners.append((x,y))
                    else:
                        cv2.circle(frame, (x, y), radius, (0, 255, 0), -1)
                else:
                    cv2.circle(frame, (x, y), radius, (0, 0, 255), -1)

            # Draw contours 
            if len(inner_corners) == 3 and len(true_corners) == 1:
                cv2.drawContours(frame, max_contour, -1, (0, 255, 0), 2)
            else:
                cv2.drawContours(frame, max_contour, -1, (0, 0, 255), 2)

            # Draw arrows between each adjacent corner point
            pts = corners.reshape(-1, 2)
            for i in range(len(pts)):
                pt1 = tuple(pts[i])
                pt2 = tuple(pts[(i + 1) % len(pts)])
                if pt1 in inner_corners and pt2 in inner_corners:
                    cv2.arrowedLine(frame, pt1, pt2, (0, 255, 255), 2, tipLength=0.2)


        cv2.imshow('Line Test', frame)
        cv2.waitKey(1)

except KeyboardInterrupt:
    pass
cv2.destroyAllWindows()