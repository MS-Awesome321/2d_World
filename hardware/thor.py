# pip install pylablib

from pylablib.devices import Thorlabs

motors = Thorlabs.list_kinesis_devices()
print(motors)

stage = Thorlabs.KinesisMotor(motors[0])
stage._move_by(20)

while stage.is_moving():
    print("moving")

stage.close()