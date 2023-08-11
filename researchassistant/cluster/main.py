import csv
import json
from researchassistant.helpers.files import create_project_dir
from researchassistant.helpers.urls import get_url_entries, url_to_filename


def cluster(context):
    print("Clustering...")
    print(context)
    create_project_dir(context)
    urls = get_url_entries(context)

    exported_json = []
    # for each url in url, call url_to_filename
    for url in urls:
        
        filename = url_to_filename(url["document"])
        csv_path = context["project_dir"] + "/" + filename + "/" + "facts.csv"
        body_text = context["project_dir"] + "/" + filename + "/" + "body.txt"
        facts = []
        with open(body_text, "r") as f:
            body_text = f.read()
        
        # read facts.csv and convert it to json
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                facts.append(row)

        if url.get("embedding", None) is not None:
            # remove embedding from url
            del url["embedding"]

        exported_json.append(
            {
                "url": url,
                "facts": facts,
                "body_text": body_text
            }
        )
    # save to json file
    with open(context["project_dir"] + "/exported.json", "w") as f:
        json.dump(exported_json, f)

    return context