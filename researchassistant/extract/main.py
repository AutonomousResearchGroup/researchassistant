import asyncio
import csv
import os
from agentmemory import create_memory, get_memories
from dotenv import load_dotenv
from researchassistant.extract.validation import validate_claim

from researchassistant.shared.content import get_content_from_file
from researchassistant.shared.files import ensure_dir_exists
from researchassistant.shared.topics import format_topics, search_topics
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

from dotenv import load_dotenv

load_dotenv()


async def extract_from_file_or_url(
    input_file_or_url, output_file, research_topic
):
    text = await get_content_from_file(input_file_or_url)
    return extract(input_file_or_url, text, output_file, research_topic)


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
        if current_word_count + paragraph_word_count < 800:
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
    paragraphs = get_memories("paragraph", {"document_id": document_id})
    # find the paragraph that contains the claim
    for paragraph in paragraphs:
        if claim_source in paragraph["text"]:
            claim["paragraph_id"] = paragraph["id"]
            break

    # create a claim memory
    create_memory("claim", claim["debate_question"] + " " + claim["claim"], claim)
    return True


def extract(source, text, output_file, research_topic):
    document_id = create_memory("document", text, {"source": source})

    text_chunks = chunk_prompt(text)

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
        create_memory(
            "paragraph", paragraph, {"source": source, "document_id": document_id, "author": author, "date": date}
        )

    summary = trim_prompt(summary, 1024)

    topics = format_topics(search_topics(summary))

    # convert output_file to absolute path
    output_file = os.path.abspath(output_file)
    with open(output_file, "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "Input",
                "Source",
                "Claim",
                "Relevant",
                "Author",
                "Debate Question",
            ]
        )

    ensure_dir_exists(output_file)
    if author == "None" or author == "none":
        author = ""
    for i, text_chunk in enumerate(text_chunks):
        print("Extracting from chunk", i, "of", len(text_chunks))
        print(text_chunk)
        claims = extract_from_chunk(text_chunk, summary, research_topic, topics, author)
        # check that claim[0] has all the values filled in for metadata
        if (len(claims) == 0) or (claims[0] is None):
            print("Warning, no claims extracted from chunk")
            continue
        for k in range(len(claims)):
            claim = claims[k]
            if claim is None:
                continue
            print("Validating claim", k, "of", len(claims))
            claim_is_valid = validate_claim(claim, text_chunk)
            if claim_is_valid is False:
                print('WARNING: Skipping claim, invalid')
                continue
            add_claim_to_memory(claim, document_id)
            print("Writing to file", output_file)
            writer.writerow(
                [
                    source,
                    claim["source"],
                    claim["claim"],
                    claim["relevant"],
                    claim["author"],
                    claim["debate_question"],
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

    return response["arguments"]


def extract_from_chunk(text, document_summary, research_topic, topics, author=None):
    dictionary = {
            "research_topic": research_topic,
            "summary": document_summary,
            "topics": topics,
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
