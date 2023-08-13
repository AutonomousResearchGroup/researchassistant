from agentmemory import cluster

def main(context):
    print("Clustering...")
    print('Clustering claims')
    cluster(category="claims", epsilon=1.0, min_samples=3)
    print('Clustering paragraphs')
    cluster(category="paragraphs", epsilon=1.0, min_samples=3)
    print('Clustering sentences')
    cluster(category="documents", epsilon=1.0, min_samples=3)
    return context