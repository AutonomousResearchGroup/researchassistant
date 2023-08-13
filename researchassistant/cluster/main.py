from agentmemory import cluster, export_memory_to_json, get_memories
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def main(context):
    print("Clustering...")
    print('Clustering claims')
    cluster(category="claims", epsilon=0.8, min_samples=2)
    print('Clustering paragraphs')
    cluster(category="paragraphs", epsilon=0.8, min_samples=2)
    print('Clustering sentences')
    cluster(category="documents", epsilon=0.8, min_samples=2)

    data = get_memories(category="claims", include_embeddings=True)
    print("CLAIMS")
    print(data)
    
    # perform PCA on claims and store the PCA vector as JSON in metadata
    # goal is to reduce to 2D for visualization
    # Step 1: Extract Embeddings and Cluster IDs
    embeddings = np.array([entry['embedding'] for entry in data])
    cluster_ids = np.array([entry['metadata']['cluster'] for entry in data])

    # Step 2: Perform PCA
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embeddings)

    # Step 3: Plot the Clusters
    plt.figure(figsize=(10, 8))
    colors = plt.cm.Spectral(np.linspace(0, 1, len(set(cluster_ids))))

    for cluster_id in set(cluster_ids):
        if cluster_id == -1:
            # Noise points in DBSCAN are assigned a cluster ID of -1
            color = 'k'
            label = 'Noise'
        else:
            color = colors[cluster_id]
            label = f'Cluster {cluster_id}'
        
        points_in_cluster = reduced_embeddings[cluster_ids == cluster_id]
        plt.scatter(points_in_cluster[:, 0], points_in_cluster[:, 1], c=[color], label=label)

    plt.legend()
    plt.title('2D Visualization of Clusters')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.show()


    return context