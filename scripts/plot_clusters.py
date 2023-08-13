import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN

from dotenv import load_dotenv
load_dotenv()
from agentmemory import get_memories

claims = get_memories(category="claims", include_embeddings=True)
paragraphs = get_memories(category="paragraphs", include_embeddings=True)
documents = get_memories(category="documents", include_embeddings=True)

data = claims + paragraphs + documents

# Extract Embeddings
embeddings = np.array([entry['embedding'] for entry in data])

# Perform K-Means Clustering
kmeans = KMeans(n_clusters=10)
kmeans_cluster_ids = kmeans.fit_predict(embeddings)

# Perform PCA with 3 components for 3D plot
pca_3d = PCA(n_components=3)
reduced_embeddings_3d = pca_3d.fit_transform(embeddings)

# Perform PCA with 2 components for 2D plot
pca_2d = PCA(n_components=2)
reduced_embeddings_2d = pca_2d.fit_transform(embeddings)

# Get number of unique clusters for both algorithms
num_clusters = len(set(kmeans_cluster_ids))

# set the colors
colors = plt.cm.rainbow(np.linspace(0, 1, num_clusters))

# Plotting
fig = plt.figure(figsize=(12, 5))

# K-Means 3D plot
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
for index in range(kmeans.n_clusters):
    color = colors[index]
    points_in_cluster_3d = reduced_embeddings_3d[kmeans_cluster_ids == index]
    ax1.scatter(points_in_cluster_3d[:, 0], points_in_cluster_3d[:, 1], points_in_cluster_3d[:, 2], c=[color], label=f'Cluster {index}')

ax1.set_title('K-Means 3D Clusters')
ax1.set_xlabel('PCA Component 1')
ax1.set_ylabel('PCA Component 2')
ax1.set_zlabel('PCA Component 3')

# K-Means 2D plot
ax2 = fig.add_subplot(1, 2, 2)
for index in range(kmeans.n_clusters):
    color = colors[index]
    points_in_cluster_2d = reduced_embeddings_2d[kmeans_cluster_ids == index]
    ax2.scatter(points_in_cluster_2d[:, 0], points_in_cluster_2d[:, 1], c=[color], label=f'Cluster {index}')

ax2.set_title('K-Means 2D Clusters')
ax2.set_xlabel('PCA Component 1')
ax2.set_ylabel('PCA Component 2')

plt.tight_layout()
plt.show()
