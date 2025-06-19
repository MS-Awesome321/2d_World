import numpy as np
from PIL import ImageGrab
import cv2
import time


try:
    while(True):
        printscreen =  np.array(ImageGrab.grab(bbox=(200,200,960,640)))
        cv2.imshow('Python View',cv2.cvtColor(printscreen, cv2.COLOR_BGR2RGB))

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            raise KeyboardInterrupt
except KeyboardInterrupt:
    print("Exiting...")
    cv2.destroyAllWindows()