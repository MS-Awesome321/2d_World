import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.linear_model import LinearRegression

# Load in and process data
with open("data_graphene_new.pkl", "rb") as file:
    data = pickle.load(file)

n_components = 3

all_points = []
all_labels = []
for points, labels in zip(data["avg_labs"], data["labels"]):
    all_points.extend(points)
    all_labels.extend(labels)

label_colors = ['blue', 'green', 'red', 'orange', 'purple']
# thickness = ["0-10", "10-20", "20-30", "30-40", "40+"]
thickness = ["monolayer", "bilayer", "trilayer", "manylayer", "bulk"]

all_points = np.stack(all_points, axis=0)
all_labels = np.array(all_labels)

# Display data
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), subplot_kw={'projection': '3d'}, sharex=True, sharey=True)
ax1.set_xlabel("L")
ax1.set_ylabel("A")
ax1.set_zlabel("B")

for i in range(n_components):
    plot_points = all_points[all_labels == i]
    color = label_colors[i]
    ax1.scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color=color, label=thickness[i])

ax1.set_title("Color Distributions of Graphene flakes")

ax2.set_xlabel("L")
ax2.set_ylabel("A")
ax2.set_zlabel("B")


# CLUSTERING MODELS

# model = KMeans(n_clusters=n_components)
# model = AgglomerativeClustering(n_clusters=n_components)
model = DBSCAN(eps=0.9, min_samples=6)
# model = GaussianMixture(n_components, n_init=3, random_state=42)

subset = all_points[np.logical_and(all_labels >= 0, all_labels < n_components)]
subset_labels = all_labels[np.logical_and(all_labels >= 0, all_labels < n_components)]
predicted_labels = model.fit_predict(subset)

print(f"Num Classes: {np.max(predicted_labels) + 1}")

mask = predicted_labels!=-1
predicted_labels_masked = predicted_labels[mask]
subset_labels = subset_labels[mask]
subset_masked = subset[mask]

cm = confusion_matrix(subset_labels, predicted_labels_masked)
row_ind, col_ind = linear_sum_assignment(-cm)
label_map = dict(zip(col_ind, row_ind))
mapped_labels = np.array([label_map[label] for label in predicted_labels_masked])

for i in range(n_components):
    plot_points = subset_masked[mapped_labels == i]
    color = label_colors[i]
    ax2.scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color=color, label=thickness[i])

# Outliers
plot_points = subset_masked[mapped_labels > n_components]
ax2.scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color="magenta", label="outliers")

plot_points = subset[predicted_labels == -1]
ax2.scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color="magenta")

# BG Lab Color
bg_lab = np.array([[49.62793933, 12.17574073,  5.43972594]])
ax1.scatter(bg_lab[:,0], bg_lab[:,1], bg_lab[:,2], color="black", label="BG Lab")
ax2.scatter(bg_lab[:,0], bg_lab[:,1], bg_lab[:,2], color="black", label="BG Lab")

def get_acc(pred, true, predicted_labels=None):
    if predicted_labels is not None:
        num_outliers = np.sum(predicted_labels == -1)
        return np.sum(pred == true) / (len(true) + num_outliers)
    return np.sum(pred == true) / len(true)

print(get_acc(mapped_labels, subset_labels, predicted_labels))
# print(model.cluster_centers_)

ax2.set_title("Predicted Color Distributions")
ax1.legend()
ax2.legend()

mask2 = mapped_labels < n_components
mapped_labels = mapped_labels[mask2]
subset_labels = subset_labels[mask2]
cm = confusion_matrix(subset_labels, mapped_labels)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=thickness[:n_components])
disp.plot()

plt.show()
