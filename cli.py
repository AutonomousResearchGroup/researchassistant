import os
import json
import sys
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit import PromptSession
from termcolor import colored

style = Style.from_dict(
    {
        "dialog": "bg:#88ff88",
        "button": "bg:#884444 #ffffff",
        "dialog.body": "bg:#ccffcc",
        "dialog shadow": "bg:#000088",
    }
)

# Define the key bindings
kb = KeyBindings()


@kb.add(Keys.ControlS)
def _(event):
    "By pressing `Control-D`, finish the input."
    event.app.exit()


# Create a multiline prompt session
session = PromptSession(key_bindings=kb, multiline=True)


def get_input_from_prompt(question, default_text):
    print("##########################################################################")
    print(colored("Press ", "white"), end="")
    print(colored("'Ctrl-S'", "yellow"), end="")
    print(colored(" to finish editing and continue to the next question.\n", "white"))
    print(colored(question, "green"))

    return session.prompt(default=default_text)


def get_project_details(project_data=None, is_editing=False):
    questions = [
        {"key": "project_name", "question": "What is the name of the project?"},
        {"key": "research_topic", "question": "What are you researching?"},
        {
            "key": "expected_output",
            "question": "What are you hoping to get as an output?",
        },
        {
            "key": "unwanted_content",
            "question": "Is there any content you don't want, or are not interested in?",
        },
        {
            "key": "keywords",
            "question": "Please type in any important keywords or search terms. You can separate them with a ',' comma.",
        },
        {"key": "urls", "question": "Please add any URLs you want to start from."},
        {
            "key": "domains",
            "question": "Any domains you want to specifically search in detail? For example: medium.com, lesswrong.com",
        },
    ]

    project_data = project_data or {}

    for item in questions:
        if is_editing and item["key"] == "project_name":
            continue

        default_answer = project_data.get(item["key"], "")
        answer = (
            get_input_from_prompt(item["question"], default_answer)
            if default_answer
            else input(f'{item["question"]}: ')
        )
        project_data[item["key"]] = answer if answer else default_answer

    return project_data


def save_project_data(name, project_data):
    ensure_project_data_folder()
    with open(f"./project_data/{name}.json", "w") as f:
        json.dump(project_data, f)


def run(project_data):
    print(project_data)
    sys.exit(0)


def ensure_project_data_folder():
    os.makedirs("./project_data", exist_ok=True)


def get_existing_projects():
    ensure_project_data_folder()
    return [f[:-5] for f in os.listdir("./project_data") if f.endswith(".json")]


def choose_project():
    return button_dialog(
        title="Project name",
        text="Choose a project:",
        buttons=[(name, name) for name in get_existing_projects()] + [("Back", "Back")],
        style=style,
    ).run()


def new_or_edit_project(is_editing=False):
    if is_editing:
        project_name = choose_project()
        if project_name == "Back":
            return
        with open(f"./project_data/{project_name}.json") as f:
            project_data = json.load(f)
    else:
        project_data = get_project_details()

    project_data = get_project_details(project_data, is_editing=is_editing)
    save_project_data(project_data["project_name"], project_data)
    print("Project saved.")

    action = button_dialog(
        title="Run project?",
        text="Do you want to run this project now?",
        buttons=[
            ("Yes", "Yes"),
            ("No", "No"),
        ],
        style=style,
    ).run()

    if action == "Yes":
        run(project_data)


def main():
    while True:
        action = button_dialog(
            title="autoresearcher",
            text="Choose an action:",
            buttons=[
                ("New", "New"),
                ("Edit", "Edit"),
                ("Run", "Run"),
                ("Quit", "Quit"),
            ],
            style=style,
        ).run()

        if action == "Quit":
            break
        elif action == "New":
            new_or_edit_project(is_editing=False)
        elif action == "Edit":
            new_or_edit_project(is_editing=True)
        elif action == "Run":
            project_name = choose_project()
            if project_name == "Back":
                continue
            with open(f"./project_data/{project_name}.json") as f:
                project_data = json.load(f)
            run(project_data)


if __name__ == "__main__":
    main()
