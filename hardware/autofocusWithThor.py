import sys
import cv2
import numpy as np
from pylablib.devices import Thorlabs

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

# Initialize motor
motors = Thorlabs.list_kinesis_devices()
print(motors)
z_motor = Thorlabs.KinesisMotor(motors[0])

# Threshold for change in blur score
threshold = 0.25
prev_blur_score = None

try:
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
            if not prev_blur_score:
                prev_blur_score = score
                z_motor.move_by(50)
                z_motor._wait_move()
            else:
                z_motor.move_by((prev_blur_score - score) * 5)
                z_motor._wait_move()
                prev_blur_score = score
            done = abs(prev_blur_score - score) < threshold
        
         # NEVER REMOVE
        cv2.waitKey(1)

except KeyboardInterrupt:
    # graceful exit
    cap.release()
    cv2.destroyAllWindows()