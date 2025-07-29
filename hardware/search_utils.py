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
from turret import Turret
from autofocus import incremental_check

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
            frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
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
        final_score = autofocus(auto_stop=True, q_stop=True, focus=focus_motor, timeup=2, direction=d, change_factor=0.25)
        focus_motor.position = temp

        if self.take_pic:
            bgr_frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
            frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite(f'{self.photo_dir}/test_{self.counter}.jpg', frame)

        self.counter += 1

class WF_M100():
    def __init__(self, photo_dir, turret_comport, take_pic = True, min_blur = 2.5, result_txt='results.txt'):
        self.take_pic = take_pic
        self.counter = 0
        self.photo_dir = photo_dir
        self.min_blur = min_blur
        self.result_txt = result_txt
        self.checked_x = []
        self.lens = Turret(turret_comport)

    def wait_focus_and_click(self, stage, coords, current_coord, focus_motor=None, n_cols=50, end=False):
        if keyboard.is_pressed('q'):
            raise KeyboardInterrupt

        temp = focus_motor.get_pos()
        d = 1 if self.counter//n_cols % 2 == 0 else -1
        final_score = autofocus(auto_stop=True, q_stop=True, focus=focus_motor, timeup=5, direction=d, change_factor=0.25)
        focus_motor.position = temp

        if self.take_pic:
            bgr_frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
            frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite(f'{self.photo_dir}/test_{self.counter}.jpg', frame)

        time.sleep(1)

        with open(self.result_txt, 'r') as f:
            lines = f.readlines()
        
        for i in range(len(lines)):
            lines[i] = lines[i][lines[i].index(':') + 2 :]
        
        m_fnum = lines[2][:-1].split(' ')
        m_x, m_y = lines[4][:-1].split(' '), lines[5][:-1].split(' ')

        b_fnum = lines[3][:-1].split(' ')
        b_x, b_y = lines[6][:-1].split(' '), lines[7][:-1].split(' ')

        f_nums = m_fnum + b_fnum
        x_s, y_s = m_x + b_x, m_y + b_y

        new_fnums = []
        new_xs = []
        new_ys = []

        for e in f_nums:
            try:
                new_fnums.append(int(e))
            except:
                pass
        f_nums = new_fnums

        for e in x_s:
            try:
                new_xs.append(int(e))
            except:
                pass
        x_s = new_xs


        for e in y_s:
            try:
                new_ys.append(int(e))
            except:
                pass
        y_s = new_ys

        new_x_idx = []
        for i in range(len(x_s)):
            if x_s[i] not in self.checked_x:
                new_x_idx.append(i)
                self.checked_x.append(x_s[i])

        for i in new_x_idx:
            print(i, f_nums[i], x_s[i], y_s[i])
            coord = get_exact_location(coords[f_nums[i]], (x_s[i], y_s[i]), (2265, 4050))
            coord[-1] -= 200
            stage.move_to(coord)
            if self.lens.position != 4:
                self.lens.rotate_to_position(4)
            final_score1 = incremental_check(focus_motor, 0, 5, 800)

            bgr_frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
            frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite(f'{self.photo_dir}/m_100/m100_{f_nums[i]}_{i}.jpg', frame)

        stage.move_to(current_coord)
        if self.lens.position != 5:
            self.lens.rotate_to_position(5)

        self.counter += 1

def clear_results(filename):
    result_str = f'mono_sizes: \nbi_sizes: \nmono_frame_nums: \nbi_frame_nums: \nmono_x: \nmono_y: \nbi_x: \nbi_y: \n'

    with open(filename, 'w') as f:
        f.writelines(result_str)

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

def get_exact_location(coord, flake_location, frame_dims):
    coord[0] += 103_900*(flake_location[1]/frame_dims[1] - 0.5)
    coord[1] += 57_700*(flake_location[0]/frame_dims[0] - 0.5)
    return coord