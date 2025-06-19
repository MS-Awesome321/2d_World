from stage import Stage

x = '27503936'
y = '27503951'
z = '26001791'

test_stage = Stage(x, y, z, 50)

test_stage.set_direction(0)
test_stage.set_home()
test_stage.set_chip_dims(10, 10)

test_stage.start_snake()



