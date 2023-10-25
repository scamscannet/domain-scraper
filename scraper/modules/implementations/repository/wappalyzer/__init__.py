import json
import os

_directory_technologies = os.path.dirname(__file__) + "/technologies"
_directory_categories = os.path.dirname(__file__) + "/categories"
merged_technologies_path = os.path.dirname(__file__) + "/technologies.json"


def prepare_technology_file():
    technologies = {}
    categories = {}
    if os.path.exists(merged_technologies_path):
        os.remove(merged_technologies_path)

    for file in os.listdir(_directory_technologies):
        filename = os.fsdecode(file)
        if filename.endswith(".json"):
            with open(os.path.join(_directory_technologies, filename), "r") as f:
                d = json.loads(f.read())
                technologies = technologies | d

    #with open(os.path.join(_directory_categories, "categories.json"), "r") as f:
    #    d = json.loads(f.read())
    #    categories = categories | d

    with open(merged_technologies_path, "w") as f:
        f.write(json.dumps({
     #       'categories': categories,
            'technologies': technologies
        }))


def get_technologies():
    with open(merged_technologies_path, "r") as f:
        return json.loads(f.read())
