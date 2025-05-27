import sys
import cv2
import os
import numpy as np
sys.path.append(os.path.abspath('/Users/mayanksengupta/Desktop/2d_World/')) # add path to folder containing segmenter.py
from segmenter2 import Segmenter
from material import wte2, graphene, EntropyEdgeMethod
import warnings
from skimage.filters.rank import entropy
from skimage.morphology import disk
from skimage.color import lab2rgb, rgb2gray, rgb2yuv, rgb2lab
from skimage.exposure import adjust_gamma
from skimage.morphology import white_tophat

warnings.filterwarnings("ignore", category=UserWarning)

# gphoto2 --capture-movie --stdout | python camera.py

sys.stdin = sys.stdin.buffer

# Create a VideoCapture object to read from stdin
cap = cv2.VideoCapture('Test_Videos/100X.mp4')  # Use 0 for stdin

# Set the VideoCapture to read from gphoto2's stdout
# cap.open("pipe:0", cv2.CAP_FFMPEG)

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


# Inputs to future AI model (Currently focusing on Monolayer, Bilayer, and >Bilayer for Segmentation)
number_by_layer = {
    'bg': 0,
    'monolayer': 1,
    'bilayer': 2,
    'trilayer': 3,
    'fewlayer': 3,
    'manylayer': 3,
    'bluish_layers':3,
    'more_bluish_layers':3,
    'bulk': 3,
    'dirt': 3,
}

# Crop Function
def crop(input):
    return input[51:879, 201:1440]

def lab_correct(lab_img, current_avg_lab, target_avg_lab=[55.96122403, 28.28108621, -3.12392236]):
  result = np.ones_like(lab_img)
  result[:,:,0] = lab_img[:,:,0] - (current_avg_lab[0] - target_avg_lab[0])*np.ones_like(lab_img[:,:,0])
  result[:,:,1] = lab_img[:,:,1] - (current_avg_lab[1] - target_avg_lab[1])*np.ones_like(lab_img[:,:,1])
  result[:,:,2] = lab_img[:,:,2] - (current_avg_lab[2] - target_avg_lab[2])*np.ones_like(lab_img[:,:,2])
  return result

def rgb_lab_correct(img, current_avg_lab, target_avg_lab=[55.96122403, 28.28108621, -3.12392236]):
  return lab2rgb(lab_correct(rgb2lab(img), current_avg_lab, target_avg_lab))

i = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame from stream", file=sys.stderr)
            break

        # Read every tenth frame
        i+=1
        if i%10 != 0:
            continue

        # Crop Frame
        frame = crop(frame)
        
        # Resize frame and prepare segmenter input
        frame = cv2.resize(frame, (frame.shape[1]*2, frame.shape[0]*2))
        input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # input = adjust_gamma(input, gamma=0.75, gain=0.5)

        # Initialize Segmenter
        segmenter = Segmenter(input, graphene, colors=colors_by_layer)

        # Run Segmenter
        segmenter.process_frame()
        segmenter.prettify()
        segmenter_output = (segmenter.colored_masks * 255).astype(np.uint8)

        output = cv2.cvtColor(segmenter_output.astype('uint8'), cv2.COLOR_RGB2BGR)

        # Display the frame
        shown = np.concatenate((output, frame), axis=1)
        cv2.imshow('Live Segmentation Demo', shown)

         # NEVER REMOVE
        cv2.waitKey(1)

except KeyboardInterrupt:
    # graceful exit
    cap.release()
    cv2.destroyAllWindows()