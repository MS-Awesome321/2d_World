from stage import Stage
import matplotlib.pyplot as plt
import numpy as np

x = '27503936'
y = '27503951'

test_stage = Stage(x, y, 20)

try:
    test_stage.set_direction(180)
    test_stage.set_home()
    test_stage.set_chip_dims(7, 7)
    test_stage.x_motor.setup_velocity(max_velocity=5_000, acceleration=500_000)
    test_stage.y_motor.setup_velocity(max_velocity=15_000, acceleration=500_000)

    # coords = test_stage.get_snake()
    # coords = np.stack(coords, axis=0)

    # plt.plot(coords[:,0], coords[:,1])
    # plt.show()

    test_stage.start_snake()

except KeyboardInterrupt:
    test_stage.stop()
    print('Stopped Motion.')


