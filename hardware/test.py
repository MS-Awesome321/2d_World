from turret import Turret
from focus import Focus
import sys
# import keyboard
from pylablib.devices import Thorlabs
from stage import Stage
import matplotlib.pyplot as plt
import numpy as np
from search_utils import PhotoShoot, AutoFocus
import cv2

# turret = Turret('COM8')
# print(turret.rotate_to_position(int(sys.argv[1])))
# print(turret.get_pos())

# focus = Focus('COM7')
# focus.rotate_relative(int(sys.argv[1]))


# while True:
#     a = keyboard.read_key()

#     if a == 'q':
#         break

#     for i in range(3):
#         print(a)
    

# while True:
#     key = keyboard.read_event()
#     if key.name =='q':
#         break
#     print(key.name)
#     print(key.event_type)

# x_motor = Thorlabs.KinesisMotor('27503936')
# print(x_motor.get_velocity_parameters())
# x_motor.setup_velocity(max_velocity=20_000, acceleration=518_630)
# print(x_motor.get_velocity_parameters())

<<<<<<< HEAD
# test_stage = Stage('', '', magnification=20, test_mode=True)
# test_stage.set_chip_dims(50,50)
# test_stage.set_direction(45)
# coords = test_stage.get_snake()
# coords = np.stack(coords, axis=0)
=======
test_stage = Stage('', '', magnification=20, test_mode=True)
test_stage.set_chip_dims(50,50)
test_stage.set_direction(45)
coords = test_stage.get_snake()
coords = np.stack(coords, axis=0)
>>>>>>> 673af25 (some tests)

# plt.plot(coords[:,0], coords[:,1])
# plt.show()
    

# ps_test = PhotoShoot(photo_dir='photo_dir')
# img = ps_test.take_photo()
# # print(img)
# # img = cv2.imread('C:/Users/PHY-Wulabmobile1/Desktop/test/2d_World/hardware/photo_dir/photo0.jpg')
# score = cv2.Laplacian(img.astype(np.float32), cv2.CV_32FC1).var()
# score = np.log(score)
# print(score)
# plt.imshow(img)
# plt.show()

af = AutoFocus('COM7')
af()