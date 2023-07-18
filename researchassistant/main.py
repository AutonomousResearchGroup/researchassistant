import os
from dotenv import load_dotenv
from pyfiglet import Figlet
from rich.console import Console

from agentloop import start, stop
from agentevents import (
    increment_epoch,
)

from researchassistant.steps import crawl, extract, cluster, visualize, archive

# Suppress warning
os.environ["TOKENIZERS_PARALLELISM"] = "False"

load_dotenv()  # take environment variables from .env.


def print_logo():
    """
    Prints ASCII logo using pyfiglet.
    """

    f = Figlet(font="cybermedium")
    console = Console()
    print("\n")
    console.print(f.renderText("research"), style="yellow")
    console.print(f.renderText("assistant"), style="yellow")

    console.print("Starting...\n", style="BRIGHT_BLACK")


def create_prepare_step(project_data):
    # load the json file at the project path
    def prepare(context):
        context = {"epoch": increment_epoch()}

        # for every key in project data, add it to the context
        for key in project_data:
            context[key] = project_data[key]
        return context

    return prepare


def finish(context, loop_dict):
    stop(loop_dict)
    return context


def main(project_data):
    print_logo()
    prepare = create_prepare_step(project_data)

    loop_dict = start(
        [
            prepare,
            crawl,
            extract,
            # cluster,
            # visualize,
            # archive,
            finish
            ]
    )
    return loop_dict
