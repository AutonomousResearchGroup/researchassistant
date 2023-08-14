import os
import numpy as np
from dotenv import load_dotenv
import psycopg2
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load Environment Variables
load_dotenv()
POSTGRES_CONNECTION_STRING = os.getenv("POSTGRES_CONNECTION_STRING")


# Connect to PostgreSQL
def connect_to_postgres():
    return psycopg2.connect(POSTGRES_CONNECTION_STRING)


# Preprocess Embeddings
def preprocess_embeddings(table_name="memory_claims"):
    conn = connect_to_postgres()
    cursor = conn.cursor()

    # Check if there is an embedding_reduced column, if not create it
    cursor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS embedding_geom geometry;"
    )

    # Perform PCA on the embeddings, start by fetching a manageable sample set
    cursor.execute(
        f"SELECT embedding FROM {table_name} LIMIT GREATEST(10000, (SELECT COUNT(*) FROM {table_name}) / 100);"
    )
    sample_data = np.array(cursor.fetchall())

    n_components = 3  # , depending on what you want
    pca = PCA(n_components=n_components)
    sample_data = np.array([np.array(eval(embedding[0])) for embedding in sample_data])
    pca.fit(sample_data)

    # Apply PCA transformation to all embeddings in the DB and convert to geometries
    cursor.execute(f"SELECT embedding FROM {table_name};")
    embeddings = np.array(cursor.fetchall())
    embeddings = np.array([np.array(eval(embedding[0])) for embedding in embeddings])
    reduced_embeddings = pca.transform(embeddings)

    for i, reduced_embedding in enumerate(reduced_embeddings):
        geom = f"ST_MakePoint({reduced_embedding[0]}, {reduced_embedding[1]}, {reduced_embedding[2]})"
        cursor.execute(
            f"UPDATE {table_name} SET embedding_geom = {geom} WHERE id = %s;", (i + 1,)
        )

    conn.commit()
    cursor.close()
    conn.close()


# Perform Iterative DBSCAN to Determine Epsilon
def iterative_dbscan(table_name="memory_claims"):
    conn = connect_to_postgres()
    cursor = conn.cursor()

    # Fetch sample set (1% of the data or 10000 entries, whichever is more)
    cursor.execute(
        f"SELECT embedding FROM {table_name} LIMIT GREATEST(10000, (SELECT COUNT(*) FROM {table_name}) / 100);"
    )
    sample_data = np.array(cursor.fetchall())

    # [['[-0.0007989494,-0.026478143,-0.028776204,-0.05423241,0.027223293,-0.15137266,0.03247689,-0.055290326,-0.04948784,-0.05838017]']]
    # embeddings are returned as strings, but are actually lists of floats, so we need to convert them
    # filter out any where the embedding is None
    sample_data = [embedding for embedding in sample_data if embedding[0] is not None]
    sample_data = np.array([np.array(eval(embedding[0])) for embedding in sample_data])

    # Perform k-means to find initial epsilon
    kmeans = KMeans(n_clusters=10).fit(sample_data)
    _, dists = pairwise_distances_argmin_min(sample_data, kmeans.cluster_centers_)
    epsilon = np.mean(dists)

    # Iterative DBSCAN
    tolerance = 0.05
    target_cluster_ratio = 0.9
    max_iterations = 10
    for iteration in range(max_iterations):
        dbscan = DBSCAN(eps=epsilon).fit(sample_data)
        labels = dbscan.labels_
        clustered_ratio = np.sum(labels != -1) / len(labels)

        if abs(clustered_ratio - target_cluster_ratio) <= tolerance:
            break

        # Adjust epsilon
        if clustered_ratio < target_cluster_ratio:
            epsilon *= 0.9
        else:
            epsilon *= 1.1

    cursor.close()
    conn.close()

    return epsilon


def pgvector_dbscan(
    epsilon, min_points=2, table_name="memory_claims", column_name="embedding"
):
    conn = connect_to_postgres()
    cursor = conn.cursor()

    epsilon = epsilon * 2

    cursor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS cluster integer;"
    )

    cursor.execute(f"UPDATE {table_name} SET cluster = NULL;")

    clustering_query = f"""
    WITH RECURSIVE clusters AS (
        SELECT 
            id,
            {column_name},
            1 AS cluster
        FROM {table_name}
        WHERE id = (SELECT id FROM {table_name} LIMIT 1)

        UNION ALL

        SELECT 
            v.id,
            v.{column_name},
            c.cluster
        FROM {table_name} v
        JOIN clusters c
        ON v.id <> c.id AND v.{column_name} <-> c.{column_name} < {epsilon}
        WHERE v.cluster IS NULL
    )
    UPDATE {table_name}
    SET cluster = clusters.cluster
    FROM clusters
    WHERE {table_name}.id = clusters.id;
    """

    cursor.execute(clustering_query)
    conn.commit()

    cursor.execute(
        f"SELECT cluster FROM {table_name} GROUP BY cluster HAVING COUNT(id) < {min_points};"
    )
    invalid_clusters = [row[0] for row in cursor.fetchall()]

    if invalid_clusters:
        cursor.execute(
            f"UPDATE {table_name} SET cluster = NULL WHERE cluster::integer IN ({','.join(map(str, invalid_clusters))});"
        )

    cursor.execute(
        f"SELECT cluster, ARRAY_AGG({column_name}) FROM {table_name} WHERE cluster IS NOT NULL GROUP BY cluster;"
    )
    clusters = cursor.fetchall()

    cursor.close()
    conn.close()

    return clusters


def plot_clusters(clusters):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    for cluster_id, embeddings in clusters:
        if cluster_id is None:
            continue

        xs, ys, zs = zip(*[embedding[:3] for embedding in embeddings])

        ax.scatter(xs, ys, zs, label=f"Cluster {cluster_id}")

    ax.legend()
    ax.set_xlabel("Dimension 1")
    ax.set_ylabel("Dimension 2")
    ax.set_zlabel("Dimension 3")
    plt.title("DBSCAN Clustering Results")
    plt.show()


# Main Function
def main():
    table_name = "memory_claims"  # Default table name
    preprocess_embeddings(table_name)
    epsilon = iterative_dbscan(table_name)
    clusters = pgvector_dbscan(epsilon, table_name=table_name)
    print(clusters)
    print("Clustering completed successfully!")
    plot_clusters(clusters)


if __name__ == "__main__":
    main()
