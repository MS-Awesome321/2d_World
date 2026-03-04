import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton as mb
from matplotlib.widgets import Button, RadioButtons
from segmenter import Segmenter
from material import graphene, hBN, wte2
import cv2
import numpy as np
import os
import random
import pickle
import sys
from utils import get_mag

"""
GUI for manually selecting masks for layer types 
in images to train segmenter. 
"""

shrink = 2

fig, axs = plt.subplots(2, 2, sharex=True, sharey=True)
plt.ion()
plt.show()

plt.rcParams["keymap.quit"] = [] 
axprev = fig.add_axes([0.7, 0.25, 0.1, 0.075])
axnext = fig.add_axes([0.81, 0.25, 0.1, 0.075])
axquit = fig.add_axes([0.59, 0.25, 0.1, 0.075])

bnext = Button(axnext, 'Next')
bprev = Button(axprev, 'Previous')
bquit = Button(axquit, 'Quit')

pts_list = []
avg_lab_list = []
labels_list = []

# folder = "/Users/mayanksengupta/Desktop/10X"
folder = "/Users/mayanksengupta/Desktop/monolayerGraphene/monolayer_Graphene/"
# folder = "/Users/mayanksengupta/Desktop/WTe2_M20"

def end():
    for points in avg_lab_list:
        print(points)
    
    data = {"points": pts_list, "avg_labs": avg_lab_list, "labels": labels_list}

    with open("data.pkl", "wb") as file:
        pickle.dump(data, file)

    sys.exit()

class PointCollector:
    active = True
    points = []
    labels = []
    lab_list = []
    plot_points = []
    ax = None
    cid = None

    def __init__(self, ax, segmenter):
        self.segmenter = segmenter
        PointCollector.ax = ax
        PointCollector.points = pts_list[GUI.i]
        PointCollector.labels = labels_list[GUI.i]
        PointCollector.lab_list = avg_lab_list[GUI.i]
        PointCollector.plot_points = []
        PointCollector.cid = ax.figure.canvas.mpl_connect('key_press_event', self.onkey)
        for i in range(len(PointCollector.points)):
            point = PointCollector.points[i]
            color = LabelOptions.label_options[PointCollector.labels[i]]
            PointCollector.plot_points.append(ax.plot(point[0], point[1], f"{color}+"))
        ax.figure.canvas.draw()

    def onkey(self, event):
        if not PointCollector.active:
            return
        if event.inaxes == PointCollector.ax and event.key == ' ':
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                PointCollector.points.append(np.array([x, y]))
                PointCollector.labels.append(LabelOptions.current)
                col = int(x + 0.5)
                row = int(y + 0.5)
                mask_num = self.segmenter.masks[row, col]
                lab = self.segmenter.avg_labs[mask_num]
                PointCollector.lab_list.append(lab)
                color = LabelOptions.label_options[LabelOptions.current]
                PointCollector.plot_points.append(PointCollector.ax.plot(x, y, f"{color}+"))
                PointCollector.ax.figure.canvas.draw()
        elif event.key == 'd' or event.key == 'D':
            if len(PointCollector.points) > 0:
                PointCollector.points.pop()
                PointCollector.labels.pop()
                PointCollector.lab_list.pop()
                removed = PointCollector.plot_points.pop()
                for handle in removed:
                    handle.remove()
                PointCollector.ax.figure.canvas.draw()

    def disconnect():
        PointCollector.ax.figure.canvas.mpl_disconnect(PointCollector.cid)

class LabelOptions:
    # options = ["0-10", "10-20", "20-30", "30-40", "40+"]
    options = ["monolayer", "bilayer", "trilayer", "manylayer", "bulk"]
    label_colors = ['blue', 'green', 'red', 'orange', 'purple']
    label_options = ['b', 'g', 'r', 'y', 'm']
    current = 0

    def change_title(label):
        LabelOptions.current = LabelOptions.options.index(label)
        axs[0, 0].set_title(f"Label: {label} nm")
        fig.canvas.draw_idle()

    def __init__(self):
        self.rbutton = RadioButtons(axs[0, 1], LabelOptions.options, active=0, label_props={'color': LabelOptions.label_colors}, radio_props={'facecolor': LabelOptions.label_colors})
        self.rbutton.on_clicked(LabelOptions.change_title)

    def set_active(self, label_num):
        if type(label_num) is str:
            label_num = LabelOptions.options.index(label_num)
        LabelOptions.current = label_num
        self.rbutton.set_active(label_num)

lo = LabelOptions()

class GUI:
    i = 0

    def prev(self, event):
        if len(PointCollector.points) > 0 and GUI.i >= 0 and GUI.i < len(images):
            pts_list[GUI.i] = PointCollector.points
            labels_list[GUI.i] = PointCollector.labels
            avg_lab_list[GUI.i] = PointCollector.lab_list
        PointCollector.disconnect()
        if GUI.i > 0:
            GUI.i -= 1
        self.show()

    def next(self, event):
        if len(PointCollector.points) > 0 and GUI.i >= 0 and GUI.i < len(images):
            pts_list[GUI.i] = PointCollector.points
            labels_list[GUI.i] = PointCollector.labels
            avg_lab_list[GUI.i] = PointCollector.lab_list
        PointCollector.disconnect()
        GUI.i += 1
        if GUI.i >= len(images):
            self.close(None)
        else:
            self.show()

    def close(self, event):
        if len(PointCollector.points) > 0 and GUI.i >= 0 and GUI.i < len(images):
            pts_list[GUI.i] = PointCollector.points
            labels_list[GUI.i] = PointCollector.labels
            avg_lab_list[GUI.i] = PointCollector.lab_list
        PointCollector.disconnect()
        end()

    def show(self):
        # Only clear axes that display images, not axs[0, 1] (RadioButtons)
        axs[0, 0].clear()
        axs[1, 0].clear()
        axs[1, 1].clear()

        label, dirpath, fname = images[GUI.i]
        magnification = get_mag(fname)

        img = cv2.imread(f"{dirpath}/{fname}", cv2.IMREAD_COLOR_RGB)
        if img is None:
            print(f"Failed to Load Image. {dirpath}/{fname}")
        else:
            img = cv2.resize(img, (img.shape[1]//shrink, img.shape[0]//shrink))
            # h, w = img.shape[0]//5, img.shape[1]//5
            # img = img[h:-h, w:-w]
            segmenter = Segmenter(img, graphene, magnification=magnification, min_area=50, k=3)
            segmenter.process_frame()

            def format_coord_lab(x, y):
                col = int(x + 0.5)
                row = int(y + 0.5)
                mask_num = segmenter.masks[row, col]
                lab = segmenter.avg_labs[mask_num]
                lab = np.round(lab, 2)
                area = segmenter.mask_areas[mask_num]
                return f'x={col},    y={row},    avg_lab={lab},    area={area},    flake_id={mask_num}'

            axs[0, 0].set_title(f"Label: {label} nm")
            axs[0, 0].imshow(img)
            axs[0, 0].format_coord = format_coord_lab
            axs[0, 0].axis('off')

            axs[1, 0].set_title(f"Img: {fname}")
            axs[1, 0].imshow(segmenter.masks, cmap='inferno')
            axs[1, 0].format_coord = format_coord_lab
            axs[1, 0].set_yticks([])
            axs[1, 0].set_xticks([])
            axs[1, 0].set_xlabel(f"Progress: {GUI.i + 1}/{len(images)}")

            axs[1, 1].axis('off')

            plt.sca(axs[0, 0])
            lo.set_active(label)
            collector = PointCollector(axs[0, 0], segmenter)
            while PointCollector.active:
                plt.pause(0.1)


# Main method
images = []
for dirpath, dirnames, filenames in os.walk(folder):
    _, label = os.path.split(dirpath)
    label = label[:-2]
    label = "monolayer"
    for fname in filenames:
        if len(filenames) > 1 and "M100" in fname:
            images.append((label, dirpath, fname))

# images = images[:50]
random.shuffle(images)

callback = GUI()
bnext.on_clicked(callback.next)
bprev.on_clicked(callback.prev)
bquit.on_clicked(callback.close)
pts_list = [[] for i in range(len(images))]
avg_lab_list = [[] for i in range(len(images))]
labels_list = [[] for i in range(len(images))]

callback.show()
