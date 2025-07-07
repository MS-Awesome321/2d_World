import numpy as np
from focus import Focus
from PIL import ImageGrab
import cv2
import time

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

focus = Focus('COM5')
focus_speed = 5
min_blur = 4.75
prev_score = None
direction = 1

try:
    while(True):        
        frame =  np.array(ImageGrab.grab(bbox=(200,200,960,640)))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Compute Blur Score
        score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
        score = np.log(score)

        # Overlay Text
        # frame = cv2.putText(frame, 'Blur Factor = '+str(score)+" "+str(prev_score), org, font, fontScale, color, thickness, cv2.LINE_AA)

        if prev_score:
            if score < prev_score:
                direction *= -1
            if score < 2:
                focus_speed = 200
            elif score < 2.5:
                focus_speed = 100
            elif score < 3:
                focus_speed = 25
            elif score < 3.5:
                focus_speed = 12.5
            elif score < 4.25:
                focus_speed = 5
            elif score < 4.5:
                focus_speed = 2.5
            else:
                focus_speed = 0

            focus.rotate_relative(direction * focus_speed)
            time.sleep(0.008 * focus_speed)
        prev_score = score
        
        # cv2.imshow('Python View',frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            raise KeyboardInterrupt
except KeyboardInterrupt:
    print("Exiting...")
    cv2.destroyAllWindows()