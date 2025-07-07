import sys
import cv2
import numpy as np
sys.path.append('C:/Users/admin/Desktop/2d_World/')
from segmenter2 import Segmenter
from material import wte2, graphene
import time
import os
from PIL import Image

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0, # Blue
    'bilayer': np.array([29,255,0])/255.0, # Green
    'trilayer': np.array([198,22,22])/255.0, # Red
    'fewlayer': np.array([255,165,0])/255.0, # Orange
    'manylayer': np.array([255,165,0])/255.0, # Orange
    'bluish_layers': np.array([255,165,0])/255.0, # Orange
    'bulk': np.array([152,7,235])/255.0, # Purple
    'dirt': np.array([0, 0, 0])/255.0, # Yellow
    'more_bluish_layers': np.array([255, 255, 0])/255.0, # Yellow
    'bg': np.array([0, 0, 0])/255.0, # Uncolored
}

to_check = []
checked = []
photo_dir = 'C:/Users/admin/Desktop/2d_World/hardware/photo_dir'
min_blur = 3

try:
    cv2.namedWindow("Live Segmentation Demo", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Live Segmentation Demo", 960, 640)
    cv2.moveWindow("Live Segmentation Demo", 900, -900)
    
    while True:
        for filename in os.listdir(photo_dir):
            if (filename not in checked) and ('.JPG' in filename):
                to_check.append(filename)

        if len(to_check) > 0:
            time.sleep(1)
            for filename in to_check:
                frame =  np.array(Image.open(f'{photo_dir}/{filename}'))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Resize frame and prepare segmenter input
                shrink = 4
                frame = cv2.resize(frame, (int(frame.shape[1]/shrink), int(frame.shape[0]/shrink)), cv2.INTER_NEAREST)
                input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                print(input.shape)

                score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
                score = np.log(score)
                print(score)

                to_check.remove(filename)
                checked.append(filename)

                if score < min_blur:
                    continue
                

                # Initialize Segmenter
                segmenter = Segmenter(input, graphene, colors=colors_by_layer, magnification=20, k=3, min_area=200)


                # Run Segmenter
                segmenter.process_frame()
                segmenter.prettify()
                segmenter_output = (segmenter.colored_masks * 255).astype(np.uint8)
                segmenter_output = cv2.cvtColor(segmenter_output, cv2.COLOR_RGB2BGR)

                # Display the frame
                # shown = np.concatenate((segmenter_output, frame), axis=1)
                cv2.imshow('Live Segmentation Demo', segmenter_output)

                # NEVER REMOVE
                cv2.waitKey(1)

except KeyboardInterrupt:
    # graceful exit
    cv2.destroyAllWindows()