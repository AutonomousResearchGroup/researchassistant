import asyncio
import csv
import os
from dotenv import load_dotenv
from fuzzysearch import find_near_matches
from fuzzywuzzy import fuzz
from collections import Counter

from researchassistant.shared.content import get_content_from_file
from researchassistant.shared.files import ensure_dir_exists
from researchassistant.shared.topics import format_topics, search_topics
from researchassistant.shared.urls import (
    get_url_entries,
    update_url_entry,
    url_to_filename,
)

load_dotenv()

from easycompletion import (
    openai_function_call,
    compose_prompt,
    compose_function,
    chunk_prompt,
    trim_prompt,
)

from agentbrowser import async_init_browser

from dotenv import load_dotenv

load_dotenv()


async def extract_from_file_or_url(
    input_file_or_url, output_file, research_topic, summary=None
):
    text = await get_content_from_file(input_file_or_url)
    return extract(input_file_or_url, text, output_file, research_topic, summary)


def extract(source, text, output_file, research_topic, summary=None):
    text_chunks = chunk_prompt(text)

    if summary is None:
        text_chunks_long = trim_prompt(text, 10000)
        summary = summarize_text(text_chunks_long)
        summary = trim_prompt(summary, 1024)

    topics = format_topics(search_topics(summary))

    # convert output_file to absolute path
    output_file = os.path.abspath(output_file)
    print("output file is", output_file)
    with open(output_file, "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "Input",
                "Source",
                "Claim",
                "Relevant",
                "In Source Text",
            ]
        )

    ensure_dir_exists(output_file)
    for i, text_chunk in enumerate(text_chunks):
        print("Extracting from chunk", i, "of", len(text_chunks))
        print(text_chunk)
        claims = extract_from_chunk(text_chunk, summary, research_topic, topics)
        for k in range(len(claims)):
            claim = claims[k]
            if claim is None:
                continue
            print("Validating claim", k, "of", len(claims))
            claim_is_valid = validate_claim(claim, text_chunk)
            print("Writing to file", output_file)
            writer.writerow(
                [
                    source,
                    claim["source"],
                    claim["claim"],
                    claim["relevant"],
                    claim_is_valid,
                ]
            )


async def async_main(context):
    await async_init_browser()
    urls = get_url_entries(context, valid=True, crawled=True)
    project_dir = context.get("project_dir", None)
    if project_dir is None:
        project_dir = "./project_data/" + context["project_name"]
        os.makedirs(project_dir, exist_ok=True)
        context["project_dir"] = project_dir

    tasks = []
    for url in urls:
        clean_url = url_to_filename(url["document"])
        update_url_entry(
            url["id"], url["document"], valid=url["metadata"]["valid"], crawled=True
        )

        # check if body exists
        path = project_dir + "/" + clean_url + "/" + "body.txt"
        if not os.path.exists(path):
            path = url["document"]

        filepath = project_dir + "/" + clean_url + "/" + "facts.csv"

        # if filepath already exists, throw a warning
        if os.path.exists(filepath):
            print("Warning! File already exists:", filepath)
            continue

        task = extract_from_file_or_url(
            path,
            filepath,
            context["research_topic"],
            context.get("summary", None),
        )
        tasks.append(task)
    await asyncio.gather(*tasks)
    return context


def main(context):
    loop = context["event_loop"]
    context = loop.run_until_complete(async_main(context))
    return context


def summarize_text(text):
    summarization_prompt = compose_prompt(
        summarization_prompt_template,
        {
            "text": text,
        },
    )

    response = openai_function_call(
        text=summarization_prompt,
        functions=[summarization_function],
        function_call="summarize_text",
    )

    return response["arguments"]["summary"]


def extract_from_chunk(text, document_summary, research_topic, topics):
    text_prompt = compose_prompt(
        claim_extraction_prompt_template,
        {
            "research_topic": research_topic,
            "summary": document_summary,
            "topics": topics,
            "text": text,
        },
    )

    response = openai_function_call(
        text=text_prompt,
        functions=[claim_extraction_function],
        function_call={"name": "extract_claims"},
    )
    arguments = response["arguments"]

    return arguments["claims"]
