import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from sklearn.linear_model import LinearRegression
from tqdm import tqdm
from material import wte2, graphene

# Initialize GIF Writers
metadata_wte2 = {
    "title": "Sequential Line of Best Fit - WTe2",
    "artist": "Mayank Sengupta"
}
metadata_graphene = {
    "title": "Sequential Line of Best Fit - Graphene",
    "artist": "Mayank Sengupta"
}
writer_wte2 = PillowWriter(fps=6, metadata=metadata_wte2)
writer_graphene = PillowWriter(fps=6, metadata=metadata_graphene)

# Load data for both materials
def load_material_data(material_name):
    if material_name == 'wte2':
        bg_lab = wte2.target_bg_lab
        d_name = 'pv_wte2_5k.pkl'
    else:  # graphene
        bg_lab = graphene.target_bg_lab
        d_name = 'pv_graphene_5k.pkl'
    
    with open(d_name, "rb") as file:
        data = pickle.load(file)
    
    points = data["avg_labs"]
    labels = data["labels"]
    
    return points, labels, bg_lab

# Load both materials
wte2_points, wte2_labels, wte2_bg_lab = load_material_data('wte2')
graphene_points, graphene_labels, graphene_bg_lab = load_material_data('graphene')

thickness = ["monolayer", "bilayer", "trilayer", "fewlayer", "manylayer", "bulk", "bg", "dirt"]
label_colors = ['blue', 'green', 'red', 'orange', 'black', 'purple', 'magenta', 'yellow']

n_layers = 6  # monolayer through bulk

def create_experiment(points, labels, bg_lab, material_name, writer):
    """Create sequential fit experiment for a material"""
    
    # Convert string labels to numeric indices
    label_to_idx = {label: idx for idx, label in enumerate(thickness)}
    numeric_labels = np.array([label_to_idx.get(label, -1) for label in labels])
    
    # Filter to valid labels
    mask = np.logical_and(numeric_labels >= 0, numeric_labels < n_layers)
    subset = points[mask]
    subset_labels = numeric_labels[mask]
    
    # Separate monolayer and non-monolayer points
    monolayer_mask = subset_labels == 0
    non_monolayer_mask = subset_labels > 0
    
    monolayer_points = subset[monolayer_mask]
    monolayer_labels = subset_labels[monolayer_mask]
    non_monolayer_points = subset[non_monolayer_mask]
    non_monolayer_labels = subset_labels[non_monolayer_mask]
    
    # Shuffle non-monolayer points
    non_mono_idxs = np.random.permutation(len(non_monolayer_points))
    non_monolayer_points = non_monolayer_points[non_mono_idxs]
    non_monolayer_labels = non_monolayer_labels[non_mono_idxs]
    
    # Shuffle monolayer points
    mono_idxs = np.random.permutation(len(monolayer_points))
    monolayer_points = monolayer_points[mono_idxs]
    monolayer_labels = monolayer_labels[mono_idxs]
    
    # Interleave monolayer points sparsely throughout the sequence
    n_non_mono = len(non_monolayer_points)
    n_mono = len(monolayer_points)
    
    # Create sequence by adding non-monolayer points and interleaving monolayer
    sequence_points = []
    sequence_labels = []
    mono_idx = 0
    mono_interval = max(1, n_non_mono // (n_mono + 1))
    
    for i, (point, label) in enumerate(zip(non_monolayer_points, non_monolayer_labels)):
        sequence_points.append(point)
        sequence_labels.append(label)
        
        # Add a monolayer point every mono_interval steps
        if mono_idx < n_mono and (i + 1) % mono_interval == 0:
            sequence_points.append(monolayer_points[mono_idx])
            sequence_labels.append(monolayer_labels[mono_idx])
            mono_idx += 1
    
    # Add remaining monolayer points at the end
    while mono_idx < n_mono:
        sequence_points.append(monolayer_points[mono_idx])
        sequence_labels.append(monolayer_labels[mono_idx])
        mono_idx += 1
    
    sequence_points = np.array(sequence_points)
    sequence_labels = np.array(sequence_labels)
    
    # Create figure
    fig, axs = plt.subplots(1, 2, figsize=(12, 8), subplot_kw={'projection': '3d'})
    fig.suptitle(f"Sequential Line of Best Fit - {material_name}")
    
    for ax in axs:
        ax.set_xlabel("L")
        ax.set_ylabel("A")
        ax.set_zlabel("B")
        ax.view_init(elev=30, azim=-130, roll=0)
    
    # Write GIF
    with writer.saving(fig, f"sequential_{material_name.lower()}.gif", 100):
        for i in tqdm(range(2, len(sequence_points), 5), desc=f"Creating {material_name} GIF"):
            for ax in axs:
                ax.clear()
            
            # Current dataset
            current_set = sequence_points[:i, :]
            current_labels = sequence_labels[:i]
            
            # Linear regression
            X = current_set[:, 0].reshape(-1, 1)
            Y = current_set[:, 1:]
            X[0] = np.expand_dims(bg_lab[:1], axis=0)
            Y[0] = np.expand_dims(bg_lab[1:], axis=0)
            weights = np.ones(len(X))
            weights[0] = 2*len(X)
            reg = LinearRegression().fit(X, Y, weights)
            
            L_fit = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
            AB_fit = reg.predict(L_fit)
            
            # Compute projections
            intercept = np.array([L_fit[0][0], AB_fit[0][0], AB_fit[0][1]])
            normalized = current_set - intercept
            direction = np.array([L_fit[1][0], AB_fit[1][0], AB_fit[1][1]]) - intercept
            direction_norm = direction / np.linalg.norm(direction)
            projection = normalized @ direction_norm
            
            # Axis 0: Labeled dataset
            for label in range(n_layers):
                sub = current_set[current_labels == label]
                if len(sub) > 0:
                    axs[0].scatter(sub[:, 0], sub[:, 1], sub[:, 2], 
                                 color=label_colors[label], label=thickness[label], alpha=0.6)
            
            # Axis 1: Projection onto line of best fit
            axs[1].scatter(current_set[:, 0], current_set[:, 1], current_set[:, 2], 
                         c=projection, cmap='inferno', alpha=0.6)
            axs[1].plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], 
                       color="gray", linewidth=2, label='Best Fit Line')
            
            # Add BG Lab point
            axs[0].scatter(bg_lab[0], bg_lab[1], bg_lab[2], 
                         color="black", marker="*", s=300, label="BG Lab")
            axs[1].scatter(bg_lab[0], bg_lab[1], bg_lab[2], 
                         color="black", marker="*", s=300, label="BG Lab")
            
            axs[0].legend(loc='upper left', fontsize=8)
            axs[1].legend()
            axs[0].set_title("Labeled Dataset")
            axs[1].set_title(f"Projection onto Line of Best Fit (n={i})")
            
            writer.grab_frame()
    
    plt.close(fig)

# Run experiments for both materials
create_experiment(wte2_points, wte2_labels, wte2_bg_lab, 'WTe2', writer_wte2)
create_experiment(graphene_points, graphene_labels, graphene_bg_lab, 'Graphene', writer_graphene)

print("GIFs created: sequential_wte2.gif and sequential_graphene.gif")