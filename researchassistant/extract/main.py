import asyncio
import csv
import json
import os
from agentmemory import create_memory, get_memories, update_memory
from dotenv import load_dotenv
from researchassistant.extract.validation import validate_claim

from researchassistant.shared.files import ensure_dir_exists
from researchassistant.shared.urls import (
    get_url_entries,
    update_url_entry,
    url_to_filename,
)

from researchassistant.extract.prompts import (
    summarization_prompt_template,
    summarization_function,
    claim_extraction_prompt_template,
    claim_extraction_function,
)

load_dotenv()

from easycompletion import (
    openai_function_call,
    compose_prompt,
    chunk_prompt,
    trim_prompt,
)

from agentbrowser import async_init_browser

PARAGRAPH_LENGTH = 400


def split_and_combine(text):
    # Normalize double newlines to single newlines
    text = text.replace("\n\n", "\n")

    # Split the text into paragraphs
    paragraphs = text.split("\n")

    # Combine paragraphs into segments of under 800 words
    segments = []
    current_segment = ""
    current_word_count = 0

    for paragraph in paragraphs:
        paragraph_word_count = len(paragraph.split())

        # Check if adding the paragraph would exceed the word limit
        if current_word_count + paragraph_word_count < PARAGRAPH_LENGTH:
            current_segment += paragraph + "\n"
            current_word_count += paragraph_word_count
        else:
            # Start a new segment if the limit would be exceeded
            segments.append(current_segment.strip())
            current_segment = paragraph + "\n"
            current_word_count = paragraph_word_count

    # Append the last segment if it's not empty
    if current_segment:
        segments.append(current_segment.strip())

    return segments


def add_claim_to_memory(claim, document_id):
    claim_source = claim["source"]
    claim["document_id"] = document_id
    paragraphs = get_memories("paragraphs", filter_metadata={"document_id": document_id})
    # find the paragraph that contains the claim
    for paragraph in paragraphs:
        if claim_source in paragraph["document"]:
            # TODO: fuzzy match claims are failing
            claim["paragraph_id"] = paragraph["id"]
            break

    # create a claim memory
    create_memory("claims", claim["debate_question"] + " " + claim["claim"], claim)
    return True


def extract(source, text, research_topic):
    document = get_memories("documents", filter_metadata={"source": source})
    document = document[0]
    document_id = document["id"]

    document_metadata = document["metadata"]

    if document_metadata["status"] == "extracted":
        print("WARNING: Already extracted: " + source)
        return

    text_chunks = chunk_prompt(text)

    if document_metadata["status"] != "summarized":
        text_chunks_long = trim_prompt(text, 10000)
        document_summary_and_metadata = summarize_text(text_chunks_long)
        summary = document_summary_and_metadata["summary"]
        relevant = document_summary_and_metadata["relevant"]
        author = document_summary_and_metadata["author"]
        date = document_summary_and_metadata["date"]

        # date contains the year, month, and day as integers
        # if no date but url, we should use algorithm to check url on wayback machine for first if url
        paragraphs = split_and_combine(text)
        # for each paragraph, create a paragraph memory
        for paragraph in paragraphs:
            memories = get_memories("paragraphs", filter_metadata={"document_id": document_id})
            for memory in memories:
                if memory["document"] == paragraph:
                    print("WARNING: Paragraph already exists in memory")
                    continue

            create_memory(
                "paragraphs",
                paragraph,
                {
                    "source": source,
                    "document_id": document_id,
                    "author": author,
                    "date": json.dumps(date),
                },
            )

        summary = trim_prompt(summary, 1024)

        document_metadata["status"] = "summarized"
        document_metadata["summary"] = summary
        document_metadata["relevant"] = relevant
        document_metadata["author"] = author
        document_metadata["date"] = json.dumps(date)

        update_memory("documents", document_id, metadata=document_metadata)

    summary = document_metadata.get("summary", None)
    relevant = document_metadata.get("relevant", None)
    author = document_metadata.get("author", None)
    date = document_metadata.get("date", None)

    # if date is 0,0,0 -- lets try to get the date from the wayback machine

    if author == "None" or author == "none" or author is None:
        author = ""
    for i, text_chunk in enumerate(text_chunks):
        claims = extract_from_chunk(text_chunk, summary, research_topic, author)
        # check that claim[0] has all the values filled in for metadata
        if (len(claims) == 0) or (claims[0] is None):
            print("Warning, no claims extracted from chunk")
            continue
        for k in range(len(claims)):
            claim = claims[k]
            if claim is None:
                continue
            claim_is_valid = validate_claim(claim, text_chunk)
            if claim_is_valid is False:
                print("WARNING: Skipping claim, invalid")
                continue
            add_claim_to_memory(claim, document_id)

    document_metadata["status"] = "extracted"
    update_memory("documents", document_id, metadata=document_metadata)


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
        memories = get_memories("documents", filter_metadata={"source": url["metadata"]["url"]})
        if len(memories) == 0:
            raise Exception("No document found for url " + url["metadata"]["url"])

        document = memories[0]

        update_url_entry(
            url["id"], url["document"], valid=url["metadata"]["valid"], crawled=True
        )

        text = document["metadata"]["text"]
        source = document["metadata"]["source"]

        task = async_extract(source, text, context["research_topic"])

        tasks.append(task)

    await asyncio.gather(*tasks)
    return context

async def async_extract(source, text, research_topic):
    extract(source, text, research_topic)

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

    return response["arguments"]


def extract_from_chunk(text, document_summary, research_topic, author=None):
    dictionary = {
        "research_topic": research_topic,
        "summary": document_summary,
        "text": text,
    }
    if author:
        dictionary["author"] = " The author of this document is " + author
    else:
        dictionary["author"] = ""
    text_prompt = compose_prompt(
        claim_extraction_prompt_template,
        dictionary,
    )

    response = openai_function_call(
        text=text_prompt,
        functions=[claim_extraction_function],
        function_call={"name": "extract_claims"},
    )
    arguments = response["arguments"]

    return arguments["claims"]
