import numpy as np
import subprocess
import time
import os
import cv2
from focus import Focus
import sys
sys.path.append('C:/Users/PHY-Wulabmobile1/Desktop/test/2d_World/')
from segmenter2 import Segmenter
from material import wte2, graphene, EntropyEdgeMethod

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0,
    'bilayer': np.array([29,255,0])/255.0,
    'trilayer': np.array([198,22,22])/255.0,
    'fewlayer': np.array([255,165,0])/255.0,
    'manylayer': np.array([255,165,0])/255.0,
    'bluish_layers': np.array([255,165,0])/255.0,
    'bulk': np.array([152,7,235])/255.0,
    'dirt': np.array([0, 0, 0])/255.0,
    'more_bluish_layers': np.array([255, 255, 0])/255.0,
    'bg': np.array([0, 0, 0])/255.0,
}

class PhotoShoot():
    def __init__(self, photo_dir='', filename=None, return_name=False, wait_and_return=True):
        self.num_photos = 0
        self.current_dir = f'{os.getcwd()}\\{photo_dir}'
        self.filename = filename
        self.return_name = return_name
        self.wait_and_return = wait_and_return
        os.chdir(self.current_dir)

        # Start persistent gphoto2 shell session
        self.gp_shell = subprocess.Popen(
            ['gphoto2', '--shell'],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

    def take_photo(self, filename=None, return_name=False, preview=False):
        if filename is None:
            if self.filename is None:
                filename = f'capt{self.num_photos:04}.jpg'
            else:
                filename = f'{self.filename}_{self.num_photos}.jpg'
        full_path = f"{self.current_dir}\\{filename}"
        full_path = full_path.replace('\\', '/')

        # Send capture command to persistent shell
        if preview:
            cmd = 'capture-preview \n'
            delay = 2
        else:
            cmd = 'capture-image-and-download \n'
            delay = 5
        self.gp_shell.stdin.write(cmd)
        self.gp_shell.stdin.flush()

        if self.wait_and_return:
            time.sleep(delay)

            img = cv2.imread(full_path, cv2.IMREAD_COLOR)
            self.num_photos += 1
            if self.return_name or return_name:
                return img, full_path
            else:
                return img

    def __del__(self):
        try:
            self.gp_shell.stdin.write('exit\n')
            self.gp_shell.stdin.flush()
            self.gp_shell.terminate()
        except Exception:
            pass
    
class AutoFocus():
    def __init__(self, comport):
        self.focus_motor = Focus(comport)
    
    def __call__(self):
        prev_score = None
        direction = 1
        ps = PhotoShoot('photo_dir')
        for i in range(5):
            frame = ps.take_photo(preview=True)
            score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
            score = np.log(score)
            print(score)
            
            if prev_score:
                if score < prev_score:
                    direction *= -1
                if score < 2:
                    focus_speed = 200
                elif score < 2.5:
                    focus_speed = 100
                elif score < 3:
                    focus_speed = 50
                elif score < 3.5:
                    focus_speed = 25
                elif score < 4.25:
                    focus_speed = 10
                elif score < 4.5:
                    focus_speed = 5
                else:
                    focus_speed = 0

                self.focus_motor.rotate_relative(direction*focus_speed)
                time.sleep(0.008 * focus_speed)
            
            prev_score = score

class TestSegment(PhotoShoot):
    def __call__(self):
        self.return_name = True
        img, name = self.take_photo()
        segmenter = Segmenter(img, graphene, colors=colors_by_layer, magnification=20)

        # Run Segmenter
        segmenter.process_frame()
        segmenter.prettify()
        segmenter_output = (segmenter.colored_masks * 255).astype(np.uint8)

        output = cv2.cvtColor(segmenter_output.astype('uint8'), cv2.COLOR_RGB2BGR)

        # Display the frame
        cv2.imshow('Live Segmentation Demo', output)
        time.sleep(1)
        os.remove(name)