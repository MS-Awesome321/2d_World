import numpy as np
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from material import wte2, graphene
import cv2
from sklearn.linear_model import LinearRegression
import argparse

parser = argparse.ArgumentParser(description="Overlay Material Data")
parser.add_argument(
    "-l",
    help="cutoff points greater than bg lab",
    action='store_true'
)
args = parser.parse_args()

# Load data for both materials
def load_material_data(material_name):
    if material_name == 'wte2':
        bg_lab = wte2.target_bg_lab
        d_name = 'pv_wte2_5k.pkl'
        target_dir = "/Users/mayanksengupta/Desktop/WTe2_M100"
    else:  # graphene
        bg_lab = graphene.target_bg_lab
        d_name = 'pv_graphene_5k.pkl'
        target_dir = "/Users/mayanksengupta/Desktop/monolayerGraphene/monolayer_Graphene"
    
    with open(d_name, "rb") as file:
        data = pickle.load(file)
    
    points = data["avg_labs"]
    labels = data["labels"]
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
    coords = np.stack(cleaned_coords, axis=0).astype('int')
    
    return {
        'points': points,
        'labels': labels,
        'names': names,
        'mask_ids': mask_ids,
        'masks': masks,
        'coords': coords,
        'bg_lab': bg_lab,
        'target_dir': target_dir
    }

# Load both materials
wte2_data = load_material_data('wte2')
graphene_data = load_material_data('graphene')

# Apply L cutoff if requested
if args.l:
    m_wte2 = wte2_data['points'][:, 0] < wte2_data['bg_lab'][0]
    wte2_data['points'] = wte2_data['points'][m_wte2]
    wte2_data['labels'] = wte2_data['labels'][m_wte2]
    wte2_data['names'] = wte2_data['names'][m_wte2]
    wte2_data['mask_ids'] = wte2_data['mask_ids'][m_wte2]
    wte2_data['masks'] = wte2_data['masks'][m_wte2]
    wte2_data['coords'] = wte2_data['coords'][m_wte2]
    
    m_graphene = graphene_data['points'][:, 0] < graphene_data['bg_lab'][0]
    graphene_data['points'] = graphene_data['points'][m_graphene]
    graphene_data['labels'] = graphene_data['labels'][m_graphene]
    graphene_data['names'] = graphene_data['names'][m_graphene]
    graphene_data['mask_ids'] = graphene_data['mask_ids'][m_graphene]
    graphene_data['masks'] = graphene_data['masks'][m_graphene]
    graphene_data['coords'] = graphene_data['coords'][m_graphene]

thickness = ["monolayer", "bilayer", "trilayer", "fewlayer", "manylayer", "bulk", "bg", "dirt"]
label_colors = ['blue', 'green', 'red', 'orange', 'black', 'purple', 'magenta', 'yellow']

# Translate points so BG Lab is at origin (0, 0, 0)
reference_bg = wte2_data['bg_lab']
wte2_points_centered = wte2_data['points'] - reference_bg
graphene_points_centered = graphene_data['points'] - graphene_data['bg_lab']

# Create figure with 5 subplots
fig = plt.figure(figsize=(20, 12))
axs = []
axs.append(fig.add_subplot(2, 3, 1, projection='3d'))
axs.append(fig.add_subplot(2, 3, 2, projection='3d', sharex=axs[0], sharey=axs[0], sharez=axs[0]))
axs.append(fig.add_subplot(2, 3, 3, projection='3d', sharex=axs[0], sharey=axs[0], sharez=axs[0]))
axs.append(fig.add_subplot(2, 3, 4))
axs.append(fig.add_subplot(2, 3, 5))

for ax in axs[:3]:
    ax.set_xlabel("L")
    ax.set_ylabel("A")
    ax.set_zlabel("B")
    ax.view_init(elev=5, azim=-140, roll=0)

# Axes 0: Overlay of all points (graphene in red, wte2 in blue)
axs[0].scatter(wte2_points_centered[:, 0], wte2_points_centered[:, 1], wte2_points_centered[:, 2], 
               color='blue', alpha=0.1, label='WTe2')
axs[0].scatter(graphene_points_centered[:, 0], graphene_points_centered[:, 1], graphene_points_centered[:, 2], 
               color='red', alpha=0.1, label='Graphene')
axs[0].scatter(0, 0, 0, color='black', marker='*', s=200, label='BG Lab (WTe2)')
axs[0].legend()
axs[0].set_title('Overlay: WTe2 (blue) vs Graphene (red)')

# Axes 1 & 2: Labels for each material
for l_type in thickness:
    plot_points = wte2_points_centered[wte2_data['labels'] == l_type]
    color = label_colors[thickness.index(l_type)]
    axs[1].scatter(plot_points[:, 0], plot_points[:, 1], plot_points[:, 2], 
                   label=l_type, color=color, alpha=0.1)

for l_type in thickness:
    plot_points = graphene_points_centered[graphene_data['labels'] == l_type]
    color = label_colors[thickness.index(l_type)]
    axs[2].scatter(plot_points[:, 0], plot_points[:, 1], plot_points[:, 2], 
                   label=l_type, color=color, alpha=0.1)

axs[1].scatter(0, 0, 0, color='black', marker='*', s=200, label='BG Lab')
axs[2].scatter(0, 0, 0, color='black', marker='*', s=200, label='BG Lab')
axs[1].set_title('WTe2 Labels')
axs[2].set_title('Graphene Labels')

# Line of best fit for WTe2
X_wte2 = wte2_points_centered[:, 0].reshape(-1, 1)
Y_wte2 = wte2_points_centered[:, 1:]
X_wte2_fit = np.concatenate([X_wte2, np.array([[0]])], axis=0)
Y_wte2_fit = np.concatenate([Y_wte2, np.array([[0, 0]])], axis=0)
weights_wte2 = np.ones(len(X_wte2_fit))
weights_wte2[-1] = 10 * len(X_wte2_fit)
reg_wte2 = LinearRegression().fit(X_wte2_fit, Y_wte2_fit, weights_wte2)
L_fit_wte2 = np.linspace(X_wte2_fit.min(), X_wte2_fit.max(), 100).reshape(-1, 1)
AB_fit_wte2 = reg_wte2.predict(L_fit_wte2)
axs[1].plot(L_fit_wte2.flatten(), AB_fit_wte2[:, 0], AB_fit_wte2[:, 1], 
            color='orange', linewidth=2, label='Best Fit Line')

# Compute direction vector for WTe2 line of best fit
direction_wte2 = np.array([L_fit_wte2[1, 0] - L_fit_wte2[0, 0], 
                           AB_fit_wte2[1, 0] - AB_fit_wte2[0, 0], 
                           AB_fit_wte2[1, 1] - AB_fit_wte2[0, 1]])
direction_wte2 = direction_wte2 / np.linalg.norm(direction_wte2)

# Create orthonormal basis for WTe2 Gaussian
# direction_wte2 is the first axis (sigma=2)
# Find two orthogonal vectors
if abs(direction_wte2[0]) < 0.9:
    ortho1_wte2 = np.cross(direction_wte2, np.array([1, 0, 0]))
else:
    ortho1_wte2 = np.cross(direction_wte2, np.array([0, 1, 0]))
ortho1_wte2 = ortho1_wte2 / np.linalg.norm(ortho1_wte2)
ortho2_wte2 = np.cross(direction_wte2, ortho1_wte2)
ortho2_wte2 = ortho2_wte2 / np.linalg.norm(ortho2_wte2)

# Create rotation matrix and covariance for WTe2
R_wte2 = np.column_stack([direction_wte2, ortho1_wte2, ortho2_wte2])
diag_cov_wte2 = np.diag([2**2, 1**2, 1**2])
cov_wte2 = R_wte2 @ diag_cov_wte2 @ R_wte2.T

print("WTe2 Gaussian Covariance Matrix:")
print(cov_wte2)
print()

# Generate ellipsoid for WTe2
u = np.linspace(0, 2 * np.pi, 30)
v = np.linspace(0, np.pi, 20)
x_sphere = 20 * np.outer(np.cos(u), np.sin(v))
y_sphere = 10 * np.outer(np.sin(u), np.sin(v))
z_sphere = 10 * np.outer(np.ones(np.size(u)), np.cos(v))
ellipsoid_wte2 = np.stack([x_sphere, y_sphere, z_sphere], axis=-1)

# Transform ellipsoid to global coordinates
ellipsoid_wte2_transformed = np.zeros_like(ellipsoid_wte2)
for i in range(ellipsoid_wte2.shape[0]):
    for j in range(ellipsoid_wte2.shape[1]):
        ellipsoid_wte2_transformed[i, j] = R_wte2 @ ellipsoid_wte2[i, j]

# Plot ellipsoid for WTe2
axs[1].plot_surface(ellipsoid_wte2_transformed[:, :, 0], 
                    ellipsoid_wte2_transformed[:, :, 1], 
                    ellipsoid_wte2_transformed[:, :, 2], 
                    alpha=0.2, color='purple')

# Line of best fit for Graphene
X_graphene = graphene_points_centered[:, 0].reshape(-1, 1)
Y_graphene = graphene_points_centered[:, 1:]
X_graphene_fit = np.concatenate([X_graphene, np.array([[0]])], axis=0)
Y_graphene_fit = np.concatenate([Y_graphene, np.array([[0, 0]])], axis=0)
weights_graphene = np.ones(len(X_graphene_fit))
weights_graphene[-1] = 10 * len(X_graphene_fit)
reg_graphene = LinearRegression().fit(X_graphene_fit, Y_graphene_fit, weights_graphene)
L_fit_graphene = np.linspace(X_graphene_fit.min(), X_graphene_fit.max(), 100).reshape(-1, 1)
AB_fit_graphene = reg_graphene.predict(L_fit_graphene)
axs[2].plot(L_fit_graphene.flatten(), AB_fit_graphene[:, 0], AB_fit_graphene[:, 1], 
            color='orange', linewidth=2, label='Best Fit Line')

# Compute direction vector for Graphene line of best fit
direction_graphene = np.array([L_fit_graphene[1, 0] - L_fit_graphene[0, 0], 
                               AB_fit_graphene[1, 0] - AB_fit_graphene[0, 0], 
                               AB_fit_graphene[1, 1] - AB_fit_graphene[0, 1]])
direction_graphene = direction_graphene / np.linalg.norm(direction_graphene)

# Create orthonormal basis for Graphene Gaussian
if abs(direction_graphene[0]) < 0.9:
    ortho1_graphene = np.cross(direction_graphene, np.array([1, 0, 0]))
else:
    ortho1_graphene = np.cross(direction_graphene, np.array([0, 1, 0]))
ortho1_graphene = ortho1_graphene / np.linalg.norm(ortho1_graphene)
ortho2_graphene = np.cross(direction_graphene, ortho1_graphene)
ortho2_graphene = ortho2_graphene / np.linalg.norm(ortho2_graphene)

# Create rotation matrix and covariance for Graphene
R_graphene = np.column_stack([direction_graphene, ortho1_graphene, ortho2_graphene])
diag_cov_graphene = np.diag([2**2, 1**2, 1**2])
cov_graphene = R_graphene @ diag_cov_graphene @ R_graphene.T

print("Graphene Gaussian Covariance Matrix:")
print(cov_graphene)
print()

# Generate ellipsoid for Graphene
ellipsoid_graphene = np.stack([x_sphere, y_sphere, z_sphere], axis=-1)

# Transform ellipsoid to global coordinates
ellipsoid_graphene_transformed = np.zeros_like(ellipsoid_graphene)
for i in range(ellipsoid_graphene.shape[0]):
    for j in range(ellipsoid_graphene.shape[1]):
        ellipsoid_graphene_transformed[i, j] = R_graphene @ ellipsoid_graphene[i, j]

# Plot ellipsoid for Graphene
axs[2].plot_surface(ellipsoid_graphene_transformed[:, :, 0], 
                    ellipsoid_graphene_transformed[:, :, 1], 
                    ellipsoid_graphene_transformed[:, :, 2], 
                    alpha=0.2, color='cyan')

# Interactive format_coord for WTe2 (axes 1 and 3)
xs_wte2, ys_wte2, zs_wte2 = wte2_points_centered[:, 0], wte2_points_centered[:, 1], wte2_points_centered[:, 2]

def format_coord_wte2(x, y):
    x_s, y_s, _ = proj3d.proj_transform(xs_wte2, ys_wte2, zs_wte2, axs[1].get_proj())
    distances_sq = (x - x_s) ** 2 + (y - y_s) ** 2
    idx = np.argmin(distances_sq)
    
    fname = wte2_data['names'][idx]
    img = cv2.imread(f"{wte2_data['target_dir']}/{fname}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[0] // 4, img.shape[1] // 4
    img = img[h:-h, w:-w]
    img = cv2.resize(img, None, fx=0.2, fy=0.2)
    
    axs[3].cla()
    axs[3].imshow(img)
    x_coord, y_coord = wte2_data['coords'][idx]
    x_coord //= 5
    y_coord //= 5
    axs[3].scatter(y_coord, x_coord)
    axs[3].set_title(f"WTe2: {fname}")
    fig.canvas.draw_idle()
    
    return f"x={x:.2f}, y={y:.2f}"

# Interactive format_coord for Graphene (axes 2 and 4)
xs_graphene, ys_graphene, zs_graphene = graphene_points_centered[:, 0], graphene_points_centered[:, 1], graphene_points_centered[:, 2]

def format_coord_graphene(x, y):
    x_s, y_s, _ = proj3d.proj_transform(xs_graphene, ys_graphene, zs_graphene, axs[2].get_proj())
    distances_sq = (x - x_s) ** 2 + (y - y_s) ** 2
    idx = np.argmin(distances_sq)
    
    fname = graphene_data['names'][idx]
    img = cv2.imread(f"{graphene_data['target_dir']}/{fname}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, None, fx=0.1, fy=0.1)
    
    axs[4].cla()
    axs[4].imshow(img)
    x_coord, y_coord = graphene_data['coords'][idx]
    x_coord //= 5
    y_coord //= 5
    axs[4].scatter(y_coord, x_coord)
    axs[4].set_title(f"Graphene: {fname}")
    fig.canvas.draw_idle()
    
    return f"x={x:.2f}, y={y:.2f}"

axs[1].format_coord = format_coord_wte2
axs[2].format_coord = format_coord_graphene

plt.tight_layout()
plt.show()