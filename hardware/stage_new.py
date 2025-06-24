from stage import Stage

x = '27503936'
y = '27503951'

test_stage = Stage(x, y, 20)

try:
    test_stage.set_direction(180)
    test_stage.set_home()
    test_stage.set_chip_dims(1, 1)

    test_stage.start_snake()

except KeyboardInterrupt:
    test_stage.stop()
    print('Stopped Motion.')


