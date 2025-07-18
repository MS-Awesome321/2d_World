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

def incremental_check(focus_motor, start, step, max) -> float:
    focus_motor.rotate_relative(start)
    time.sleep(0.0055 * abs(start))

    frame =  np.array(ImageGrab.grab(bbox=(202,205,960,710)))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
    score = np.log(score)

    prev_score = 0
    max_score = 0
    max_pos = None

    i = start
    while prev_score < score + 0.025 and abs(i) < abs(max):
        prev_score = score

        focus_motor.rotate_relative(step)
        time.sleep(0.0055 * abs(step))

        frame =  np.array(ImageGrab.grab(bbox=(202,205,960,710)))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
        score = np.log(score)
        i += step

        print(i, score, prev_score)
        if score > max_score:
            max_score = score
            max_pos = focus_motor.get_position()

    focus_motor.move_to(max_pos)
    time.sleep(1)
    return score

def autofocus(auto_stop = False, focus=None, q_stop=False, timeup = 2, direction = 1, change_factor = 1):
    focus_speed = 5
    prev_score = None
    timer = 0
    ok_blur = 4.5

    while(True):        
        frame =  np.array(ImageGrab.grab(bbox=(202,205,960,710)))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if q_stop and keyboard.is_pressed('q'):
            return True

        # Compute Blur Score
        score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
        score = np.log(score)

        # Overlay Text
        # frame = cv2.putText(frame, 'Blur Factor = '+str(score)+" "+str(prev_score), org, font, fontScale, color, thickness, cv2.LINE_AA)

        if prev_score:
            if score < prev_score:
                direction *= -1
            
            if score < 1.9:
                focus_speed = 500
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

            focus.rotate_relative(change_factor * direction * focus_speed)
            time.sleep(0.0055 * focus_speed)
        prev_score = score
        
        # cv2.imshow('Python View',frame)

        if auto_stop and timer > timeup:
            cv2.destroyAllWindows()
            return score

        timer += 1

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            raise KeyboardInterrupt
        
if __name__=='__main__':
    try:
        focus = Focus('COM5')
        import sys
        try:
            r = float(sys.argv[1])
        except:
            r = 1
        if autofocus(focus=focus, q_stop=True, change_factor=r):
            print(focus.get_pos())
    except KeyboardInterrupt:
        print("Exiting...")
        cv2.destroyAllWindows()