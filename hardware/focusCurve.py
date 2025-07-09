import numpy as np
from focus import Focus
from PIL import ImageGrab
import cv2
import matplotlib.pyplot as plt


focus = Focus('COM5')
x = []
y = []

for i in range(-2000, 2050, 2):
    focus.move_to(i, wait=True)
    frame =  np.array(ImageGrab.grab(bbox=(200,200,960,640)))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
    score = np.log(score)
    print(f'Positon: {i}, Score: {score}')

    x.append(i)
    y.append(score)

focus.move_to(0, wait=True)
plt.plot(x, y, '-bo')
plt.show()
