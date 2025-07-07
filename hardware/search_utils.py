import numpy as np
import subprocess
import time
import os
import cv2
from focus import Focus
import sys
sys.path.append('C:/Users/admin/Desktop/2d_World/')
from segmenter2 import Segmenter
from material import wte2, graphene, EntropyEdgeMethod
from PIL import ImageGrab, Image
import pyautogui as pag
import keyboard



class WF():
    def __init__(self, min_blur, wait_frames, mercy_pause=7, min_colors=4):
        self.min_blur = min_blur
        self.wait_frames = wait_frames
        self.counter = 0
        self.mp = mercy_pause
        self.min_colors = min_colors

    def color_count_score(self, img, bins=16, shrink = 4):
        """
        Estimates the amount of different colors in an RGB image.
        The score increases as the number of distinct colors increases.
        """

        img = cv2.resize(img, (int(img.shape[1]/shrink), int(img.shape[0]/shrink)), cv2.INTER_NEAREST)
        pixels = img.reshape(-1, 3)
        quantized = (pixels // (256 // bins)).astype(np.uint8)
        unique_colors = np.unique(quantized, axis=0)
        
        return len(unique_colors)

    def wait_focus_and_click(self):
        score = 0
        i = 0
        take_pic = True
        if self.counter % self.mp == 0:
            w_f = 2*self.wait_frames
            mercy_pause = True
        else:
            w_f = self.wait_frames
            mercy_pause = False

        while score < self.min_blur and i < w_f:
            if keyboard.is_pressed('q'):
                raise KeyboardInterrupt
            frame =  np.array(ImageGrab.grab(bbox=(200,200,960,640)))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Compute Blur Score
            score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
            score = np.log(score)
            # print(score)
            colors = self.color_count_score(frame, bins=4)
            # print(colors)
            i+=1

            if colors < self.min_colors and not(mercy_pause):
                take_pic = False
                break

        if take_pic:
            # pag.leftClick(1776, 280)
            pag.leftClick(1794, 230)
            # print('POP')
        time.sleep(0.05)
        self.counter += 1


# Old stuff

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
    def __init__(self, photo_dir='', filename=None, return_name=False, wait_and_return=True, current_dir = None):
        if current_dir is not None:
            os.chdir(current_dir)

        self.num_photos = 0
        self.current_dir = f'{os.getcwd()}\\{photo_dir}'
        self.current_dir = self.current_dir.replace('\\', '/').replace('//', '/')
        self.filename = filename
        self.return_name = return_name
        self.wait_and_return = wait_and_return

        try:
            os.chdir(self.current_dir)
        except:
            pass

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
                if preview:
                    filename = 'capture_preview.jpg'
                else:
                    filename = f'capt{self.num_photos:04}.jpg'
            else:
                filename = f'{self.filename}_{self.num_photos}.jpg'
        full_path = f"{self.current_dir}\\{filename}"
        full_path = full_path.replace('\\', '/')

        # Send capture command to persistent shell
        if preview:
            if os.path.isfile(full_path):
                os.remove(full_path)
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

            if preview and os.path.isfile(full_path):
                os.remove(full_path)

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
    def __init__(self, dir, comport):
        self.focus_motor = Focus(comport)
        self.dir = dir
        self.gp_shell = subprocess.Popen(
            ['gphoto2', '--shell'],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        self.gp_shell.stdin.write(f'lcd {dir} \n')

    def __del__(self):
        try:
            self.gp_shell.stdin.write('exit\n')
            self.gp_shell.stdin.flush()
            self.gp_shell.terminate()
        except Exception:
            pass

    def _capture_preview(self):
        self.gp_shell.stdin.write('capture-preview \n')
        while not os.path.isfile(f'{os.getcwd().replace('\\', '/')}/{self.dir}/capture_preview.jpg'):
            time.sleep(0.05)
        img = Image.open(f'{os.getcwd().replace('\\', '/')}/{self.dir}/capture_preview.jpg')
        img = np.array(img)
        os.remove(f'{os.getcwd().replace('\\', '/')}/{self.dir}/capture_preview.jpg')
        return img
    
    def __call__(self):
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (50, 50)
        fontScale = 1
        color = (255, 0, 0)
        thickness = 2

        prev_score = None
        direction = 1
        finished = False
        while not finished:
            frame = self._capture_preview()
            score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
            score = np.log(score)
            if score > 4.5:
                finished = True

            frame = cv2.putText(frame, 'Blur Factor = '+str(score)+" "+str(prev_score), org, font, fontScale, color, thickness, cv2.LINE_AA)
            cv2.imshow("display", frame)
            cv2.waitKey(1)
            
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

                self.focus_motor.rotate_relative(direction * focus_speed)
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

class Shoot_Focus():
    def __init__(self, dir, comport, focus_interval=5):
        self.dir = dir
        self.gp_shell = subprocess.Popen(
            ['gphoto2', '--shell'],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        self.gp_shell.stdin.write(f'lcd {dir} \n')

        self.focus = Focus(comport=comport)
        self.focus_interval = focus_interval
        self.counter = 0

    def __del__(self):
        try:
            self.gp_shell.stdin.write('exit\n')
            self.gp_shell.stdin.flush()
            self.gp_shell.terminate()
        except Exception:
            pass

    def _capture_preview(self):
        self.gp_shell.stdin.write('capture-preview \n')
        while not os.path.isfile(f'{os.getcwd().replace('\\', '/')}/{self.dir}/capture_preview.jpg'):
            time.sleep(0.05)
            print('hello?')
        img = Image.open(f'{os.getcwd().replace('\\', '/')}/{self.dir}/capture_preview.jpg')
        img = np.array(img)
        os.remove(f'{os.getcwd().replace('\\', '/')}/{self.dir}/capture_preview.jpg')
        return img
        
    def __call__(self):
        if self.counter%self.focus_interval == 0:

            # Auto focusing
            prev_score = None
            direction = 1
            finished = False
            while not finished:
                frame = self._capture_preview()
                score = cv2.Laplacian(frame, cv2.CV_32FC1).var()
                score = np.log(score)
                if score > 4.5:
                    finished = True

                # frame = cv2.putText(frame, 'Blur Factor = '+str(score)+" "+str(prev_score), org, font, fontScale, color, thickness, cv2.LINE_AA)
                # cv2.imshow("display", frame)
                # cv2.waitKey(1)
                
                if prev_score:
                    if score <= prev_score:
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

                    self.focus.rotate_relative(direction * focus_speed)
                    time.sleep(0.008 * focus_speed)
            
                prev_score = score

        self.counter += 1

        # Actual Image Capture
        self.gp_shell.stdin.write('capture-image-and-download \n')
        time.sleep(0.2)