import asyncio
import csv
import os
from dotenv import load_dotenv
from fuzzysearch import find_near_matches
import hashlib
import re
from fuzzywuzzy import fuzz

from researchassistant.helpers.content import get_content_from_file
from researchassistant.helpers.files import ensure_dir_exists
from researchassistant.helpers.topics import format_topics, search_topics
from researchassistant.helpers.urls import (
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


summarization_function = compose_function(
    name="summarize_text",
    description="Summarize the text and decide if the article is relevant to the research topic.",
    properties={
        "summary": {
            "type": "string",
            "description": "Detailed summary of the text, along with an explanation of why the text is or isn't relevant.",
        },
        "relevant": {
            "type": "boolean",
            "description": "Is the text relevant to the research topic?",
        },
    },
    required_properties=["summary", "relevant"],
)

summarization_prompt_template = """
I have the following document
```
{{text}}
```

I am a researcher with the following research topic:
{{research_topic}}

Please summarize the document and determine if the document is relevant to the research topic. In your summary, explain why it is or isn't relevant."
"""

claim_extraction_prompt_template = """\
I am a researcher with the following research topic:
{{research_topic}}

Summary of the full document:
{{summary}}

Current section of the document I am working on:
{{text}}

TASK: Extract claims from the currect section I am working on.

- Include the specific passage of source text that the claim references as the source parameter.
- Please extract the specific and distinct claims from this text, and respond with all factual claims as a JSON array. Avoid duplicate claims.
- Each claim should be one statement. Ignore questions, section headers, fiction, feelings and rhetoric: they are not factual claims.
- DO NOT just of use pronouns or shorthand like 'he' or 'they' in claims. Use the actual complete name of the person or thing you are referring to and be very detailed and specific.
- Claims should include extensive detail so that they can stand alone without the source text. This includes detailed descriptions of who, what and when.
- ALWAYS use the full name and title of people along with any relationship to organizations. For example, instead of 'the president', use 'Current U.S. President Joe Biden'. Do not use nicknames or short names when referring to people. Instead of "Mayor Pete", use "Pete Buttigieg".
- Ignore anything that isn't relevant to the research topic, including political opinions, feelings, and rhetoric. We are only interested in claims that are factual, i.e. can be proven or disproven.
- Please disambiguate and fully describe known entities. For example, instead of 'Kim the Rocketman', use 'North Korean leader Kim Jong Un'. Instead of 'the 2016 election', use 'the 2016 U.S. presidential election'.
- Split claims up into specific statements, even if the source text has combined the claims into a single statement. There can be multiple claims for a source. For example, if a source sentence makes multiple claims, these should be separated

Output should be formatted as an array of claims, which each have the following structure:
[{
    source: string # "The exact source text referenced in the claim",
    claim: string # "The factual claim being made in the source text",
    relevant: boolean # Is the claim relevant to the research topic and summary?
}, {...}]
"""

claim_extraction_function = compose_function(
    name="extract_claims",
    description="Extract all factual claims from the section of text.",
    properties={
        "claims": {
            "type": "array",
            "description": "Array of claims extracted from the current section of the source text",
            "items": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "The exact source text from which the claim has been extracted",
                    },
                    "claim": {
                        "type": "string",
                        "description": "A factual claim made in the source text",
                    },
                    "relevant": {
                        "type": "boolean",
                        "description": "Determine whether this claim is relevant to the research topic. If it is not relevant, set this to False, otherwise set it to True.",
                    },
                },
            },
        }
    },
    required_properties=["claims"],
)


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


def validate_claims(claims):
    # check to make sure that arguments has source, claim, relevant
    # if the keys are missing, return false
    for claim in claims:
        for key in [
            "source",
            "claim",
            "relevant",
        ]:
            if key not in claim:
                print("Missing key", key)
                return False


def validate_claim(claim, document):
    claim_source = claim["source"]
    if claim_source is None or claim_source == "":
        print("Claim is empty")
        return False

    matches = find_near_matches(claim_source, document, max_l_dist=8, max_substitutions=10, max_insertions=10, max_deletions=10)

    if len(matches) == 0:
        print("Claim source not found in document")
        
        sentences = document.split('.')
        for sentence in sentences:
            similarity_ratio = fuzz.token_set_ratio(claim_source, sentence)
            if similarity_ratio >= 90:
                print("Claim source found in document with 90% similarity")
                return True
        
        return False
    else:
        print("Claim source found in document")

    return True



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
