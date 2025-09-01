from stage import Stage
from search_utils import WF, WF_M100, sort_results, clear_results
from autofocus import incremental_check
from turret import Turret
import keyboard
import cv2
import numpy as np
import time
from tqdm import tqdm
import sys
import os
from typing import List

def autosearch(z_corners: List[int], angle: int, chip_dims:List[float], num_top_matches: int = 25, stage: Stage = None, lens: Turret = None, photo_dir: str = 'C:/Users/admin/Desktop/2d_World/hardware/photo_dir', is_main: bool = False) -> tuple[str]:
    '''
    Searches a silicon chip for monolayer and bilayer flakes. 
    First performs an snake scan of the full chip at 10x magnification
    Then returns to the largest monolayer and bilayer flakes and images them at 100x magnification
    to verify whether or not they are truly useful flakes.
    Finally returns a list of two paths to the text files logging the areas and positions of the 
    largest monolayer and bilayer flakes at 10x and 100x respectively.

    Arguments:
        z_corners: A list of 3 integers representing the z-values of the bottom left, top left, and
            top right corners in that order, with the z-value for the bottom right corner
            (fixed as the origin) assumed to be 0.

        angle: The angle, measured counterclockwise from the x-axis, at which the snake scan
            should proceed from the origin.

        chip_dims: The length and width of the chip to be scanned, in inches.

        num_top_matches: The number of the largest flakes to image at 100x after the snake scan.

        stage: Stage object to manipulate during autosearch. Defaults to a new 
            Stage(x, y, focus_comport='COM5', magnification=10)

        lens: Turret object to manipulate during autosearch and flake refinding. Defaults to a new
            Turret('COM7)

        is_main: Only set to True if run independently of other functions.

    Returns:
        result_paths: Paths to the results of the snake scan and the 100x flake verification steps 
            respectively, structured [result_txt, result_txt_m100].
    '''
    
    # Set up Motors
    grow = 2
    max_area = 5000
    result_txt = 'results.txt'
    result_txt_m100 = 'results100.txt'

    if stage is None:
        x = '27503936'
        y = '27503951'
        stage = Stage(x, y, focus_comport='COM5', magnification=10)

    if lens is None:
        lens = Turret('COM7')

    # AUTOSEARCH
    try:
        # Set Home, Direction, and Chip Corners
        stage.set_direction(angle)
        stage.set_home()
        print(f'Home: {stage.home_location}')
        print(chip_dims)
        stage.set_chip_dims(*chip_dims)
        stage.x_motor.setup_velocity(max_velocity=1_000_000, acceleration=2_000_000)
        stage.y_motor.setup_velocity(max_velocity=1_000_000, acceleration=2_000_000)

        # Ensure Optimal Camera Focus
        temp = stage.focus_motor.get_pos()
        incremental_check(stage.focus_motor, 0, 10, 1000, backpedal = True, auto_direction=True, slope_threshold=-2**(-8)) # Realign focus at the start
        if is_main:
            stage.focus_motor.position = temp
        else:
            stage.focus_motor.position = 0

        # Perform Autosearch
        wf = WF(photo_dir, take_pic=True)
        clear_results('results.txt')
        print(z_corners)
        stage.start_snake(z_corners=z_corners, wf = wf.wait_focus_and_click)


    except KeyboardInterrupt:
        pass

    stage.stop()
    stage.move_home()
    print('Stopped Motion.')

    # Sort and organize 10x results for refinding
    sort_results(result_txt)

    if os.path.exists(result_txt):
        with open(result_txt, 'r') as f:
            lines = f.readlines()
        
        for i in range(len(lines)):
            lines[i] = lines[i][lines[i].index(':') + 2 :]

    stage.x_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)
    stage.y_motor.setup_velocity(max_velocity=4_000_000, acceleration=8_000_000)


    def get_exact_location(coord, flake_location, frame_dims):
        coord[0] += 103_900*(flake_location[1]/frame_dims[1] - 0.5)
        coord[1] += 57_700*(flake_location[0]/frame_dims[0] - 0.5)
        return coord

    coords = np.stack(stage.coords, axis=0)

    m_fnum = lines[2][:-1].split(' ')
    m_x, m_y = lines[4][:-1].split(' '), lines[5][:-1].split(' ')
    m_areas = lines[0][:-1].split(' ')

    b_fnum = lines[3][:-1].split(' ')
    b_x, b_y = lines[6][:-1].split(' '), lines[7][:-1].split(' ')
    b_areas = lines[1][:-1].split(' ')

    f_nums = np.array([int(e) for e in m_fnum + b_fnum])
    x_s, y_s = np.array([float(e) for e in m_x + b_x]), np.array([float(e) for e in m_y + b_y])
    areas = np.array([int(e) for e in m_areas + b_areas])

    idxs = np.argsort(areas)[::-1]
    idxs = idxs[areas[idxs] < max_area]
    f_nums = f_nums[idxs][:num_top_matches]
    x_s, y_s = x_s[idxs][:num_top_matches], y_s[idxs][:num_top_matches]

    poi = coords[f_nums]
    z_vals = poi[:, -1]
    idxs = np.argsort(z_vals)[::-1]
    poi = poi[idxs]
    f_nums = f_nums[idxs]
    x_s, y_s = x_s[idxs], y_s[idxs]

    # Ensure Optimal Camera Focus
    temp = stage.focus_motor.get_pos()
    incremental_check(stage.focus_motor, 0, 10, 1000, backpedal = True, auto_direction=True, slope_threshold=-2**(-8)) # Realign focus at the start
    stage.focus_motor.position = temp

    # FLAKE REFINDING
    try:
        prev_frame = None
        lens.rotate_to_position(4)
        clear_results(result_txt_m100)

        for i in tqdm(range(num_top_matches)):
            if keyboard.is_pressed('q'):
                break

            f_num = f_nums[i]
            x, y = x_s[i], y_s[i]

            coord = get_exact_location(poi[i], (x, y), (755 * grow, 1350 * grow))
            coord = [int(e) for e in coord.tolist()]

            if prev_frame is not None and prev_frame == f_num:
                coord[2] = prev_pos + 200
                stage.move_to(coord, wait=True)
            else:
                coord[2] -= 20
                stage.move_to(coord, wait=True)
            prev_frame = f_num

            time.sleep(0.5)
            final_frame, prev_pos = incremental_check(stage.focus_motor, 0, 15, 1000, slope_threshold=-2**(-6))

            if final_frame is not None:
                cv2.imwrite(f'{photo_dir}/m_100/m100_{f_num}_{i}.jpg', final_frame)
            else:
                print(f'{f_num} {i} is None')
                prev_pos = coord[2]

    except Exception as e:
        print(e)
        pass

    lens.rotate_to_position(5)
    stage.move_home()

    # Sort and organize 10x results for refinding
    sort_results(result_txt_m100)

    return [result_txt, result_txt_m100]

if __name__ == '__main__':
    z_corners = [-4290, -5920, -960]
    angle = 180
    chip_dims = [1.7, 0.91]
    print(autosearch(z_corners=z_corners, angle=angle, chip_dims=chip_dims, num_top_matches=int(sys.argv[1]), is_main=True))