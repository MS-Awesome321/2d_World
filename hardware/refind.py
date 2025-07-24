import os
from stage import Stage
import time
from autofocus import autofocus, incremental_check
import numpy as np
from PIL import ImageGrab
import cv2
from turret import Turret
import sys

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
z_plane = [-1520, -3450, -1900]


def get_exact_location(coord, flake_location, frame_dims):
    coord[0] += 103_900*(flake_location[1]/frame_dims[1] - 0.5)
    coord[1] += 57_700*(flake_location[0]/frame_dims[0] - 0.5)
    return coord

coords = test_stage.get_snake(z_plane)
try:
    i = int(sys.argv[1])
    mono_bi = sys.argv[2]
except:
    i = 0

if 'm' in mono_bi:
    f_num = int(lines[2].split(' ')[i])
    x, y = float(lines[4].split(' ')[i]), float(lines[5].split(' ')[i])
elif 'b' in mono_bi:
    f_num = int(lines[3].split(' ')[i])
    x, y = float(lines[6].split(' ')[i]), float(lines[7].split(' ')[i])
else:
    raise ValueError('Bad argument for monolayer/bilayer')

coord = get_exact_location(coords[f_num], (x, y), (2265, 4050))
coord = [int(e) for e in coord.tolist()]
print(coord)

test_stage.x_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)
test_stage.y_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)

test_stage.move_to(coord)
lens.rotate_to_position(4)

final_score1 = incremental_check(test_stage.focus_motor, 0, 5, 1000)
print(final_score1)

bgr_frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
cv2.imwrite(f'{photo_dir}/m100_{f_num}.jpg', frame)

lens.rotate_to_position(5)
test_stage.move_home()