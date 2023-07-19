import os

def ensure_dir_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_project_dir(context):
    project_dir = context.get("project_dir", None)
    if project_dir is None:
        project_dir = "./project_data/" + context["project_name"]
        os.makedirs(project_dir, exist_ok=True)
        context["project_dir"] = project_dir
    return context