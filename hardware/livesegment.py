import cv2
import numpy as np
import os
import sys
sys.path.append('/Users/mayanksengupta/Desktop/2d_World/')
from segmenter2 import Segmenter
from material import graphene
from tqdm import tqdm
from utils import Stopwatch, focus_disk
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



dir = '/Users/mayanksengupta/Desktop/2d_World/hardware/photo_dir'
result_dir = '/Users/mayanksengupta/Desktop/2d_World/hardware/results'
result_txt = '/Users/mayanksengupta/Desktop/2d_World/hardware/results.txt'

monolayer_sizes = np.array([])
mono_frame_nums = np.array([])
bilayer_sizes = np.array([])
bi_frame_nums = np.array([])

filename = sys.argv[1]
g1 = cv2.imread(f'{dir}/{filename}')
shrink = 0.25
f = focus_disk(g1, int(275/shrink), invert=True)

segmenter = Segmenter(g1, graphene, colors=colors_by_layer, magnification=10, min_area=500)
segmenter.process_frame(black_zone_mask=f, segment_edges=True)
result = segmenter.prettify()
result = (255 * result).astype(np.uint8)
result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

cv2.imwrite(f'{result_dir}/{filename}', result)

mono_size = segmenter.largest_flakes('monolayer')
bi_size = segmenter.largest_flakes('bilayer')

if 'test_' in filename:
    i = int(filename[filename.index('_') + 1:filename.index('.')])
    mono_frame_nums = np.concatenate((mono_frame_nums, i*np.ones_like(mono_size)))
    bi_frame_nums = np.concatenate((bi_frame_nums, i*np.ones_like(bi_size)))

    if os.path.exists(result_txt):
        with open(result_txt, 'r') as f:
            lines = f.readlines()
        # Ensure there are 4 lines
        while len(lines) < 4:
            lines.append('\n')
    else:
        lines = ['\n'] * 4

    # Prepare new data as strings
    def append_to_line(line, arr):
        arr_str = ' '.join(str(x) for x in arr)
        line = line.strip()
        if line:
            return line + ' ' + arr_str + '\n'
        else:
            return arr_str + '\n'

    lines[0] = append_to_line(lines[0], mono_size)
    lines[1] = append_to_line(lines[1], bi_size)
    lines[2] = append_to_line(lines[2], mono_frame_nums)
    lines[3] = append_to_line(lines[3], bi_frame_nums)

    # Write back to results.txt
    with open(result_txt, 'w') as f:
        f.writelines(lines)