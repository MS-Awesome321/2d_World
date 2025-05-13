from skimage.color import lab2rgb, rgb2gray, rgb2lab
import numpy as np
import cv2
from tqdm import tqdm
import matplotlib.pyplot as plt
import sys

sys.setrecursionlimit(1000000)


class Node():
    def __init__(self, row, col):
        self.coords = (row, col)
        self.total = np.array([0,0,0])
        self.children = 0
        self.leader = self

    def avg_color(self):
        return self.total/self.children

class WeightedUnionFind():
    def __init__(self, rows, cols):
        self.nodes = [[Node(row, col) for col in range(cols)] for row in range(rows)]

    def find(self, row, col):
        node  = self.nodes[row][col]
        while(node.leader != node):
            node = node.leader
        return node
    
    def union(self, r1, c1, r2, c2):
        node1 = self.find(r1, c1)
        node2 = self.find(r2, c2)

        if node1 == node2:
            return

        if (node1.children > node2.children):
            node2.leader = node1
            node2.children += node1.children
            node2.total += node1.total
        else:
            node1.leader = node2
            node1.children += node2.children
            node1.total += node2.total


# Region Adjacency Segmenter
class RAS():
    default_footprint = np.array(
        [[0,1,0], 
         [1,1,1], 
         [0,1,0]]
    )

    def __init__(self, img, threshold):
        self.lab = rgb2lab(img)
        self.filled = np.zeros((img.shape[0], img.shape[1])).astype('bool')
        self.wuf = WeightedUnionFind(img.shape[0], img.shape[1])
        self.threshold = threshold
        self.masks = np.zeros((img.shape[0], img.shape[1]))
        self.num_masks = 0

    def segment(self, footprint = default_footprint):
        for row in tqdm(range(self.lab.shape[0])):
            for col in range(self.lab.shape[1]):
                if not(self.filled[row][col]):
                    self.num_masks += 1
                    self.flood(row, col, self.num_masks, footprint)

                # leader = self.wuf.find(row, col)
                # id = self.masks[leader.coords[0]][leader.coords[1]]
                # if id > 0:
                #     self.masks[row][col] = id
                # else:
                #     self.num_masks += 1
                #     self.masks[leader.coords[0]][leader.coords[1]] = self.num_masks
                #     self.masks[row][col] = self.num_masks


    def flood(self, row, col, id, footprint=default_footprint):
        if self.filled[row][col]:
            return
        else:
            self.filled[row][col] = True

        self.masks[row][col] = id
        color = self.lab[row][col][1]
        if footprint[0][0] == 1 and (row > 0 and col > 0):
            if (np.linalg.norm(self.lab[row - 1][col - 1][1] - color) < self.threshold):
                # self.wuf.union(row, col, row-1, col-1)
                self.flood(row - 1, col - 1, id, footprint)
        
        if footprint[0][1] == 1 and row > 0:
            if (np.linalg.norm(self.lab[row - 1][col][1] - color) < self.threshold):
                # self.wuf.union(row, col, row-1, col)
                self.flood(row - 1, col, id, footprint)

        if footprint[0][2] == 1 and (row > 0 and col < self.lab.shape[1] - 1):
            if (np.linalg.norm(self.lab[row - 1][col + 1][1] - color) < self.threshold):
                # self.wuf.union(row, col, row-1, col+1)
                self.flood(row - 1, col + 1, id, footprint)

        if footprint[1][0] == 1 and col > 0:
            if (np.linalg.norm(self.lab[row][col - 1][1] - color) < self.threshold):
                # self.wuf.union(row, col, row, col-1)
                self.flood(row, col - 1, id, footprint)

        if footprint[1][2] == 1 and col < self.lab.shape[1] - 1:
            if (np.linalg.norm(self.lab[row][col + 1][1] - color) < self.threshold):
                # self.wuf.union(row, col, row, col + 1)
                self.flood(row, col + 1, id, footprint)

        if footprint[2][0] == 1 and (row < self.lab.shape[0] - 1 and col > 0):
            if (np.linalg.norm(self.lab[row + 1][col - 1][1] - color) < self.threshold):
                # self.wuf.union(row, col, row+1, col-1)
                self.flood(row + 1, col - 1, id, footprint)
        
        if footprint[2][1] == 1 and (row < self.lab.shape[0] - 1):
            if (np.linalg.norm(self.lab[row + 1][col][1] - color) < self.threshold):
                # self.wuf.union(row, col, row + 1, col)
                self.flood(row + 1, col, id, footprint)

        if footprint[2][2] == 1 and (row < self.lab.shape[0] - 1 and col < self.lab.shape[1] - 1):
            if (np.linalg.norm(self.lab[row + 1][col + 1][1] - color) < self.threshold):
                # self.wuf.union(row, col, row+1, col+1)
                self.flood(row + 1, col + 1, id, footprint)

# Testing
g1 = cv2.imread('../monolayerGraphene/monolayer_Graphene_Labeled/Inputs/1.jpg')
g1 = cv2.cvtColor(g1, cv2.COLOR_BGR2RGB)
# g1 = cv2.resize(g1, (g1.shape[1]//4, g1.shape[0]//4))

segmenter = RAS(g1, 0.45)
segmenter.segment()
plt.imshow(segmenter.masks)
plt.show()