from agentmemory import cluster

def main(context):
    print("Clustering...")
    print('Clustering claims')
    project_name = context['project_name']
    cluster(category=project_name+"_claims", epsilon=1.0, min_samples=3)
    print('Clustering paragraphs')
    cluster(category=project_name+"_paragraphs", epsilon=1.0, min_samples=3)
    print('Clustering sentences')
    cluster(category=project_name+"_documents", epsilon=1.0, min_samples=3)
    return context