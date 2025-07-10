import numpy as np
import cv2
from PIL import ImageGrab

bgr_frame =  np.array(ImageGrab.grab(bbox=(200,200,960,640)))
frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
cv2.imwrite(f'manual2.jpg', frame)