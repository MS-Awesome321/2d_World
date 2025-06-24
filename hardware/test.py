from turret import Turret
from focus import Focus
import sys
# import keyboard
from pylablib.devices import Thorlabs
from stage import Stage
import matplotlib.pyplot as plt
import numpy as np

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

x_motor = Thorlabs.KinesisMotor('27503936')
print(x_motor.get_jog_parameters())
x_motor.setup_jog(acceleration=518630)
print(x_motor.get_jog_parameters())

# test_stage = Stage('', '', magnification=20, test_mode=True)
# test_stage.set_chip_dims(50,50)
# test_stage.set_direction(90)
# coords = test_stage.get_snake()
# coords = np.stack(coords, axis=0)

# plt.plot(coords[:,0], coords[:,1])
# plt.show()