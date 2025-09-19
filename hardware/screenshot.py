import numpy as np
from PIL import ImageGrab
import cv2

frame =  np.array(ImageGrab.grab(bbox=(432,137,1782,892)))
cv2.imwrite("corner1.png", frame[:,:,::-1])