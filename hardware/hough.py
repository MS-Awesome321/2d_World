import cv2
from PIL import ImageGrab
import numpy as np
 
shrink = 4
# cut = 5
radius = 5

try:
    while(True):        
        raw_frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
        raw_frame = cv2.resize(raw_frame, (int(raw_frame.shape[1]/shrink), int(raw_frame.shape[0]/shrink)), cv2.INTER_NEAREST)
        frame = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)
        # frame = frame[frame.shape[0]//cut : (cut - 1)*frame.shape[0]//cut, frame.shape[1]//cut : (cut - 1)*frame.shape[1]//cut]

        # Find Lines
        gray =  cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
        # blurred = cv2.blur(gray, (5,5))
        # edges = cv2.Canny(gray,50,150,apertureSize = 3)
        # lines = cv2.HoughLines(edges,1,np.pi/36,35)

        # # Overlay Lines
        # if lines is not None:
        #     for line in lines:
        #         rho,theta = line[0]
        #         a = np.cos(theta)
        #         b = np.sin(theta)
        #         x0 = a*rho
        #         y0 = b*rho
        #         x1 = int(x0 + 1000*(-b))
        #         y1 = int(y0 + 1000*(a))
        #         x2 = int(x0 - 1000*(-b))
        #         y2 = int(y0 - 1000*(a))
            
        #         cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)

        ret, thresh_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Find contours
        contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_contour = None
        for contour in contours:
            a = cv2.contourArea(contour)
            if a > max_area:
                max_area = a
                max_contour = contour

        perimeter = cv2.arcLength(max_contour, True)
        corners = cv2.approxPolyDP(max_contour, 0.03 * perimeter, True)

        # Draw contours 
        cv2.drawContours(frame, max_contour, -1, (0, 255, 0), 2)


        # corners = cv2.goodFeaturesToTrack(thresh_image, maxCorners=50, qualityLevel=0.01, minDistance=50, useHarrisDetector=True, k=0.2)
        if corners is not None:
            for corner in corners:
                x, y = corner[0]
                cv2.circle(frame, (x, y), radius, (255, 0, 0), -1)


        cv2.imshow('Line Test', frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            raise KeyboardInterrupt
        
except KeyboardInterrupt:
    print("Exiting...")
    cv2.destroyAllWindows()