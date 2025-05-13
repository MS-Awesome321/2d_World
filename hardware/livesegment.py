import sys
import cv2
import numpy as np

sys.path.append('../2d_World/segmenter.py')

from segmenter import Segmenter
from material import wte2, graphene

# gphoto2 --capture-movie --stdout | python camera.py

sys.stdin = sys.stdin.buffer

# Create a VideoCapture object to read from stdin
cap = cv2.VideoCapture(0)  # Use 0 for stdin

# Set the VideoCapture to read from gphoto2's stdout
cap.open("pipe:0", cv2.CAP_FFMPEG)

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

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

    # Compute Blur Score
    score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
    score = -np.log(score)

    # Overlay Text
    frame = cv2.putText(frame, 'Blur Factor = '+str(score), org, font, 
                   fontScale, color, thickness, cv2.LINE_AA)
    
    # Initialize Segmenter
    segmenter = Segmenter(frame,
                        material=wte2,
                        size = frame.shape[:2],
                        mask_colors=colors_by_layer,
                        magnification=100,
                        mask_numbers=number_by_layer
                    )

    # Run Segmenter
    segmenter.go()

    # Display the frame
    shown = np.concatenate((segmenter.prettify(), frame), axis=1)
    cv2.imshow('Live Segment Demo', shown)


    if cv2.waitKey(1) == ord('q'): # Break on 'q' key press
        break

cap.release()
cv2.destroyAllWindows()