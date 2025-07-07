import keyboard
from stage import Stage

x = '27503936'
y = '27503951'

test_stage = Stage(x, y, magnification=50)
test_stage.x_motor.setup_velocity(max_velocity=100_000, acceleration=700_000)
test_stage.y_motor.setup_velocity(max_velocity=100_000, acceleration=700_000)

try:
    print('Starting Manual Motor Control')
    print('Press q to end Manual Motor Control')
    if test_stage.start_manual_control('q', focus_comport='COM5', turret_comport='COM7'):
        print('Ended manual control mode.')

except KeyboardInterrupt:
    test_stage.stop()
    print('Stopped Motion.')