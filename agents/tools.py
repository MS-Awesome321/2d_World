from smolagents import tool
import sys
sys.path.append('/Users/mayanksengupta/Desktop/2d_World/hardware/')
from go import autosearch
from corner import calibrate_corners

autosearch_tool = tool(autosearch)
calibrate_corners_tool = tool(calibrate_corners)

@tool
def chip_processing_tool() -> tuple[str]:
    '''
    Runs both steps of chip scanning in one function:
        1. Calibrating corners
        2. Autosearching
    
    Returns:
        result_paths: Paths to the results of the snake scan and the 100x flake verification steps 
            respectively, structured [result_txt, result_txt_m100]. 
    '''

    z_corners, chip_dims, angle = calibrate_corners()
    return autosearch(z_corners, angle, chip_dims, num_top_matches = 25)