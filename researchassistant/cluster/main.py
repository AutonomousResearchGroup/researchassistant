from agentmemory import cluster

def main(context):
    print("Clustering...")
    print('Clustering claims')
    cluster(category="claims", epsilon=0.8, min_samples=2)
    print('Clustering paragraphs')
    cluster(category="paragraphs", epsilon=0.8, min_samples=2)
    print('Clustering sentences')
    cluster(category="documents", epsilon=0.8, min_samples=2)
    return context