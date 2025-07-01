from stage import Stage
from focus import Focus
import matplotlib.pyplot as plt
import numpy as np
from search_utils import PhotoShoot, TestSegment, Shoot_Focus, WF
import os

x = '27503936'
y = '27503951'

test_stage = Stage(x, y, 20)
os.chdir('C:/Users/PHY-Wulabmobile1/Desktop/test/2d_World/hardware')

try:
    test_stage.set_direction(180)
    test_stage.set_home()
    test_stage.set_chip_dims(7, 7)
    test_stage.x_motor.setup_velocity(max_velocity=60_000, acceleration=700_000)
    test_stage.y_motor.setup_velocity(max_velocity=60_000, acceleration=700_000)

    # coords = test_stage.get_snake()
    # coords = np.stack(coords, axis=0)c
    # coords = np.stack(coords, axis=0)

    # print(coords.shape)
    # plt.plot(coords[:,0], coords[:,1], '-o')
    # plt.show()

    # test_stage.start_snake(TestSegment(photo_dir='photo_dir', filename='segment_img'))
    wf = WF(min_blur = 3.5, wait_frames=35)
    test_stage.start_snake([wf.wait_focus_and_click])

except KeyboardInterrupt:
    test_stage.stop()
    print('Stopped Motion.')


