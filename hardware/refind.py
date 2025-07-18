import os
from stage import Stage
import time
from autofocus import autofocus, incremental_check
import numpy as np
from PIL import ImageGrab
import cv2
from turret import Turret

result_txt = 'results.txt'

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
test_stage.set_chip_dims(1, 1.1)
z_plane = [-2840, -2960, -170]


def get_exact_location(coord, flake_location, frame_dims):
    coord[0] += 84_600*(flake_location[1]/frame_dims[1] - 0.5)
    coord[1] += 65_400*(flake_location[0]/frame_dims[0] - 0.5)
    return coord

coords = test_stage.get_snake(z_plane)
i = 2
f_num = int(lines[2].split(' ')[i])
x, y = float(lines[4].split(' ')[i]), float(lines[5].split(' ')[i])

coord = get_exact_location(coords[f_num], (x, y), (2020, 3032, 3))
coord = [int(e) for e in coord.tolist()]
print(coord)

test_stage.x_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)
test_stage.y_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)

test_stage.move_to(coord)
lens.rotate_to_position(4)

final_score1 = incremental_check(test_stage.focus_motor, 0, 10, 1000)
print(final_score1)

bgr_frame =  np.array(ImageGrab.grab(bbox=(202,205,960,710)))
frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
cv2.imwrite(f'{photo_dir}/m100_{f_num}.jpg', frame)

lens.rotate_to_position(5)
test_stage.move_home()