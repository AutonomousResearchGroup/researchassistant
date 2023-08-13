import json
import numpy as np
import matplotlib.pyplot as plt
import json
import numpy as np
from sklearn.decomposition import PCA

from dotenv import load_dotenv
load_dotenv()
from agentmemory import get_memories

data = get_memories(category="claims", include_embeddings=True)

print("data")
print(data)

if not data or 'embedding' not in data[0]:
    print("No embeddings found. Ensure the data is correct.")
    exit()


# perform PCA on claims and store the PCA vector as JSON in metadata
# goal is to reduce to 2D for visualization
# Step 1: Extract Embeddings and Cluster IDs
embeddings = np.array([entry['embedding'] for entry in data])

if embeddings.ndim != 2:
    print(f"Unexpected shape of embeddings: {embeddings.shape}. Ensure each embedding is a vector.")
    exit()
    
cluster_ids = np.array([entry['metadata']['cluster'] for entry in data])
# Step 2: Perform PCA
pca = PCA(n_components=2)

print('embeddings')
print(embeddings)

reduced_embeddings = pca.fit_transform(embeddings)

unique_cluster_ids = list(set(cluster_ids))
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_cluster_ids)))

for index, cluster_id in enumerate(unique_cluster_ids):
    if cluster_id == -1:
        color = 'k'
        label = 'Noise'
    else:
        color = colors[index]
        label = f'Cluster {cluster_id}'

    points_in_cluster = reduced_embeddings[cluster_ids == cluster_id]
    plt.scatter(points_in_cluster[:, 0], points_in_cluster[:, 1], c=[color], label=label)

plt.legend()
plt.title('2D Visualization of Clusters')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.show()
