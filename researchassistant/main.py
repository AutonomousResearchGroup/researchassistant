import os
from dotenv import load_dotenv
from pyfiglet import Figlet
from rich.console import Console

from agentaction import import_actions
from agentloop import start
from agentevents import (
    increment_epoch,
)

from researchassistant.steps import reason
from researchassistant.steps import act

from researchassistant.helpers.context import (
    backup_project,
    collect_files,
    get_file_count,
    read_and_format_code,
    run_main,
    run_tests,
    validate_files,
)

# Suppress warning
os.environ["TOKENIZERS_PARALLELISM"] = "False"

load_dotenv()  # take environment variables from .env.


def print_logo():
    """
    Prints ASCII logo using pyfiglet.
    """

    f = Figlet(font="slant")
    console = Console()
    print("\n")
    console.print(f.renderText("researchassistant"), style="yellow")
    console.print("Starting...\n", style="BRIGHT_BLACK")


def create_initialization_step(project_data):
    # load the json file at the project path
    def initialize(context):
        context = {
            "epoch": increment_epoch()
        }
        context = get_file_count(context)

        # New path
        if context["file_count"] == 0:
            return context

        context = backup_project(context)
        context = collect_files(context)
        context = validate_files(context)
        context = run_tests(context)
        context = run_main(context)
        context = read_and_format_code(context)

        # for every key in project data, add it to the context
        for key in project_data:
            context[key] = project_data[key]
        return context
    return initialize


def main(project_data):
    print_logo()
    import_actions("./researchassistant/actions")
    initialize = create_initialization_step(project_data)

    loop_dict = start(
        [
            initialize,
            reason,
            act,
        ]
    )
    return loop_dict
