import asyncio
import os
from dotenv import load_dotenv
from pyfiglet import Figlet
from rich.console import Console

load_dotenv()  # take environment variables from .env.

from agentloop import start, stop
from agentmemory import increment_epoch

from researchassistant.crawl import crawl
from researchassistant.extract import extract
from researchassistant.cluster import cluster

# Suppress warning
os.environ["TOKENIZERS_PARALLELISM"] = "False"


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

        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        context["event_loop"] = loop

        return context

    return prepare


def finish(context, loop_dict):
    stop(loop_dict)
    return context


def main(project_data):
    print_logo()
    prepare = create_prepare_step(project_data)

    loop_dict = start([prepare, crawl, extract, cluster, finish])
    return loop_dict
