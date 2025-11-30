import numpy as np
from PIL import ImageGrab
import cv2
import sys

frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
try:
    filename = sys.argv[1]
except:
    filename = "corner_observed0.png"
cv2.imwrite(filename, frame[:,:,::-1])