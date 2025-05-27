# pip install pylablib
# pip install --user --upgrade thorlabs-apt-device

# from pylablib.devices import Thorlabs
# import ft232

# motors = Thorlabs.list_kinesis_devices()
# print(motors)

# stage = Thorlabs.KinesisMotor(motors[0])
# stage._move_by(20)

# while stage.is_moving():
#     print("moving")

# stage.close()

from thorlabs_apt_device.devices.kdc101 import KDC101
from thorlabs_apt_device.devices.aptdevice import list_devices, APTDevice
from thorlabs_apt_device.devices.aptdevice_motor import APTDevice_Motor
import time

# print(list_devices())

stage = KDC101(pid='0xfaf0')
print(stage.status)
stage.identify()
# stage.set_jog_params(max_velocity=10, acceleration=10, size=10)
stage.move_relative(20000)
time.sleep(1)
print(stage.status)
stage.close()

# stage.move_jog(direction='forward')
# print(stage.status)
# time.sleep(5)
# stage.stop()
# stage.close()