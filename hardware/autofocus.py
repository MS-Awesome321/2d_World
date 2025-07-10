import numpy as np
from focus import Focus
from PIL import ImageGrab
import cv2
import keyboard
import time

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

def color_count_score(img, bins=16, shrink = 4):
    """
    Estimates the amount of different colors in an RGB image.
    The score increases as the number of distinct colors increases.
    """

    img = cv2.resize(img, (int(img.shape[1]/shrink), int(img.shape[0]/shrink)), cv2.INTER_NEAREST)
    pixels = img.reshape(-1, 3)
    quantized = (pixels // (256 // bins)).astype(np.uint8)
    unique_colors = np.unique(quantized, axis=0)
    
    return len(unique_colors)

def autofocus(auto_stop = False, focus=None, q_stop=False, timeup = 2, direction = 1):
    focus_speed = 5
    prev_score = None
    timer = 0
    ok_blur = 4.5

    while(True):        
        frame =  np.array(ImageGrab.grab(bbox=(200,200,960,640)))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if q_stop and keyboard.is_pressed('q'):
            return True

        # Compute Blur Score
        score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
        score = np.log(score)

        # Overlay Text
        # frame = cv2.putText(frame, 'Blur Factor = '+str(score)+" "+str(prev_score), org, font, fontScale, color, thickness, cv2.LINE_AA)

        if auto_stop and color_count_score(frame, 4) < 14:
            return False

        if prev_score:
            if score < prev_score:
                direction *= -1
            
            if score < 1.9:
                focus_speed = 2000
            if score < 2.15:
                focus_speed = 200
            if score < 2.25:
                focus_speed = 100
            elif score < 2.5:
                focus_speed = 75
            elif score < 3:
                focus_speed = 50
            elif score < 3.5:
                focus_speed = 25
            elif score < 4.25:
                focus_speed = 12
            elif score < 4.5:
                focus_speed = 6
            else:
                focus_speed = 0
                if auto_stop:
                    return True

            focus.rotate_relative(direction * focus_speed)
            time.sleep(0.0055 * focus_speed)
        prev_score = score
        
        # cv2.imshow('Python View',frame)

        if auto_stop and timer > timeup:
            cv2.destroyAllWindows()
            return True

        timer += 1

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            raise KeyboardInterrupt
        
if __name__=='__main__':
    try:
        focus = Focus('COM5')
        if autofocus(focus=focus, q_stop=True):
            print(focus.get_pos())
    except KeyboardInterrupt:
        print("Exiting...")
        cv2.destroyAllWindows()