from turret import Turret
from focus import Focus
import sys
# import keyboard
from pylablib.devices import Thorlabs
from stage import Stage
import matplotlib.pyplot as plt
import numpy as np
# from search_utils import PhotoShoot, AutoFocus
import cv2
import subprocess
import time
import os
from PIL import Image
# import pyautogui as pag

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

test_stage = Stage('', '', magnification=10, test_mode=True)
test_stage.set_chip_dims(1.7,0.86)
test_stage.set_direction(180)
z_plane = [-3000, -3800, -1200]
coords = test_stage.get_snake(z_plane)
coords = np.stack(coords, axis=0)

fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
ax = fig.add_subplot()
print(len(coords[:,0]))
# ax.plot(coords[:,0], coords[:,1], coords[:,2], '-b')
ax.plot(-coords[:,0], coords[:,1], '-bo')
# x, y, z = zip(*[(1, 1, 1000), (2, 2, 3000)])
# ax.plot(x, y, z, '-b')
# ax.scatter(coords[0,0], coords[0,1], coords[0,2], color='green', s=60, label='Start')
# ax.scatter(coords[0,0], coords[0,1], color='green', s=60, label='Start')
# ax.legend()
plt.show()
    

# ps_test = PhotoShoot(photo_dir='photo_dir')
# img = ps_test.take_photo()
# # print(img)
# # img = cv2.imread('C:/Users/PHY-Wulabmobile1/Desktop/test/2d_World/hardware/photo_dir/photo0.jpg')
# score = cv2.Laplacian(img.astype(np.float32), cv2.CV_32FC1).var()
# score = np.log(score)
# print(score)
# plt.imshow(img)
# plt.show()

# af = AutoFocus('photo_dir', 'COM7')
# af()

# gp_shell = subprocess.Popen(
#             ['gphoto2', '--shell'],
#             shell=True,
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             universal_newlines=True,
#             bufsize=1
#         )

# gp_shell.stdin.write('lcd photo_dir \n')


# for i in range(15):
#     if i%5 == 0:
#         for j in range(5):
#             gp_shell.stdin.write('capture-preview \n')
#             while not os.path.isfile('C:/Users/PHY-Wulabmobile1/Desktop/test/2d_World/hardware/photo_dir/capture_preview.jpg'):
#                 time.sleep(0.05)
#             img = Image.open('C:/Users/PHY-Wulabmobile1/Desktop/test/2d_World/hardware/photo_dir/capture_preview.jpg')
#             img = np.array(img)
#             print(img)
#             os.remove('C:/Users/PHY-Wulabmobile1/Desktop/test/2d_World/hardware/photo_dir/capture_preview.jpg')
#     gp_shell.stdin.write('capture-image-and-download \n')

# pag.leftClick(1776, 280)
# pag.leftClick(1776, 280)

# pag.leftClick(1794, 230)
# pag.leftClick(1794, 230)

# while True:
#     print(pag.displayMousePosition())
#     time.sleep(0.05)

# for i in range(10):
#     print(i)
#     time.sleep(1.5)