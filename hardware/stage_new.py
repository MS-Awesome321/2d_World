from stage import Stage
from focus import Focus
import matplotlib.pyplot as plt
import numpy as np
from search_utils import PhotoShoot, TestSegment, Shoot_Focus, WF
import os

x = '27503936'
y = '27503951'

test_stage = Stage(x, y, focus_comport='COM5', magnification=10)

try:
    test_stage.set_direction(180)
    test_stage.set_home()
    test_stage.set_chip_dims(6.5, 6.75)
    test_stage.x_motor.setup_velocity(max_velocity=1_000_000, acceleration=1_000_000)
    test_stage.y_motor.setup_velocity(max_velocity=1_000_000, acceleration=1_000_000)

    # coords = test_stage.get_snake()
    # coords = np.stack(coords, axis=0)c
    # coords = np.stack(coords, axis=0)

    # print(coords.shape)
    # plt.plot(coords[:,0], coords[:,1], '-o')
    # plt.show()

    # test_stage.start_snake(TestSegment(photo_dir='photo_dir', filename='segment_img'))
    wf = WF(min_blur = 3.5, take_pic=True, min_colors=12)
    z_corners = [-2980, -3380, -470]
    # z_corners = [0,0,0]
    test_stage.start_snake(z_corners=z_corners, wf = wf.wait_focus_and_click)
    # test_stage.start_snake(z_corners=z_corners)


except KeyboardInterrupt:
    pass
test_stage.stop()
test_stage.move_home()
print('Stopped Motion.')


