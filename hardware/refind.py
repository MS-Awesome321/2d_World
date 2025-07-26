import os
from stage import Stage
import time
from autofocus import autofocus, incremental_check
import numpy as np
from PIL import ImageGrab
import cv2
from turret import Turret
import sys
sys.path.append('C:/Users/admin/Desktop/2d_World/')
from utils import Stopwatch

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
test_stage.set_chip_dims(1.7, 0.86)
z_plane = [-4480, -5250, -830]


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

watch = Stopwatch()

coord = get_exact_location(coords[f_num], (x, y), (2265, 4050))
coord = [int(e) for e in coord.tolist()]
print(coord)

test_stage.x_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)
test_stage.y_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)

watch.clock()
test_stage.move_to(coord)
watch.clock()

# temp = test_stage.focus_motor.get_pos()
# d = 1 if (test_stage.home_location[-1] - coord[-1] > 0) else -1
# final_score = autofocus(auto_stop=True, q_stop=True, focus=test_stage.focus_motor, timeup=5, change_factor=0.125, direction=d)
# test_stage.focus_motor.position = temp

lens.rotate_to_position(4)

watch.clock()
time.sleep(1)
final_frame = incremental_check(test_stage.focus_motor, 0, 5, 1000)
watch.clock()

cv2.imwrite(f'{photo_dir}/m100_{f_num}.jpg', final_frame)

cv2.namedWindow("M100", cv2.WINDOW_NORMAL)
cv2.imshow('M100', final_frame)
cv2.waitKey(0)
print(f_num)

lens.rotate_to_position(5)
test_stage.move_home()