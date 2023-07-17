import os
from agentmemory import create_memory, wipe_category

def archive(context):
    return context

def import_archive(
    path_to_archive=None,
    replace_existing=False
    ):
    if path_to_archive is None:
        raise ValueError("Please provide a path to the archive you want to import.")
    if not os.path.exists(path_to_archive):
        raise ValueError("The path you provided does not exist.")
    
    # TODO ...


def export_archive(
    topic="all",
    path="data",
    output_path="archive.json"
):
    if topic == "all":
        # TODO ...
        pass
    else:
        # TODO ...
        pass