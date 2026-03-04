import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from sklearn.linear_model import LinearRegression
from tqdm import tqdm
from gmm import LineConstrainedGMM
from material import graphene, wte2
import argparse

# Parse arguments
parser = argparse.ArgumentParser(description="Animate GMM Evolution on Sequentially Added Points")
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

# Select material
if args.material == 'wte2':
    bg_lab = wte2.target_bg_lab
    d_name = 'points_wte2.pkl'
elif args.material == 'graphene':
    bg_lab = graphene.target_bg_lab
    d_name = 'points_graphene.pkl'
else:
    raise ValueError("Invalid Material")

# Initialize GIF Writer
metadata = {
    "title": f"Sequential GMM Evolution - {args.material.capitalize()}",
    "artist": "Mayank Sengupta"
}
writer = PillowWriter(fps=10, metadata=metadata)

# Load data
with open(d_name, "rb") as file:
    data = pickle.load(file)

points = data["avg_labs"]
labels = data["labels"]

# Apply L cutoff if requested
if args.l:
    m = points[:, 0] < bg_lab[0]
    points = points[m]
    labels = labels[m]

# Randomize points
rng = np.random.RandomState(42)
shuffle_idx = rng.permutation(len(points))
points = points[shuffle_idx]
labels = labels[shuffle_idx]

# Helper function to compute line distance
def compute_line_distance(line_point, line_direction, X):
    """Compute distance of each point from the line"""
    to_points = X - line_point
    proj_lengths = (to_points @ line_direction)[:, np.newaxis]
    projections = line_point + proj_lengths * line_direction
    distances = np.linalg.norm(X - projections, axis=1)
    return distances

# Configure plot
fig = plt.figure(figsize=(25, 10))
axs = []
axs.append(fig.add_subplot(1, 3, 1, projection='3d'))
axs.append(fig.add_subplot(1, 3, 2, projection='3d', sharex=axs[0], sharey=axs[0], sharez=axs[0]))
axs.append(fig.add_subplot(1, 3, 3, projection='3d', sharex=axs[0], sharey=axs[0], sharez=axs[0]))

thickness = ["monolayer", "bilayer", "trilayer", "fewlayer", "manylayer", "bulk", "bg", "dirt"]
label_colors = ['blue', 'green', 'red', 'orange', 'black', 'purple', 'magenta', 'yellow']

for ax in axs:
    ax.set_xlabel("L")
    ax.set_ylabel("A")
    ax.set_zlabel("B")
    ax.view_init(elev=5, azim=-140, roll=0)

# Animation loop

n_components = 15
stride = 5

with writer.saving(fig, f"gmm_evolution_{args.material}.gif", 100):
    for frame_idx in tqdm(range(stride, len(points), stride)):
        min_points_per_cluster = frame_idx//20
        current_subset = points[:frame_idx]
        current_labels = labels[:frame_idx]

        # Compute line of best fit with background
        current_subset[0] = bg_lab
        X = current_subset[:, 0].reshape(-1, 1)
        Y = current_subset[:, 1:]
        weights = np.ones(frame_idx)
        weights[0] = 10 * frame_idx

        reg = LinearRegression().fit(X, Y, weights)
        line_direction = np.array([1, reg.coef_[0, 0], reg.coef_[1, 0]])
        line_direction = line_direction / np.linalg.norm(line_direction)
        L_fit = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        AB_fit = reg.predict(L_fit)

        # Filter points close to line
        distances = compute_line_distance(bg_lab, line_direction, current_subset)
        d = 20
        subset_mask = distances < d
        cut_subset = current_subset[subset_mask]
        comp_subset = current_subset[np.logical_not(subset_mask)]
        
        # Clear axes
        for ax in axs:
            ax.clear()
        
        # Fit GMM
        gmm = LineConstrainedGMM(
            n_components=n_components,
            line_point=bg_lab,
            line_direction=line_direction,
            covariance_type='full',
            max_iter=100,
        )
        gmm.fit(cut_subset)
        
        means = gmm.means_
        proba = gmm.predict_proba(cut_subset)
        cluster_labels = np.argmax(proba, axis=1)
        nums, counts = np.unique(cluster_labels, return_counts=True)
        valid = nums[counts >= min_points_per_cluster]
        elim = nums[counts < min_points_per_cluster]
        proba[:, elim] = -1
        cluster_labels = np.argmax(proba, axis=1)
        
        # Plot 1: Original points with distance threshold
        axs[0].scatter(cut_subset[:, 0], cut_subset[:, 1], cut_subset[:, 2], 
                      color="green", alpha=0.3, s=20)
        axs[0].scatter(comp_subset[:, 0], comp_subset[:, 1], comp_subset[:, 2], 
                      color="black", alpha=0.3, s=20)
        axs[0].plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color='orange', linewidth=2)
        axs[0].scatter(bg_lab[0], bg_lab[1], bg_lab[2], color="black", marker="*", s=200)
        axs[0].set_title(f"Points Added: {frame_idx}")
        
        # Plot 2: Clusters with all components
        for k in range(len(label_colors)):
            cluster_points = current_subset[current_labels == thickness[k]]
            axs[1].scatter(cluster_points[:, 0], cluster_points[:, 1], cluster_points[:, 2],
                              color=label_colors[k], alpha=0.1, s=20)
        
        axs[1].scatter(means[:, 0], means[:, 1], means[:, 2], color="cyan", marker="*", s=100, zorder=10)
        axs[1].plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color='orange', linewidth=2)
        axs[1].scatter(bg_lab[0], bg_lab[1], bg_lab[2], color="black", marker="*", s=200)
        axs[1].set_title(f"GMM Clustering (Valid: {len(valid)}, Eliminated: {len(elim)})")
        
        # Plot 3: Valid components only with 2-sigma ellipsoids
        for k in valid:
            cluster_points = cut_subset[cluster_labels == k]
            axs[2].scatter(cluster_points[:, 0], cluster_points[:, 1], cluster_points[:, 2],
                          color=label_colors[k % len(label_colors)], alpha=0.1, s=20)
            
            if gmm.covariance_type == 'full':
                try:
                    eigvals, eigvecs = np.linalg.eigh(gmm.covariances_[k])
                    eigvals = np.sqrt(np.abs(eigvals)) * 2
                    scale_matrix = eigvecs @ np.diag(eigvals) @ eigvecs.T
                    
                    u = np.linspace(0, 2 * np.pi, 20)
                    v = np.linspace(0, np.pi, 15)
                    x_sphere = np.outer(np.cos(u), np.sin(v))
                    y_sphere = np.outer(np.sin(u), np.sin(v))
                    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
                    
                    points_sphere = np.stack([x_sphere, y_sphere, z_sphere], axis=-1)
                    points_scaled = np.zeros_like(points_sphere)
                    for i in range(points_sphere.shape[0]):
                        for j in range(points_sphere.shape[1]):
                            points_scaled[i, j] = scale_matrix @ points_sphere[i, j]
                    
                    x_final = points_scaled[:, :, 0] + means[k, 0]
                    y_final = points_scaled[:, :, 1] + means[k, 1]
                    z_final = points_scaled[:, :, 2] + means[k, 2]
                    
                    axs[2].plot_surface(x_final, y_final, z_final, alpha=0.1, color=label_colors[k % len(label_colors)])
                except np.linalg.LinAlgError:
                    pass
        
        axs[2].scatter(means[valid, 0], means[valid, 1], means[valid, 2],
                      color="cyan", marker="*", s=100, zorder=10)
        axs[2].plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color='orange', linewidth=2)
        axs[2].scatter(bg_lab[0], bg_lab[1], bg_lab[2], color="black", marker="*", s=200)
        axs[2].set_title(f"Valid Components Only ({len(valid)} clusters)")
        
        for ax in axs:
            ax.set_xlabel("L")
            ax.set_ylabel("A")
            ax.set_zlabel("B")
        
        writer.grab_frame()

plt.close()
print(f"GIF saved as gmm_evolution_{args.material}.gif")