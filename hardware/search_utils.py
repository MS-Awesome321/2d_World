import numpy as np
import subprocess
import time
import os
import cv2
from focus import Focus
import sys
sys.path.append('C:/Users/admin/Desktop/2d_World/')
from segmenter2 import Segmenter
from material import wte2, graphene, EntropyEdgeMethod
from autofocus import autofocus, color_count_score
from PIL import ImageGrab, Image
import keyboard
import multiprocessing


class GetOptFocus():
    def __init__(self, range):
        self.range = range
        os.chdir('C:/Users/admin/Desktop/2d_World/hardware/photo_dir')
        self.data = []

    def __call__(self, pos, focus_motor):
        high_score = 0
        high_i = None
        start_pos = focus_motor.get_pos()

        for i in self.range:
            focus_motor.move_to(start_pos + i)
            time.sleep(abs(0.0055 * i))
            frame =  np.array(ImageGrab.grab(bbox=(200,200,960,640)))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
            score = np.log(score)
            if score > high_score:
                high_score = score
                high_i = i

        focus_motor.move_to(start_pos)
        self.data.append((pos[0], pos[1], start_pos + high_i))


class WF():
    def __init__(self, photo_dir, take_pic = True, min_blur = 2.5):
        self.take_pic = take_pic
        self.counter = 0
        self.photo_dir = photo_dir
        self.min_blur = min_blur

    def wait_focus_and_click(self, focus_motor=None, n_cols=50, end=False):
        if keyboard.is_pressed('q'):
            raise KeyboardInterrupt

        temp = focus_motor.get_pos()
        d = 1 if self.counter//n_cols % 2 == 0 else -1
        final_score = autofocus(auto_stop=True, q_stop=True, focus=focus_motor, timeup=2, direction=d)
        focus_motor.position = temp

        if self.take_pic:
            bgr_frame =  np.array(ImageGrab.grab(bbox=(202,205,960,710)))
            frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite(f'{self.photo_dir}/test_{self.counter}.jpg', frame)

        self.counter += 1

def sort_results(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    for i in range(len(lines)):
        colon_idx = lines[i].index(':') + 2
        lines[i] = lines[i][colon_idx:-1].split(' ')
        for j in range(len(lines[i])):
            try:
                lines[i][j] = int(lines[i][j])
            except:
                pass
    
    monolayer_sizes = np.array(lines[0])
    bilayer_sizes = np.array(lines[1])
    mono_frame_nums = np.array(lines[2])
    bi_frame_nums = np.array(lines[3])
    mono_locations_x = np.array(lines[4])
    mono_locations_y = np.array(lines[5])
    bi_locations_x = np.array(lines[6])
    bi_locations_y = np.array(lines[7])

    sorted_array = np.argsort(monolayer_sizes)[::-1]
    monolayer_sizes = monolayer_sizes[sorted_array]
    mono_frame_nums = mono_frame_nums[sorted_array]
    mono_locations_x = mono_locations_x[sorted_array]
    mono_locations_y = mono_locations_y[sorted_array]

    sorted_array = np.argsort(bilayer_sizes)[::-1]
    bilayer_sizes = bilayer_sizes[sorted_array]
    bi_frame_nums = bi_frame_nums[sorted_array]
    bi_locations_x = bi_locations_x[sorted_array]
    bi_locations_y = bi_locations_y[sorted_array]

    result_str = f'mono_sizes: {np.array2string(monolayer_sizes, max_line_width=10000)}\nbi_sizes: {np.array2string(bilayer_sizes, max_line_width=10000)}\nmono_frame_nums: {np.array2string(mono_frame_nums, max_line_width=10000)}\nbi_frame_nums: {np.array2string(bi_frame_nums, max_line_width=10000)}\n'
    result_str += f'mono_x: {np.array2string(mono_locations_x, max_line_width=10000)}\nmono_y: {np.array2string(mono_locations_y, max_line_width=10000)}\nbi_x: {np.array2string(bi_locations_x, max_line_width=10000)}\nbi_y: {np.array2string(bi_locations_y, max_line_width=10000)}\n'
    result_str = result_str.replace('[', '').replace(']', '').replace('   ', ' ').replace('  ', ' ').replace("'", "")

    with open(filename, 'w') as f:
        f.writelines(result_str)