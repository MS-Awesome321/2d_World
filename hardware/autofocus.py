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

def incremental_check(focus_motor, start, step, max, window_size=5, shrink=2, bbox=(432,137,1782,892), verbose = False, backpedal=False, auto_direction=False, slope_threshold=-0.05):
    focus_motor.rotate_relative(start)
    time.sleep(0.006 * abs(start))

    og_frame = np.array(ImageGrab.grab(bbox=bbox))
    og_frame = cv2.cvtColor(og_frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(og_frame, (int(og_frame.shape[1]/shrink), int(og_frame.shape[0]/shrink)))
    score = np.log(cv2.Laplacian(frame, cv2.CV_32FC1).var())
    first_score = score

    max_score = score
    max_frame = None
    max_pos = None
    min_slope = 0
    i = start
    flipped = False

    if verbose:
        print(i, score, flipped)

    score_window = collections.deque([score], maxlen=window_size)

    while abs(i) < abs(max):
        if keyboard.is_pressed('q'):
            break

        focus_motor.rotate_relative(step)
        time.sleep(0.006 * abs(step))

        og_frame = np.array(ImageGrab.grab(bbox=bbox))
        og_frame = cv2.cvtColor(og_frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(og_frame, (int(og_frame.shape[1]/shrink), int(og_frame.shape[0]/shrink)))
        score = np.log(cv2.Laplacian(frame, cv2.CV_32FC1).var())
        i += step

        if score > max_score:
            max_score = score
            max_frame = og_frame
            max_pos = focus_motor.get_position()

        score_window.append(score)

        if len(score_window) == window_size:
            avg_slope = (score_window[-1] - score_window[0]) / (window_size)

            if verbose:
                print(i, score, avg_slope, flipped)

            if avg_slope < min_slope:
                min_slope = avg_slope

            # if (auto_direction and not flipped) and (score < 1.3 and abs(i) > abs(max / 2)):
            #     step *= -1
            #     flipped = True
            #     score_window = collections.deque([], maxlen=window_size)
            #     time.sleep(0.5)
            
            if avg_slope < slope_threshold:
                if auto_direction and (not flipped and (score < first_score)):
                    step *= -1
                    flipped = True
                    score_window = collections.deque([], maxlen=window_size)
                    time.sleep(0.5)
                else:
                    break


    # Backpedal
    if backpedal:
        s = -1 * step // 4
        if s > 0 and abs(s) < 1:
            s = 1
        elif s < 0 and abs(s) < 1:
            s = -1
            
        for _ in range(max):
            frame = np.array(ImageGrab.grab(bbox=bbox))
            frame = cv2.resize(frame, (int(frame.shape[1]/shrink), int(frame.shape[0]/shrink)))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            score = np.log(cv2.Laplacian(frame, cv2.CV_32FC1).var())

            if verbose:
                print(score)

            if abs(score - max_score) < 0.05:
                break

            focus_motor.rotate_relative(s)
            time.sleep(0.006 * abs(step)) # slowed because of how much slip this motor has

    if max_pos is None:
        max_pos = focus_motor.get_position()
    return max_frame, max_pos

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