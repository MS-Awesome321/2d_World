import sys
import cv2
import os
import numpy as np
sys.path.append(os.path.abspath('/Users/mayanksengupta/Desktop/2d_World/')) # add path to folder containing segmenter.py
from segmenter import Segmenter
from material import wte2, graphene

# gphoto2 --capture-movie --stdout | python camera.py

sys.stdin = sys.stdin.buffer

# Create a VideoCapture object to read from stdin
cap = cv2.VideoCapture(0)  # Use 0 for stdin

# Set the VideoCapture to read from gphoto2's stdout
cap.open("pipe:0", cv2.CAP_FFMPEG)

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0, # Blue
    'bilayer': np.array([29,255,0])/255.0, # Green
    'trilayer': np.array([198,22,22])/255.0, # Red
    'fewlayer': np.array([255,165,0])/255.0, # Orange
    'manylayer': np.array([255,165,0])/255.0, # Orange
    'bluish_layers': np.array([255,165,0])/255.0, # Orange
    'bulk': np.array([152,7,235])/255.0, # Purple
    'dirt': np.array([255, 255, 0])/255.0, # Yellow
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

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame from stream", file=sys.stderr)
        break
    
    # Resize frame and prepare segmenter input
    frame = cv2.resize(frame, (840, 560))
    input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Initialize Segmenter
    segmenter = Segmenter(input,
                        material=wte2,
                        size = input.shape[:2],
                        mask_colors=colors_by_layer,
                        magnification=100,
                        mask_numbers=number_by_layer
                    )

    # Run Segmenter
    segmenter.go()
    segmenter.prettify()

    output = cv2.cvtColor((segmenter.colored_masks * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)

    # Display the frame
    shown = np.concatenate((output, frame), axis=1)
    cv2.imshow('Live Segment Demo', shown)


    if cv2.waitKey(1) == ord('q'): # Break on 'q' key press
        break

cap.release()
cv2.destroyAllWindows()