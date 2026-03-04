import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.linear_model import LinearRegression
from mpl_toolkits.mplot3d import proj3d
from material import wte2, graphene
import cv2
import argparse

parser = argparse.ArgumentParser(description="Cluster Material Data")
parser.add_argument(
        'material', 
        help='wte2 or graphene',
)
parser.add_argument(
    "-l",
    help="cutoff points greater than bg lab",
    action='store_true'
)
args = parser.parse_args()

if args.material == 'wte2':
    bg_lab = wte2.target_bg_lab
    d_name = 'pv_wte2_5k.pkl'
    target_dir = "/Users/mayanksengupta/Desktop/WTe2_M100"
elif args.material == 'graphene':
    bg_lab = graphene.target_bg_lab
    d_name = 'pv_graphene_5k.pkl'
    target_dir = "/Users/mayanksengupta/Desktop/monolayerGraphene/monolayer_Graphene"
else:
    raise ValueError("Invalid Material")

thickness = ["monolayer", "bilayer", "trilayer", "fewlayer", "manylayer", "bulk", "bg", "dirt"]
label_colors = ['blue', 'green', 'red', 'orange', 'black', 'purple', 'magenta', 'yellow']

with open(d_name, "rb") as file:
    data = pickle.load(file)

points = data["avg_labs"]
labels = data["labels"]
# sizes = data["sizes"]
names = np.array(data["names"])
mask_ids = np.array(data["mask_ids"])

cleaned_masks = []
for mask in data["masks"]:
    if mask is not None and mask.shape == data["masks"][10].shape:
        cleaned_masks.append(mask)
    else:
        cleaned_masks.append(np.zeros_like(data["masks"][10]))
masks = np.stack(cleaned_masks, axis=0)

cleaned_coords = []
for coord in data["coords"]:
    if coord is not None and coord.shape == data["coords"][10].shape:
        cleaned_coords.append(coord)
    else:
        cleaned_coords.append(np.zeros_like(data["coords"][10]))
coords = np.stack(cleaned_coords, axis=0)
coords = coords.astype('int')

print(len(points))

if args.l:
    m = points[:,0] < bg_lab[0]
    points = points[m]
    labels = labels[m]
    names = names[m]
    mask_ids = mask_ids[m]
    coords = coords[m]
    # sizes = sizes[m]
    print(len(points))

fig = plt.figure(figsize=(12, 8))
axs = []
axs.append(fig.add_subplot(1, 4, 1, projection='3d'))
axs.append(fig.add_subplot(1, 4, 2, projection='3d', sharex=axs[0], sharey=axs[0], sharez=axs[0]))
axs.append(fig.add_subplot(1, 4, 3)) 
axs.append(fig.add_subplot(1, 4, 4)) 

for ax in axs[:2]:
    ax.set_xlabel("L")
    ax.set_ylabel("A")
    ax.set_zlabel("B")
    ax.view_init(elev=5, azim=-140, roll=0)

# CLUSTERTING
model = DBSCAN(eps=3, min_samples=6)
no_monos = points
predicted_labels = model.fit_predict(no_monos)
predicted_labels[predicted_labels >= len(thickness)] = -1
m = np.max(predicted_labels) + 1

for i in range(m):
    plot_points = no_monos[predicted_labels == i]
    color = label_colors[i]
    # s = sizes[predicted_labels == i]/10000
    axs[0].scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color=color, alpha=0.1)

# Outliers
plot_points = no_monos[predicted_labels == -1]
# s = sizes[predicted_labels == -1]/10000
axs[0].scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color="magenta", label="outliers", alpha=0.1)

xs, ys, zs = points[:,0], points[:,1], points[:,2]

def format_coord(x, y):
    x_s, y_s, _ = proj3d.proj_transform(xs, ys, zs, ax.get_proj())
    
    # Calculate squared distance to the mouse position (x, y are screen coords)
    distances_sq = (x - x_s)**2 + (y - y_s)**2
    
    # Find the index of the closest point
    idx = np.argmin(distances_sq)
    
    # Retrieve the actual 3D coordinates of the closest point
    x_val = xs[idx]
    y_val = ys[idx]
    z_val = zs[idx]

    fname = names[idx]

    img = cv2.imread(f'{target_dir}/{fname}')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if args.material == 'wte2':
        h, w = img.shape[0]//4, img.shape[1]//4
        img = img[h:-h, w:-w]
        img = cv2.resize(img, None, fx=0.2, fy=0.2)
    elif args.material == 'graphene':
        img = cv2.resize(img, None, fx=0.1, fy=0.1)

    x, y = coords[idx]
    x //= 5
    y //= 5
    w_size = 50
    # window = img[max(0, x-w_size):min(x+w_size, img.shape[0]), max(0, y-w_size):min(y+w_size, img.shape[1]), :]
    window = masks[idx].astype('uint8')
    window = cv2.resize(window, None, fx=0.1, fy=0.1)

    axs[2].cla()
    axs[2].imshow(img)
    axs[2].scatter(y, x)

    axs[3].cla()
    axs[3].imshow(window)
    fig.canvas.draw_idle()
    
    return f'L={x_val:.2f}, A={y_val:.2f}, B={z_val:.2f}, label={labels[idx]}, mask={mask_ids[idx]}, name= {fname}'

axs[0].format_coord = format_coord
axs[1].format_coord = format_coord

# All Points
for l_type in thickness:
    plot_points = points[labels==l_type]
    color = label_colors[thickness.index(l_type)]
    # s = sizes[labels==l_type]/10000
    axs[1].scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], label=l_type, color=color, alpha=0.1)

for ax in axs[:2]:
    ax.scatter(bg_lab[0], bg_lab[1], bg_lab[2], color="black", label="BG Lab", marker="*", s=100)

# for ax in axs[:2]:
#     ax.legend()

# Line of Best Fit
X = points[:, 0].reshape(-1, 1) 
Y = points[:, 1:]

X = np.concatenate([X, np.expand_dims(bg_lab[:1], axis=0)], axis=0)
Y = np.concatenate([Y, np.expand_dims(bg_lab[1:], axis=0)], axis=0)
weights = np.ones(len(X))
weights[-1] = 2*len(X)

reg = LinearRegression().fit(X, Y, weights)
L_fit = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
AB_fit = reg.predict(L_fit)

axs[0].plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color='orange', linewidth=2, label='Best Fit Line')
axs[1].plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color='orange', linewidth=2, label='Best Fit Line')

plt.show()
