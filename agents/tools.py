from smolagents import tool
from typing import List, Any
import sys
import os
import time
# Add the hardware directory to the Python path using relative path
current_dir = os.path.dirname(os.path.abspath(__file__))
hardware_dir = os.path.join(os.path.dirname(current_dir), 'hardware')
sys.path.append(hardware_dir)
from go import autosearch
from corner import calibrate_corners
import subprocess

@tool
def calibrate_corners_tool(is_main: bool = False) -> List[Any]:
    """
    Calibrates the silicon chip corners and focus for microscope scanning.
    This tool traces the edges of a silicon chip under the microscope to find corners
    and calibrates the microscope focus at 10x magnification for each corner.
    IMPORTANT: This MUST be run before autosearch_tool each time a new chip is placed
    under the microscope.
    Args:
        is_main: Set to True to display OpenCV windows with internal computations.
                Default is False for normal operation.
    """
    return calibrate_corners()

@tool
def autosearch_tool(z_corners: List[int], angle: int, chip_dims: List[int], num_top_matches: int = 25) -> List[str]:
    """
    Searches silicon chip for monolayer and bilayer flakes using automated scanning.
    This tool performs a snake scan of the full chip at 10x magnification, then returns
    to the largest flakes and images them at 100x magnification for verification.
    PREREQUISITE: Must run calibrate_corners_tool first to get required parameters.
    Args:
        z_corners: List of 3 integers for z-values [bottom_left, top_left, top_right]
                  (from calibrate_corners_tool)
        angle: Scan angle in degrees counterclockwise from x-axis (from calibrate_corners_tool)
        chip_dims: List of chip dimensions [length, width] in inches (from calibrate_corners_tool)
        num_top_matches: Number of largest flakes to image at 100x (default: 25)
    """
    return autosearch(z_corners, angle, chip_dims, num_top_matches)

@tool
def chip_processing_tool() -> List[str]:
    '''
    Runs both steps of chip scanning in one function:
        1. Calibrating corners
        2. Autosearching
    Returns:
        result_paths: Paths to the results of the snake scan and the 100x flake verification steps
            respectively, structured [result_txt, result_txt_m100].
    '''

    z_corners, chip_dims, angle, stage, lens = calibrate_corners(False)

    time.sleep(1)

    current_dir = os.getcwd().replace('\\', '/')
    photo_dir = f'{current_dir}/photo_dir_{time.time()}'
    os.mkdir(photo_dir)
    os.mkdir(f'{photo_dir}/m_100')

    result_dir = f'{current_dir}/results_{time.time()}'
    os.mkdir(result_dir)
    os.mkdir(f'{result_dir}/m_100')

    result_txt =  f'{current_dir}/results.txt'
    results_m100 = f'{current_dir}/results100.txt'

    obs1 = subprocess.Popen(['python', '../hardware/observer.py', '10', photo_dir, result_dir, result_txt])
    obs2 = subprocess.Popen(['python', '../hardware/observer.py', '100', f'{photo_dir}/m_100', f'{result_dir}/m_100', results_m100])
    print('Both processes running')

    result = autosearch(z_corners, angle, chip_dims, num_top_matches = 25, stage = stage, lens = lens, photo_dir=photo_dir)

    obs1.terminate()
    obs2.terminate()

    return result


