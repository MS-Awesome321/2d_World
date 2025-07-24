import numpy as np
from focus import Focus
from PIL import ImageGrab
import cv2
import keyboard
import time
import collections

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

def incremental_check(focus_motor, start, step, max, window_size=10, shrink=2, bbox=(432,137,1782,892)) -> float:
    focus_motor.rotate_relative(start)
    time.sleep(0.006 * abs(start))

    frame = np.array(ImageGrab.grab(bbox=bbox))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    score = np.log(cv2.Laplacian(frame, cv2.CV_32FC1).var())

    max_score = score
    max_pos = focus_motor.get_position()
    i = start

    # Use a deque for a moving window of scores
    score_window = collections.deque([score], maxlen=window_size)

    while abs(i) < abs(max):
        focus_motor.rotate_relative(step)
        time.sleep(0.006 * abs(step))

        frame = np.array(ImageGrab.grab(bbox=bbox))
        frame = cv2.resize(frame, (int(frame.shape[1]/shrink), int(frame.shape[0]/shrink)))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        score = np.log(cv2.Laplacian(frame, cv2.CV_32FC1).var())
        i += step

        score_window.append(score)
        avg_prev = sum(list(score_window)[:-1]) / (len(score_window)-1) if len(score_window) > 1 else score

        # print(i, score, avg_prev)

        if score > max_score:
            max_score = score
            max_pos = focus_motor.get_position()

        # If the current score is less than the average of previous scores, break (downward trend)
        if len(score_window) == window_size and score < avg_prev - 0.025:
            break

    focus_motor.move_to(max_pos)
    time.sleep(1)
    return max_score

def autofocus(auto_stop = False, focus=None, q_stop=False, timeup = 2, direction = 1, change_factor = 1, shrink=2, bbox=(432,137,1782,892)):
    focus_speed = 5
    prev_score = None
    timer = 0
    ok_blur = 4.5

    while(True):        
        frame =  np.array(ImageGrab.grab(bbox=bbox))
        frame = cv2.resize(frame, (int(frame.shape[1]/shrink), int(frame.shape[0]/shrink)))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if q_stop and keyboard.is_pressed('q'):
            return 0

        # Compute Blur Score
        score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
        score = np.log(score)

        # Overlay Text
        # frame = cv2.putText(frame, 'Blur Factor = '+str(score)+" "+str(prev_score), org, font, fontScale, color, thickness, cv2.LINE_AA)

        if prev_score:
            if prev_score > score + 0.005:
                direction *= -1
            
            if score < 1.9:
                focus_speed = 750
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
                    return score

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