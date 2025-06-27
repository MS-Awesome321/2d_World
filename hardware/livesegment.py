import sys
import cv2
import numpy as np
sys.path.append('C:/Users/PHY-Wulabmobile1/Desktop/test/2d_World/')
from segmenter2 import Segmenter
from material import wte2, graphene, EntropyEdgeMethod, hessian_determinant
from scipy.ndimage import gaussian_filter, gaussian_gradient_magnitude
from skimage.filters import sobel, unsharp_mask, farid
import warnings
from PIL import ImageGrab

warnings.filterwarnings("ignore", category=UserWarning)

<<<<<<< HEAD
=======
# gphoto2 --capture-movie --stdout | python livesegment.py

sys.stdin = sys.stdin.buffer

# Create a VideoCapture object to read from stdin
cap = cv2.VideoCapture('Test_Videos/20X_1.mp4') 

# Set the VideoCapture to read from gphoto2's stdout
# cap.open("pipe:0", cv2.CAP_FFMPEG)

>>>>>>> 673af25 (some tests)
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

<<<<<<< HEAD
=======
# Crop Function
def crop(input):
    return input[210:770, 400:1220]

>>>>>>> 673af25 (some tests)
i = 0

try:
    while True:
        frame =  np.array(ImageGrab.grab(bbox=(200,200,960,640)))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Read every tenth frame
        i+=1
        if i%5 != 0:
            continue
        
        # Resize frame and prepare segmenter input
        grow = 2
        frame = cv2.resize(frame, (int(frame.shape[1]*grow), int(frame.shape[0]*grow)), cv2.INTER_NEAREST)
        input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Initialize Segmenter
        segmenter = Segmenter(input, graphene, colors=colors_by_layer, magnification=20)


        # Run Segmenter
        # segmenter.process_frame()
        # segmenter.prettify()
        # segmenter_output = (segmenter.colored_masks * 255).astype(np.uint8)

        # output = cv2.cvtColor((255*EntropyEdgeMethod(magnification=20, sigma=1, threshold=0.875)(frame)).astype('uint8'), cv2.COLOR_RGB2BGR)
        edges = farid(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))
        edges = edges/np.max(edges)
        edges = np.pow(edges, 2**(-2))
        fattened = edges.copy()
        fattened[fattened < 0.22] = 0
        fattened = gaussian_filter(edges, sigma=2)
        edges[edges < 0.3] = 2*fattened[edges < 0.3]
        # edges = edges > 0.22
        output = cv2.cvtColor((255*edges).astype('uint8'), cv2.COLOR_GRAY2BGR)

        # Display the frame
        # shown = np.concatenate((output, frame), axis=1)
        cv2.imshow('Live Segmentation Demo', output)

         # NEVER REMOVE
        cv2.waitKey(1)

except KeyboardInterrupt:
    # graceful exit
    cv2.destroyAllWindows()