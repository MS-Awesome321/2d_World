import keyboard
from stage import Stage

x = '27503936'
y = '27503951'
z = '26001791'

test_stage = Stage(x, y, z, 50)

try:
    print('Starting Manual Motor Control')
    print('Press q to end Manual Motor Control')
    if test_stage.start_manual_control('q', focus_comport='COM7', turret_comport='COM8'):
        print('Ended manual control mode.')

except KeyboardInterrupt:
    test_stage.stop()
    print('Stopped Motion.')