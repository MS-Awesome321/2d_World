import cv2
from PIL import ImageGrab
import numpy as np
 
shrink = 4

try:
    while(True):        
        raw_frame =  np.array(ImageGrab.grab(bbox=(200,200,900,640)))
        raw_frame = cv2.resize(raw_frame, (int(raw_frame.shape[1]/shrink), int(raw_frame.shape[0]/shrink)), cv2.INTER_NEAREST)
        frame = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)

        # Find Lines
        gray =  cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray,50,150,apertureSize = 3)
        lines = cv2.HoughLines(edges,1,np.pi/18,25)

        # Overlay Lines
        if lines is not None:
            for line in lines:
                rho,theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
            
                cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)


        cv2.imshow('Line Test', frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            raise KeyboardInterrupt
        
except KeyboardInterrupt:
    print("Exiting...")
    cv2.destroyAllWindows()