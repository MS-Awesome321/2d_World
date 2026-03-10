import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from sklearn.linear_model import LinearRegression
from sklearn.mixture import GaussianMixture
from scipy.stats import norm
from tqdm import tqdm
from material import wte2, graphene
from utils import compute_proj_dist
import argparse

# Parse Arguments
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
    d_name = 'points_wte2.pkl'
    f_name = "sequential_wte2.gif"
    name = 'WTe2'
elif args.material == 'graphene':
    bg_lab = graphene.target_bg_lab
    d_name = 'points_graphene.pkl'
    f_name = "sequential_graphene.gif"
    name = 'Graphene'

else:
    raise ValueError("Invalid Material")

# LOAD DATA
with open(d_name, "rb") as file:
    data = pickle.load(file)

points = data["avg_labs"]
labels = data["labels"]

label_colors = ["red", "green", "blue", "magenta", "purple", "black", "orange"]
thickness = ["trilayer", "bilayer", "monolayer", "bg", "bulk", "fewlayer", "manylayer"]

n_layers = 4

# Initialize GIF Writer
metadata = {
    "title": "Sequential Line of Best Fit",
    "artist": "Mayank Sengupta"
}
writer = PillowWriter(fps=7, metadata=metadata)

# Write GIF
fig = plt.figure(figsize=(15, 12))
axs = []
axs.append(fig.add_subplot(2, 3, 1, projection='3d'))
axs.append(fig.add_subplot(2, 3, 2, projection='3d', sharex=axs[0], sharey=axs[0], sharez=axs[0]))
axs.append(fig.add_subplot(2, 3, 3, projection='3d', sharex=axs[0], sharey=axs[0], sharez=axs[0]))
axs.append(fig.add_subplot(2, 3, 4))
axs.append(fig.add_subplot(2, 3, 5))
fig.suptitle(f"Color Distributions of {name} flakes")

for ax in axs[:3]:
    ax.set_xlabel("L")
    ax.set_ylabel("A")
    ax.set_zlabel("B")
    ax.view_init(elev=30, azim=-130, roll=0)

d = 10
n_gaussians = 4
with writer.saving(fig, f_name, 100):
    for i in tqdm(range(15, len(points), 5)):
        for ax in axs:
            ax.clear()
        
        # Line of Best Fit and Projection
        current_set = points[:i, :]
        current_labels = labels[:i]
        X = current_set[:, 0].reshape(-1, 1) 
        Y = current_set[:, 1:]
        X = np.concatenate([X, np.expand_dims(bg_lab[:1], axis=0)], axis=0)
        Y = np.concatenate([Y, np.expand_dims(bg_lab[1:], axis=0)], axis=0)
        weights = np.ones(len(X))
        weights[-1] = 10*len(X)

        reg = LinearRegression().fit(X, Y, weights)
        L_fit = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        AB_fit = reg.predict(L_fit)
        line_direction = np.array([1, reg.coef_[0, 0], reg.coef_[1, 0]])
        line_direction = line_direction / np.linalg.norm(line_direction)

        distances, projections = compute_proj_dist(bg_lab, line_direction, current_set)
        subset = current_set[distances < d]
        complement = current_set[distances >= d]

        for ax in axs[:3]:
            ax.scatter(bg_lab[0], bg_lab[1], bg_lab[2], color="black", marker="*", s=100, label="BG Lab")
            ax.plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color="gray", linewidth=2, label='Best Fit Line')

        # Axis 0
        for t, c in zip(thickness, label_colors):
            sub = current_set[current_labels == t]
            axs[0].scatter(sub[:, 0], sub[:, 1], sub[:, 2], color=c, label=t, alpha=0.1)

        # Axis 1
        axs[1].scatter(subset[:, 0], subset[:, 1], subset[:, 2], c='green')
        axs[1].scatter(complement[:, 0], complement[:, 1], complement[:, 2], c='black', alpha=0.1)

        # Axis 2
        axs[2].scatter(current_set[:, 0], current_set[:, 1], current_set[:, 2], c=projections, cmap='inferno', alpha=0.5)

        # Histogram
        projections = projections[distances < d]
        if args.l:
            projections = projections[projections < 5]
            projections = np.expand_dims(projections, axis=1)
            upper_limit = 5
        else:
            upper_limit = 55

        counts, bins = np.histogram(projections, bins=np.linspace(-55, upper_limit, 100))
        axs[3].stairs(counts, bins, fill=True)
        axs[4].stairs(counts, bins, fill=True)

        # GMM
        model = GaussianMixture(n_gaussians, n_init=3, random_state=42, covariance_type="full")
        model.fit_predict(projections)
        means = model.means_

        s = np.argsort(model.means_[:, 0])
        means = model.means_[s, 0]
        covariances = model.covariances_[s, 0, 0]

        for g in range(n_gaussians):
            mean = means[g]

            # Standard deviation is the square root of the covariance
            std = np.sqrt(covariances[g])
            weight = model.weights_[g]

            x_axis = np.linspace(-55, upper_limit, 1000).reshape(-1, 1)

            # Calculate the PDF for this specific component
            y = np.max(counts) * norm.pdf(x_axis, mean, std)
            zero = np.zeros_like(x_axis)

            axs[4].plot(x_axis, y, lw=2, linestyle='-', color=label_colors[g])
            axs[4].fill_between(np.squeeze(x_axis), np.squeeze(y), np.squeeze(zero), alpha=0.2, color=label_colors[g])
            axs[4].scatter(mean, 0, s=300, marker="*", color=label_colors[g], label=thickness[g])

        # Titles and Legend
        axs[0].set_title("Labeled Dataset")
        axs[1].set_title("Subset Used for Prediction")
        axs[2].set_title("Projection onto Line of Best Fit")
        axs[3].set_title("Histogram of Projections")
        axs[4].set_title("GMM Predictions")

        axs[0].legend()
        axs[4].legend()

        writer.grab_frame()

plt.show()
