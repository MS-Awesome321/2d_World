import os
from stage import Stage

result_txt = 'results.txt'

if os.path.exists(result_txt):
    with open(result_txt, 'r') as f:
        lines = f.readlines()

x = '27503936'
y = '27503951'

test_stage = Stage(x, y, focus_comport='COM5', magnification=10)
test_stage.set_direction(180)
test_stage.set_home()
test_stage.set_chip_dims(1, 1.1)
z_plane = [-2840, -2960, -170]
coords = test_stage.get_snake(z_plane)

def get_exact_location(coord, flake_location, frame_dims):
    coord[0] += 84_600*(flake_location[1]/frame_dims[1] - 0.5)
    coord[1] += 65_400*(flake_location[0]/frame_dims[0] - 0.5)
    return coord

i = 39
coord = get_exact_location(coords[i], (729, 1360), (2020, 3032, 3))
test_stage.move_to(coords)