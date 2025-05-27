import sys
import cv2
import numpy as np

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

def crop(input):
    return input[50:880, 200:1440]

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame from stream", file=sys.stderr)
            break

        # Crop Frame
        # frame = crop(frame)

        # Compute Blur Score
        score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
        score = -np.log(score)

        # Overlay Text
        frame = cv2.putText(frame, 'Blur Factor = '+str(score), org, font, 
                    fontScale, color, thickness, cv2.LINE_AA)

        # Display the frame
        cv2.imshow('Blur Factor Demo', frame)

        # NEVER REMOVE
        cv2.waitKey(1)

except KeyboardInterrupt:
    # graceful exit
    pass
cap.release()
cv2.destroyAllWindows()