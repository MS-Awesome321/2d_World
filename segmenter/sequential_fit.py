import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from sklearn.linear_model import LinearRegression
from tqdm import tqdm

# Initialize GIF Writer
metadata = {
    "title": "Sequential Line of Best Fit",
    "artist": "Mayank Sengupta"
}
writer = PillowWriter(fps=15, metadata=metadata)

# Load in and process data
with open("data_graphene_new.pkl", "rb") as file:
    data = pickle.load(file)

all_points = []
all_labels = []
for points, labels in zip(data["avg_labs"], data["labels"]):
    all_points.extend(points)
    all_labels.extend(labels)

label_colors = ['blue', 'green', 'red', 'orange', 'purple']
thickness = ["monolayer", "bilayer", "trilayer", "manylayer", "bulk"]

all_points = np.stack(all_points, axis=0)
all_labels = np.array(all_labels)

n_layers = 3

# Write GIF
fig, axs = plt.subplots(1, 2, figsize=(12, 8), subplot_kw={'projection': '3d'})
fig.suptitle("Color Distributions of Graphene flakes")
bg_lab = np.array([[49.62793933, 12.17574073,  5.43972594]])

for ax in axs:
    ax.set_xlabel("L")
    ax.set_ylabel("A")
    ax.set_zlabel("B")
    ax.view_init(elev=30, azim=-130, roll=0)

subset = all_points[np.logical_and(all_labels >= 0, all_labels < n_layers)]
subset_labels = all_labels[np.logical_and(all_labels >= 0, all_labels < n_layers)]

idxs = np.arange(0, len(subset))
idxs = np.concatenate([idxs[subset_labels > 0], idxs[subset_labels == 0]])

subset = subset[idxs]
subset_labels = subset_labels[idxs]

with writer.saving(fig, "sequential.gif", 100):
    for i in tqdm(range(1, len(subset))):
        for ax in axs:
            ax.clear()
        
        # Line of Best Fit and Projection
        current_set = subset[:i, :]
        current_labels = subset_labels[:i]
        X = current_set[:, 0].reshape(-1, 1) 
        Y = current_set[:, 1:]

        reg = LinearRegression().fit(X, Y)
        L_fit = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        AB_fit = reg.predict(L_fit)

        intercept = np.array([L_fit[0][0], AB_fit[0][0], AB_fit[0][1]])
        normalized = current_set - intercept
        direction = np.array([L_fit[1][0], AB_fit[1][0], AB_fit[1][1]]) - intercept
        projection = normalized @ direction

        # Axis 1
        for label in range(n_layers):
            sub = current_set[current_labels == label]
            axs[0].scatter(sub[:, 0], sub[:, 1], sub[:, 2], color=label_colors[label], label=thickness[label])

        # Axis 2
        axs[1].scatter(current_set[:, 0], current_set[:, 1], current_set[:, 2], c=projection, cmap='inferno')
        axs[1].plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color="gray", linewidth=2, label='Best Fit Line')

        bg_lab = np.array([[49.62793933, 12.17574073,  5.43972594]])
        axs[0].scatter(bg_lab[:,0], bg_lab[:,1], bg_lab[:,2], color="black", marker="*", label="BG Lab")
        axs[1].scatter(bg_lab[:,0], bg_lab[:,1], bg_lab[:,2], color="black", marker="*", label="BG Lab")
        
        axs[0].legend()
        axs[1].legend()

        axs[0].set_title("Labeled Dataset")
        axs[1].set_title("Projection onto Line of Best Fit")

        writer.grab_frame()

plt.show()
