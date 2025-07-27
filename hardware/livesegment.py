import cv2
import numpy as np
import os
import sys
sys.path.append('C:/Users/admin/Desktop/2d_World/')
from segmenter2 import Segmenter
from material import graphene
from tqdm import tqdm
from utils import focus_disk
import warnings

warnings.simplefilter('ignore', UserWarning)

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0, # Blue
    'bilayer': np.array([29,255,0])/255.0, # Green
    'trilayer': np.array([198,22,22])/255.0, # Red
    'fewlayer': np.array([255,165,0])/255.0, # Orange
    'manylayer': np.array([255,165,0])/255.0, # Orange
    'bluish_layers': np.array([255,165,0])/255.0, # Orange
    'bulk': np.array([152,7,235])/255.0, # Purple
    'dirt': np.array([0, 0, 0])/255.0, # Uncolored
    'more_bluish_layers': np.array([255, 255, 0])/255.0, # Yellow
    'bg': np.array([0, 0, 0])/255.0, # Uncolored
}



dir = 'C:/Users/admin/Desktop/2d_World/hardware/photo_dir'
result_dir = 'C:/Users/admin/Desktop/2d_World/hardware/results'
result_txt = 'C:/Users/admin/Desktop/2d_World/hardware/results.txt'

def append_to_line(line, arr):
    arr_str = ' '.join(str(x) for x in arr)
    line = line.strip()
    if line:
        return line + ' ' + arr_str + '\n'
    else:
        return arr_str + '\n'

class LiveSegment():
    def __init__(self, input_dir, result_dir, magnification, focus_disks, min_area=1000, grow = 3):
        self.input_dir = input_dir
        self.result_dir = result_dir
        self.magnification = magnification 
        self.focus_disks = focus_disks
        self.min_area = min_area
        self.grow = grow
        if magnification < 50:
            self.segment_edges = True
        else:
            self.segment_edges = False

    def __call__(self, filename):
        g1 = cv2.imread(f'{self.input_dir}/{filename}')
        g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)
        g1 = cv2.resize(g1, (int(g1.shape[1]*self.grow), int(g1.shape[0]*self.grow)))

        segmenter = Segmenter(g1, graphene, colors=colors_by_layer, magnification=self.magnification, min_area=self.min_area, focus_disks=self.focus_disks)
        segmenter.process_frame(segment_edges=self.segment_edges)
        result = segmenter.prettify()
        result = (255 * result).astype(np.uint8)
        result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

        cv2.imwrite(f'{self.result_dir}/{filename}', result)

        mono_size, mono_locations = segmenter.largest_flakes('monolayer')
        bi_size, bi_locations = segmenter.largest_flakes('bilayer')

        if 'test_' in filename:
            i = int(filename[filename.index('_') + 1:filename.index('.')])
            mono_frame_nums = i*np.ones_like(mono_size)
            bi_frame_nums = i*np.ones_like(bi_size)

            if os.path.exists(result_txt):
                with open(result_txt, 'r') as f:
                    lines = f.readlines()

            if mono_locations is not None:
                mono_locations = np.round(mono_locations, 2)
                lines[0] = append_to_line(lines[0], mono_size)
                lines[2] = append_to_line(lines[2], mono_frame_nums)
                lines[4] = append_to_line(lines[4], mono_locations[:, 0])
                lines[5] = append_to_line(lines[5], mono_locations[:, 1])

            if bi_locations is not None:
                bi_locations = np.round(bi_locations, 2)
                lines[1] = append_to_line(lines[1], bi_size)
                lines[3] = append_to_line(lines[3], bi_frame_nums)
                lines[6] = append_to_line(lines[6], bi_locations[:, 0])
                lines[7] = append_to_line(lines[7], bi_locations[:, 1])

            # Write back to results.txt
            with open(result_txt, 'w') as f:
                f.writelines(lines)

        return segmenter