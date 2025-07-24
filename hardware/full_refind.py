import os
from stage import Stage
import time
from autofocus import incremental_check
import numpy as np
from PIL import ImageGrab
import cv2
from turret import Turret
from tqdm import tqdm
import keyboard

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

m_fnum = lines[2][:-1].split(' ')
m_x, m_y = lines[4][:-1].split(' '), lines[5][:-1].split(' ')

b_fnum = lines[3][:-1].split(' ')
b_x, b_y = lines[6][:-1].split(' '), lines[7][:-1].split(' ')

f_nums = m_fnum + b_fnum
x_s, y_s = m_x + b_x, m_y + b_y

counter = 0

try:
    lens.rotate_to_position(4)

    for i in tqdm(range(len(m_fnum))):
        if keyboard.is_pressed('q'):
            break

        f_num = int(f_nums[i])
        x, y = float(x_s[i]), float(y_s[i])

        coord = get_exact_location(coords[f_num], (x, y), (2265, 4050))
        coord = [int(e) for e in coord.tolist()]
        coord[-1] += -200
        # print(coord)

        test_stage.x_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)
        test_stage.y_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)

        test_stage.move_to(coord)

        final_score1 = incremental_check(test_stage.focus_motor, 0, 5, 800)
        # print(final_score1)

        bgr_frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
        frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        cv2.imwrite(f'{photo_dir}/m_100/m100_{f_num}_{counter}.jpg', frame)
        counter += 1

except KeyboardInterrupt:
    pass

lens.rotate_to_position(5)
test_stage.move_home()