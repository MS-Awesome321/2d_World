import sys
import cv2
import numpy as np
sys.path.append('/Users/mayanksengupta/Desktop/2d_World/')
from segmenter2 import Segmenter
from material import wte2, graphene, EntropyEdgeMethod
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# gphoto2 --capture-movie --stdout | python livesegment.py

sys.stdin = sys.stdin.buffer

# Create a VideoCapture object to read from stdin
cap = cv2.VideoCapture('Test_Videos/100X.mp4') 

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
    return input[210:770, 400:1220]

i = 0

try:
    while True:
        ret, frame = cap.read()
        #print(frame.shape)
        if not ret:
            break

        # Read every tenth frame
        i+=1
        if i%5 != 0:
            continue

        # Crop Frame
        frame = crop(frame)
        
        # Resize frame and prepare segmenter input
        grow = 1
        frame = cv2.resize(frame, (int(frame.shape[1]*grow), int(frame.shape[0]*grow)), cv2.INTER_NEAREST)
        input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # input = adjust_gamma(input, gamma=0.75, gain=0.5)

        # Initialize Segmenter
        #segmenter = Segmenter(input, graphene, colors=colors_by_layer)
        segmenter = Segmenter(input, graphene, colors=colors_by_layer, magnification=100)


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