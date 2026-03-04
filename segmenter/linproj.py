import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.cluster import DBSCAN

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

# Clustering
model = DBSCAN(eps=5, min_samples=2)
predicted_labels = model.fit_predict(all_points)
subset = all_points[predicted_labels == 0]
subset_labels = all_labels[predicted_labels == 0]

# Display data
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8), subplot_kw={'projection': '3d'})
fig.suptitle("Color Distributions of Graphene flakes")
ax1.set_xlabel("L")
ax1.set_ylabel("A")
ax1.set_zlabel("B")

# Axis 1
for i in range(len(label_colors)):
    plot_points = subset[subset_labels == i]
    color = label_colors[i]
    ax1.scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color=color, label=thickness[i])

ax2.set_xlabel("L")
ax2.set_ylabel("A")
ax2.set_zlabel("B")

# Line of Best Fit
X = subset[:, 0].reshape(-1, 1) 
Y = subset[:, 1:]

reg = LinearRegression().fit(X, Y)
L_fit = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
AB_fit = reg.predict(L_fit)

ax1.plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color='orange', linewidth=2, label='Best Fit Line')
ax2.plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color='orange', linewidth=2, label='Best Fit Line')

# Axis 2
intercept = np.array([L_fit[0][0], AB_fit[0][0], AB_fit[0][1]])
normalized = subset - intercept
direction = np.array([L_fit[1][0], AB_fit[1][0], AB_fit[1][1]]) - intercept
c = normalized @ direction
ax2.scatter(subset[:,0], subset[:,1], subset[:,2], c=c, cmap='inferno')

# BG Lab Color
bg_lab = np.array([[49.62793933, 12.17574073,  5.43972594]])
ax1.scatter(bg_lab[:,0], bg_lab[:,1], bg_lab[:,2], color="black", label="BG Lab")
ax2.scatter(bg_lab[:,0], bg_lab[:,1], bg_lab[:,2], color="green", label="BG Lab")

ax1.legend()
ax2.legend()

# Axis 3 (Whole Dataset with Labels)
for i in range(len(label_colors)):
    plot_points = all_points[all_labels == i]
    color = label_colors[i]
    ax3.scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color=color, label=thickness[i])


# Axis 4 (Clustering Results)
for i in range(np.max(predicted_labels) + 1):
    plot_points = all_points[predicted_labels == i]
    if i < len(label_colors):
        color = label_colors[i]
    else:
        color = "black"
    ax4.scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color=color)

plot_points = all_points[predicted_labels == -1]
ax4.scatter(plot_points[:,0], plot_points[:,1], plot_points[:,2], color='magenta', label="outliers")
ax4.legend()

# Histogram
# plt.figure()
# plt.hist(c)

plt.tight_layout()
plt.show()
