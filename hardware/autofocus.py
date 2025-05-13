import sys
import cv2
import numpy as np
import time
from motor import rotate_relative

# gphoto2 --capture-movie --stdout | python autofocus.py

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

start = time.time()
wait_time = 3 # wait for motor to stop spinning
prev_blur_score= 0
direction = -1 # down
threshold = 0.5
done = False

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

    # Display the frame
    cv2.imshow('Autofocus Demo', frame)

    if not done:
        if (time.time() - start > wait_time):
            start = time.time()
            if prev_blur_score > score:
                # Move in same direction
                rotate_relative(direction * 10 * abs(prev_blur_score - score))
            else :
                # Negate direction
                direction *= -1
                rotate_relative(direction * 10 * abs(prev_blur_score - score))
            done = abs(prev_blur_score - score) < threshold
            if done:
                print("microscope focused")
            prev_blur_score = score


    if cv2.waitKey(1) == ord('q'): # Break on 'q' key press
        break

cap.release()
cv2.destroyAllWindows()