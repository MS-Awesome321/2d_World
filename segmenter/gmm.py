from scipy.stats import multivariate_normal
import numpy as np

class LineConstrainedGMM:
    """
    Fast GMM where component means are constrained to lie on a line.
    Uses vectorized operations and scipy for PDF computation.
    With safeguards against component collapse.
    """
    
    def __init__(self, n_components=1, line_point=None, line_direction=None, 
                 covariance_type='full', max_iter=100, tol=1e-4, random_state=None,
                 min_component_weight=0.01, sep_penalty=0.0, verbose=False):
        """
        Args:
            n_components: Number of Gaussian components
            line_point: Point on the constraint line
            line_direction: Direction vector of the line
            covariance_type: 'full', 'diag', or 'spherical'
            max_iter: Maximum EM iterations
            tol: Convergence tolerance
            random_state: Random seed
            min_component_weight: Minimum weight for each component (default: 1%)
                Prevents components from disappearing
            sep_penalty: Separation penalty (0.0 to 1.0)
                Encourages components to stay separated along the line
            verbose: Print training steps
        """
        self.n_components = n_components
        self.line_point = np.array(line_point, dtype=np.float64) if line_point is not None else np.zeros(3)
        self.line_direction = np.array(line_direction, dtype=np.float64) if line_direction is not None else np.array([1, 0, 0])
        self.line_direction = self.line_direction / np.linalg.norm(self.line_direction)
        self.covariance_type = covariance_type
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.min_component_weight = min_component_weight
        self.sep_penalty = sep_penalty
        self.verbose = verbose
        
        self.means_ = None
        self.covariances_ = None
        self.weights_ = None
        self.converged_ = False
        self.n_iter_ = 0
    
    def _initialize_parameters(self, X):
        """Fast initialization with even spacing"""
        n_samples, n_features = X.shape
        rng = np.random.RandomState(self.random_state)
        
        # Project all points onto line and use quantiles for initialization
        projections = (X - self.line_point) @ self.line_direction
        positions = np.linspace(projections.min(), projections.max(), self.n_components)
        
        self.means_ = self.line_point[np.newaxis, :] + positions[:, np.newaxis] * self.line_direction[np.newaxis, :]
        noise = rng.normal(0, 1, size=self.means_.shape)
        self.means_ += noise
        
        # Fast covariance initialization
        if self.covariance_type == 'full':
            self.covariances_ = np.array([np.eye(n_features) for _ in range(self.n_components)])
        elif self.covariance_type == 'diag':
            self.covariances_ = np.ones((self.n_components, n_features))
        elif self.covariance_type == 'spherical':
            self.covariances_ = np.ones(self.n_components)
        
        self.weights_ = np.ones(self.n_components) / self.n_components
    
    def _enforce_minimum_weight(self):
        """Enforce minimum component weight to prevent collapse"""
        n_samples_min = self.min_component_weight
        
        # Find components below minimum
        below_min = self.weights_ < self.min_component_weight
        
        if np.any(below_min):
            # Redistribute weight from components above minimum to those below
            weights_above = self.weights_[~below_min]
            excess = np.sum(weights_above) - (1.0 - self.min_component_weight * np.sum(below_min))
            
            if excess > 0:
                # Scale down components above minimum
                self.weights_[~below_min] = weights_above * (1.0 - excess / np.sum(weights_above))
            
            # Set minimum weights
            self.weights_[below_min] = self.min_component_weight
            
            # Normalize
            self.weights_ = self.weights_ / np.sum(self.weights_)
    
    def _compute_separation_penalty(self):
        """Compute penalty for components that are too close together"""
        if self.sep_penalty == 0:
            return 0.0
        
        # Compute pairwise distances between means (projected on line)
        projections = (self.means_ - self.line_point) @ self.line_direction
        
        penalty = 0.0
        for i in range(self.n_components):
            for j in range(i + 1, self.n_components):
                dist = abs(projections[i] - projections[j])
                min_dist = 0.5  # Minimum expected separation
                
                if dist < min_dist:
                    penalty += self.sep_penalty * (min_dist - dist) ** 2
        
        return penalty
    
    def _e_step(self, X):
        """Fast E-step with separation penalty"""
        n_samples = X.shape[0]
        resp = np.zeros((n_samples, self.n_components))
        
        for k in range(self.n_components):
            if self.covariance_type == 'full':
                try:
                    dist = multivariate_normal(mean=self.means_[k], cov=self.covariances_[k])
                    resp[:, k] = self.weights_[k] * dist.pdf(X)
                except np.linalg.LinAlgError:
                    resp[:, k] = self.weights_[k] * 1e-10
            elif self.covariance_type == 'diag':
                diff = X - self.means_[k]
                resp[:, k] = self.weights_[k] * np.exp(-0.5 * np.sum(diff**2 / (self.covariances_[k] + 1e-10), axis=1))
                resp[:, k] /= np.sqrt(np.prod(2 * np.pi * self.covariances_[k]))
            elif self.covariance_type == 'spherical':
                diff = X - self.means_[k]
                resp[:, k] = self.weights_[k] * np.exp(-0.5 * np.sum(diff**2, axis=1) / (self.covariances_[k] + 1e-10))
                resp[:, k] /= (2 * np.pi * self.covariances_[k]) ** (X.shape[1] / 2)
        
        # Normalize with numerical stability
        resp_sum = resp.sum(axis=1, keepdims=True)
        resp_sum[resp_sum == 0] = 1e-10
        resp = resp / resp_sum
        
        return resp
    
    def _m_step(self, X, resp):
        """Fast M-step with vectorization"""
        n_samples, n_features = X.shape
        nk = resp.sum(axis=0)
        
        # Enforce minimum samples per component
        nk = np.maximum(nk, n_samples * self.min_component_weight)
        
        # Update weights with enforcement
        self.weights_ = nk / n_samples
        self._enforce_minimum_weight()
        
        # Update means with line constraint (vectorized)
        weighted_X = (resp.T @ X)
        new_means = weighted_X / nk[:, np.newaxis]
        
        # Project onto line (vectorized)
        to_means = new_means - self.line_point
        proj_lengths = (to_means @ self.line_direction)
        self.means_ = self.line_point + proj_lengths[:, np.newaxis] * self.line_direction
        
        # Re-space means if they're collapsing together (optional adaptive spacing)
        projections = proj_lengths
        projections_sorted = np.sort(projections)
        min_spacing = (projections_sorted[-1] - projections_sorted[0]) / (self.n_components - 1) if self.n_components > 1 else 1.0
        
        # Ensure minimum spacing
        if min_spacing > 0:
            for k in range(self.n_components - 1):
                if projections[k + 1] - projections[k] < min_spacing * 0.5:
                    # Adjust spacing
                    projections[k + 1] = projections[k] + min_spacing * 0.5
        
        self.means_ = self.line_point + projections[:, np.newaxis] * self.line_direction
        
        # Fast covariance update
        if self.covariance_type == 'full':
            self.covariances_ = np.zeros((self.n_components, n_features, n_features))
            for k in range(self.n_components):
                diff = X - self.means_[k]
                weighted_diff = resp[:, k, np.newaxis] * diff
                self.covariances_[k] = (weighted_diff.T @ diff) / nk[k]
                # Enforce minimum variance
                self.covariances_[k] += np.eye(n_features) * 1e-2
        
        elif self.covariance_type == 'diag':
            self.covariances_ = np.zeros((self.n_components, n_features))
            for k in range(self.n_components):
                diff = X - self.means_[k]
                self.covariances_[k] = (resp[:, k] @ (diff ** 2)) / nk[k]
                self.covariances_[k] = np.maximum(self.covariances_[k], 1e-2)
        
        elif self.covariance_type == 'spherical':
            self.covariances_ = np.zeros(self.n_components)
            for k in range(self.n_components):
                diff = X - self.means_[k]
                self.covariances_[k] = np.sum(resp[:, k] * np.sum(diff ** 2, axis=1)) / (nk[k] * n_features)
                self.covariances_[k] = max(self.covariances_[k], 1e-2)
    
    def fit(self, X):
        """Fast fit with early stopping"""
        X = np.asarray(X, dtype=np.float64)
        self._initialize_parameters(X)
        
        prev_weight_change = np.inf
        
        for iteration in range(self.max_iter):
            resp = self._e_step(X)
            old_weights = self.weights_.copy()
            self._m_step(X, resp)
            
            weight_change = np.max(np.abs(self.weights_ - old_weights))
            
            if iteration % 10 == 0:
                min_weight = np.min(self.weights_)
                max_weight = np.max(self.weights_)
                if self.verbose:
                    print(f"Iter {iteration}: weight range [{min_weight:.4f}, {max_weight:.4f}]")
            
            if weight_change < self.tol:
                self.converged_ = True
                self.n_iter_ = iteration + 1
                break
            
            prev_weight_change = weight_change
        
        self.n_iter_ = iteration + 1
        return self
    
    def predict(self, X):
        """Predict cluster labels"""
        resp = self._e_step(X)
        return np.argmax(resp, axis=1)
    
    def predict_proba(self, X):
        """Predict soft assignments"""
        return self._e_step(X)


# MAIN METHOD
if __name__=='__main__':
    import pickle
    import matplotlib.pyplot as plt
    from material import graphene, wte2
    from sklearn.linear_model import LinearRegression
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
        d_name = 'points_wte2.pkl'
    elif args.material == 'graphene':
        bg_lab = graphene.target_bg_lab
        d_name = 'points_graphene.pkl'
    else:
        raise ValueError("Invalid Material")

    # LOAD DATA
    with open(d_name, "rb") as file:
        data = pickle.load(file)

    points = data["avg_labs"]
    labels = data["labels"]

    if args.l:
        m = points[:, 0] < bg_lab[0]
        points = points[m]
        labels = labels[m]

    def compute_line_distance(line_point, line_direction,X):
        """Compute distance of each point from the line"""
        # Vector from line_point to each data point
        to_points = X - line_point
        
        # Project onto line direction
        proj_lengths = (to_points @ line_direction)[:, np.newaxis]
        projections = line_point + proj_lengths * line_direction
        
        # Distance from line
        distances = np.linalg.norm(X - projections, axis=1)
        
        return distances
    
    

    # PLOT POINTS
    fig = plt.figure(figsize=(15, 8))
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

    for t, color in zip(thickness, label_colors):
        plot_points = points[labels == t]
        axs[1].scatter(plot_points[:, 0], plot_points[:, 1], plot_points[:, 2], label=t, color=color, alpha=0.1)

    # GET LINE OF BEST FIT
    X = points[:, 0].reshape(-1, 1) 
    Y = points[:, 1:]

    X = np.concatenate([X, np.expand_dims(bg_lab[:1], axis=0)], axis=0)
    Y = np.concatenate([Y, np.expand_dims(bg_lab[1:], axis=0)], axis=0)
    weights = np.ones(len(X))
    weights[-1] = 10*len(X)

    reg = LinearRegression().fit(X, Y, weights)
    L_fit = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    AB_fit = reg.predict(L_fit)


    line_direction = np.array([1, reg.coef_[0, 0], reg.coef_[1, 0]])
    line_direction = line_direction / np.linalg.norm(line_direction)

    for ax in axs:
        ax.plot(L_fit.flatten(), AB_fit[:, 0], AB_fit[:, 1], color='orange', linewidth=2, label='Best Fit Line')
        ax.scatter(bg_lab[0], bg_lab[1], bg_lab[2], color="black", label="BG Lab", marker="*", s=200)


    distances = compute_line_distance(bg_lab, line_direction, points)
    d = 20
    subset = points[distances < d]
    complement = points[distances >= d]

    axs[0].scatter(subset[:, 0], subset[:, 1], subset[:, 2], color="green", alpha=0.3, zorder=0)
    axs[0].scatter(complement[:, 0], complement[:, 1], complement[:, 2], color="black", alpha=0.1, zorder=0)

    # GMM STUFF
    gmm = LineConstrainedGMM(
        n_components=15,
        line_point=bg_lab,
        line_direction=line_direction,
        covariance_type='full',
        max_iter=1000,
    )

    gmm.fit(subset)

    means = gmm.means_

    for ax in axs[:-1]:
        ax.scatter(means[:, 0], means[:, 1], means[:, 2], color="cyan", marker="*", s=100, zorder=10)

    # Plot subset colored by GMM prediction on axs[2]
    proba = gmm.predict_proba(subset)

    min_points = 50

    cluster_labels = np.argmax(proba, axis=1)
    nums, counts = np.unique(cluster_labels, return_counts=True)
    valid = nums[counts >= min_points]
    elim = nums[counts < min_points]
    proba[:, elim] = -1
    cluster_labels = np.argmax(proba, axis=1)


    # Plot 2-sigma ellipsoids for each component
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 20)
    min_points = 100
    
    for k in valid:
        if gmm.covariance_type == 'spherical':
            sigma = np.sqrt(gmm.covariances_[k]) * 2  # 2-sigma
            scale = np.array([sigma, sigma, sigma])
        elif gmm.covariance_type == 'diag':
            sigma = np.sqrt(gmm.covariances_[k]) * 2
            scale = sigma
        elif gmm.covariance_type == 'full':
            eigvals, eigvecs = np.linalg.eigh(gmm.covariances_[k])
            eigvals = np.sqrt(np.abs(eigvals)) * 2
            scale_matrix = eigvecs @ np.diag(eigvals) @ eigvecs.T
        
        x_sphere = np.outer(np.cos(u), np.sin(v))
        y_sphere = np.outer(np.sin(u), np.sin(v))
        z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
        
        if gmm.covariance_type in ['spherical', 'diag']:
            x_scaled = x_sphere * scale[0]
            y_scaled = y_sphere * scale[1]
            z_scaled = z_sphere * scale[2]
        else:
            points_sphere = np.stack([x_sphere, y_sphere, z_sphere], axis=-1)
            points_scaled = np.zeros_like(points_sphere)
            for i in range(points_sphere.shape[0]):
                for j in range(points_sphere.shape[1]):
                    points_scaled[i, j] = scale_matrix @ points_sphere[i, j]
            x_scaled = points_scaled[:, :, 0]
            y_scaled = points_scaled[:, :, 1]
            z_scaled = points_scaled[:, :, 2]
        
        x_final = x_scaled + means[k, 0]
        y_final = y_scaled + means[k, 1]
        z_final = z_scaled + means[k, 2]
        
        # Plot ellipsoid
        for ax in axs:
            ax.plot_surface(x_final, y_final, z_final, alpha=0.05, color=label_colors[k % len(label_colors)])

        cluster_points = subset[cluster_labels == k]
        axs[2].scatter(cluster_points[:, 0], cluster_points[:, 1], cluster_points[:, 2], 
                        color=label_colors[k % len(label_colors)], label=f"Cluster {k}", alpha=0.1)
        
        axs[2].scatter(means[k, 0], means[k, 1], means[k, 2], color="cyan", marker="*", s=100, zorder=10)

    axs[0].set_title("Subset Used for GMM Clustering")
    axs[1].set_title("Original Segmenter Labels")
    axs[2].set_title("GMM Clustering")
    plt.show()
