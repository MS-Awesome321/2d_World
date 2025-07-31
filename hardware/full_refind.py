import os
from stage import Stage
import time
from autofocus import incremental_check, autofocus
import numpy as np
from PIL import ImageGrab
import cv2
from turret import Turret
from tqdm import tqdm
import keyboard
import sys

result_txt = 'results.txt'
grow = 2

if os.path.exists(result_txt):
    with open(result_txt, 'r') as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        lines[i] = lines[i][lines[i].index(':') + 2 :]

lens = Turret('COM7')

x = '27503936'
y = '27503951'
photo_dir = 'C:/Users/admin/Desktop/2d_World/hardware/photo_dir'

test_stage = Stage(x, y, focus_comport='COM5', magnification=10)
test_stage.set_direction(180)
test_stage.set_home()
test_stage.set_chip_dims(1.7, 0.86)
z_plane = [-3600, -1240, 2170]
test_stage.x_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)
test_stage.y_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)


def get_exact_location(coord, flake_location, frame_dims):
    coord[0] += 103_900*(flake_location[1]/frame_dims[1] - 0.5)
    coord[1] += 57_700*(flake_location[0]/frame_dims[0] - 0.5)
    return coord

coords = np.stack(test_stage.get_snake(z_plane), axis=0)

m_fnum = lines[2][:-1].split(' ')
m_x, m_y = lines[4][:-1].split(' '), lines[5][:-1].split(' ')
m_areas = lines[0][:-1].split(' ')

b_fnum = lines[3][:-1].split(' ')
b_x, b_y = lines[6][:-1].split(' '), lines[7][:-1].split(' ')
b_areas = lines[1][:-1].split(' ')

f_nums = np.array([int(e) for e in m_fnum + b_fnum])
x_s, y_s = np.array([float(e) for e in m_x + b_x]), np.array([float(e) for e in m_y + b_y])
areas = np.array([int(e) for e in m_areas + b_areas])

idxs = np.argsort(areas)[::-1]
max_area = 5000
idxs = idxs[areas[idxs] < max_area]

num_top_matches = int(sys.argv[1])
f_nums = f_nums[idxs][:num_top_matches]
x_s, y_s = x_s[idxs][:num_top_matches], y_s[idxs][:num_top_matches]

poi = coords[f_nums]
z_vals = poi[:, -1]
idxs = np.argsort(z_vals)[::-1]
poi = poi[idxs]
f_nums = f_nums[idxs]
x_s, y_s = x_s[idxs], y_s[idxs]

temp = test_stage.focus_motor.get_pos()
incremental_check(test_stage.focus_motor, 0, 10, 1000, backpedal = True, auto_direction=True, slope_threshold=-0.0125) # Realign focus at the start
test_stage.focus_motor.position = temp

prev_frame = None

try:
    lens.rotate_to_position(4)
    print(f'Home: {test_stage.home_location}')

    for i in tqdm(range(num_top_matches)):
        if keyboard.is_pressed('q'):
            break

        f_num = f_nums[i]
        x, y = x_s[i], y_s[i]

        coord = get_exact_location(poi[i], (x, y), (755 * grow, 1350 * grow))
        coord = [int(e) for e in coord.tolist()]

        if prev_frame is not None and prev_frame == f_num:
            coord[2] = prev_pos + 250
            test_stage.move_to(coord)
        else:
            coord[2] -= 350
            test_stage.move_to(coord)
        prev_frame = f_num

        time.sleep(0.5)
        final_frame, prev_pos = incremental_check(test_stage.focus_motor, 0, 15, 750, slope_threshold=-0.025)

        if final_frame is not None:
            cv2.imwrite(f'{photo_dir}/m_100/m100_{f_num}_{i}.jpg', final_frame)
        else:
            print(f'{f_num} {i} is None')
            prev_pos = coord[2]

except Exception as e:
    print(e)
    pass

lens.rotate_to_position(5)
test_stage.move_home()