from agentmemory import cluster

def main(context):
    print("Clustering...")
    cluster(category="facts", epsilon=0.2, min_samples=4)
    cluster(category="paragraphs", epsilon=0.2, min_samples=4)
    cluster(category="documents", epsilon=0.2, min_samples=4)

    return context