import numpy as np
from PIL import ImageGrab
import cv2
import time

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

def blur_score(img):
    score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
    score = np.log(score)
    return score

def colorfulness(img):
    '''
    Finds how colorful an RGB image is. Based on this paper: 
    https://infoscience.epfl.ch/server/api/core/bitstreams/77f5adab-e825-4995-92db-c9ff4cd8bf5a/content
    '''

    rg = img[:,:,0] - img[:,:,1]
    sigma_rg = np.std(rg)
    mu_rg = np.mean(rg)
    yb = 0.5*(img[:,:,0] + img[:,:,1]) - img[:,:,2]
    sigma_yb = np.std(yb)
    mu_yb = np.mean(yb)

    sigma = np.sqrt(np.pow(sigma_rg, 2) + np.pow(sigma_yb, 2))
    mu = np.sqrt(np.pow(mu_rg, 2) + np.pow(mu_yb, 2))
    return sigma + 0.3*mu

def color_var(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    return np.std(img[:,:,0]) + np.std(img[:,:,1]) + np.std(img[:,:,2])

def img_population(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Sobel edge detection (both x and y)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    # Combine the two gradients
    edges = cv2.magnitude(sobelx, sobely)
    # Return the variance of the edge image
    return np.var(edges)

def color_count_score(img, bins=16, shrink = 4):
    """
    Estimates the amount of different colors in an RGB image.
    The score increases as the number of distinct colors increases.
    """

    img = cv2.resize(img, (int(img.shape[1]/shrink), int(img.shape[0]/shrink)), cv2.INTER_NEAREST)
    pixels = img.reshape(-1, 3)
    quantized = (pixels // (256 // bins)).astype(np.uint8)
    unique_colors = np.unique(quantized, axis=0)
    
    return len(unique_colors)

try:
    cv2.namedWindow("Python View", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Python View", 960, 640)
    cv2.moveWindow("Python View", 900, -1100)

    while(True):        
        frame =  np.array(ImageGrab.grab(bbox=(200,200,960,640)))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Compute Score
        # score = color_count_score(frame, bins=4)
        score = blur_score(frame)

        # Overlay Text
        frame = cv2.putText(frame, 'Score = '+str(score), org, font, fontScale, color, thickness, cv2.LINE_AA)

        cv2.imshow('Python View', frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            raise KeyboardInterrupt
        
except KeyboardInterrupt:
    print("Exiting...")
    cv2.destroyAllWindows()