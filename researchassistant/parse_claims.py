import json
import os
import sys
import csv
import openai
import PyPDF2
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from tqdm import tqdm
from dotenv import load_dotenv
import tiktoken
import chromadb

# set env var TOKENIZERS_PARALLELISM= to false to avoid a warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

chroma_client = chromadb.Client()

def query_topics(
    query_texts,
    collection_name="topics",
    where=None,
    where_document=None,
    n_results=50,
    include=["documents"],
):
    """
    Search a collection with given query texts.
    """
    collection = chroma_client.get_or_create_collection(collection_name)
    return collection.query(
        query_texts=query_texts,
        where=where,
        where_document=where_document,
        n_results=n_results,
        include=include,
    )

def create_topic(
    text
):
    collection = chroma_client.get_or_create_collection("topics")
    # sanitize and escape text - remove all special characters
    text = re.sub(r"[^a-zA-Z0-9]+", " ", text)

    collection.upsert(
        ids=[text],
        documents=[text],
        metadatas=[{"text": text, "type": "topic"}],
    )


def seed_topics():
    # load topics 
    topics_file = open("topics.csv", "r").read()

    # topic headers are Topic,Subtopic in the first row
    topics = topics_file.split("\n")
    topic_headers = topics[0].split(",")
    topic_rows = topics[1:]

    for topic_row in topic_rows:
        topic_row_values = topic_row.split(",")
        topic = topic_row_values[0]
        subtopics = topic_row_values[1:]
        # print suptopics
        for subtopic in subtopics:
            print('creating document for topic: ' + topic + ', subtopic: ' + subtopic)

            topic_plus_subtopic = topic + ", " + subtopic

            # create the document with the topic as the text and the subtopics as the metadata
            create_topic(
                text=topic_plus_subtopic,
            )

seed_topics()

model = "gpt-3.5-turbo-0613"
encoding = "gpt-3.5-turbo-0613"

# get the text from system_prompt.txt
system_prompt = open("system_prompt.txt", "r").read()
user_prompt = open("user_prompt.txt", "r").read()
summarization_prompt = open("summarization_prompt.txt", "r").read()

# Define the maximum number of tokens
chunk_length = 2000

load_dotenv()  # take environment variables from .env.

print('Parsing ' + sys.argv[1])
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_text_chunk(sentences, chunk_length=chunk_length):
    current_chunk = ""
    text_chunks = []
    for sentence in sentences:
        if get_token_length(current_chunk + sentence + " ") <= chunk_length:
            current_chunk += sentence + " "
        else:
            text_chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:  # If there is any leftover sentence
        text_chunks.append(current_chunk.strip())
    return text_chunks

def get_token_length(string: str) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(tiktoken.encoding_for_model(encoding).encode(string))
    return num_tokens

input_file = sys.argv[1]

if not input_file:
    print("Please provide a URL or a PDF file.")
    sys.exit()

if len(sys.argv) > 3:
    print("Error, couldn't read path. You probably need to add quotes around your input file.")
    sys.exit()

def process_file():
    if input_file.startswith('http'):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        driver = webdriver.Chrome(options=options)

        driver.get(input_file)

        html_content = driver.page_source

        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        driver.quit()
        return text

    else:
        if input_file.endswith('.pdf'):
            with open(input_file, 'rb') as f:
                try:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ''
                    for i in range(len(pdf_reader.pages)):
                        text += pdf_reader.pages[i].extract_text()
                    return text
                except PyPDF2.utils.PdfReadError:
                    print("Failed to read PDF file.")
                    sys.exit()
        elif input_file.endswith('.txt'):
            with open(input_file, 'r') as f:
                text = f.read()
                return text
        else:
            print("Invalid input file format. Please provide a URL or a PDF file.")
            sys.exit()

text = process_file()

# Assemble chunks of text in sentences, with chunk_length characters max each, and each ending in a complete sentence.
sentences = re.split(r'(?<=[.!?])\s+', text)
text_chunks = build_text_chunk(sentences)
current_chunk = ""

output_file = sys.argv[2] if len(sys.argv) > 2 else 'claims.csv'

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    writer.writerow(['Input', 'Source', 'Claim', 'Relevant', 'Topic', 'Subtopic', 'Debate Question'])

    summarization_function = {
        "name": "summarize_text",
        "description": "Summarize the text. Include the topic, subtopics.",
        "parameters": {
            "type": "object",
            "properties": {
                "topics": {
                    "type": "string",
                    "description": "List of major topics, separated by commas. For example, 'Existential Risk, AI Safety, AI Alignment'.",
                },
                "summary": {
                    "type": "string",
                    "description": "Detailed summary of the text.",
                }
            },
            "required": ["topics", "summary"],
        }
    }

    summary = ""
    topics = ""

    # Summarize the text with gpt-3.5-16k
    conversation = [{"role": "system", "content": system_prompt }]
    text_prompt = "```\n" + text_chunks[0] + "```\n" + summarization_prompt
    conversation.append({"role": "user", "content": text_prompt})

    retries = 0
    while retries < 5:
        response = None
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=conversation,
                functions=[summarization_function],
                function_call={ "name": "summarize_text" }
            )
        except Exception as e:
            print('exception: ' + str(e))
            continue
        print('conversation:\n' + str(conversation))
        print('response:\n' + str(response))

        if response is None:
            print("NO RESPONSE FROM API.")
            continue

        message = response.choices[0].message

        if "function_call" not in message:
            print("NO FUNCTION DETECTED IN THE RESULT.")
            continue

        if "arguments" in message["function_call"]:
            arguments = message["function_call"]["arguments"]
            if isinstance(arguments, str):
                arguments = json.loads(arguments)

        if arguments is None:
            print("INVALID SUMMARY RESPONSE.")
            continue

        if "summary" not in arguments or "topics" not in arguments:
            continue

        summary = arguments["summary"]
        topics = arguments["topics"]

        break

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_length:
            current_chunk += sentence + " "
        else:
            text_chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:  # If there is any leftover sentence
        text_chunks.append(current_chunk.strip())

    for i, text_chunk in enumerate(text_chunks):
        print('processing chunk ' + str(i) + ' of ' + str(len(text_chunks)))
        conversation = [{"role": "system", "content": system_prompt }]

        chunk_topics = []
        queried_topics_summary = query_topics(
            query_texts=[summary],
            collection_name="topics",
            n_results=10,
            include=["documents"],
        )

        queried_topics_chunk = query_topics(
            query_texts=[text_chunk],
            collection_name="topics",
            n_results=10,
            include=["documents"],
        )

        # add the topics to the claim_topics list
        for topic in queried_topics_summary["documents"][0]:
            print('appending topic: ' + topic + ' to claim_topics')
            chunk_topics.append(topic)

        for topic in queried_topics_chunk["documents"][0]:
            print('appending topic: ' + topic + ' to claim_topics')
            chunk_topics.append(topic)

        # filter out duplicate topics ith a set
        chunk_topics = list(set(chunk_topics))

        chunk_topics_string = ""
        # join chunk_topics into a string, should be formatted like [topic], [topic] with [] around each topic
        for topic in chunk_topics:
            chunk_topics_string += "[" + topic + "], "
        
        # remove the last comma and space
        chunk_topics_string = chunk_topics_string[:-2]

        text_prompt = "Relevant Topics:\n```\n" + chunk_topics_string + "```\n\nSummary of the document:\n```\n" + summary + "```\n\nCurrent Text Chunk:\n```" + text_chunk + "```\n" + user_prompt

        conversation.append({"role": "user", "content": text_prompt})
        print('conversation:\n' + str(conversation))
        response = None
        retries = 0
        while retries < 5:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    temperature=0.01,
                    messages=conversation
                )
                print("response:")
                print(response)
            except Exception as e:
                print('exception: ' + str(e))
                continue
            break

        def extract_and_parse_json(text):
            # Use a regular expression to find the JSON block
            json_block_match = re.search(r'\[.*\]', text, re.DOTALL)
            
            # If a JSON block is found
            if json_block_match:
                json_block = json_block_match.group(0)
                print('JSON block: ' + json_block)
                
                # Parse the JSON block into a Python list
                python_list = json.loads(json_block)
                
                return python_list
            else:
                return []
        print('response.choices:')
        choice = response.choices[0]
        print('Choice: ' + choice.message.content)
        claims = extract_and_parse_json(choice.message.content)

        # for each value in claim.source and claim.claim, make sure there are no newlines, and the beginning and last character are a double quote (")
        for claim in claims:
            claim['source'] = claim['source'].replace('\n', ' ').strip()
            claim['claim'] = claim['claim'].replace('\n', ' ').strip()
            if claim['source'][0] != '"':
                claim['source'] = '"' + claim['source']
            if claim['source'][-1] != '"':
                claim['source'] = claim['source'] + '"'
            if claim['claim'][0] != '"':
                claim['claim'] = '"' + claim['claim']
            if claim['claim'][-1] != '"':
                claim['claim'] = claim['claim'] + '"'

        claim_metadata_function = {
            "name": "add_claim_metadata",
            "description": "Add claim metadata. From the list of topic:subtopic pairs, choose the most appropriate one. If the claim is not relevant to the goal topics, set 'relevant' to False, if it is relevant set it to True. Also include a debate question which the claim would be most relevant to.",
            "parameters": {
                "type": "object",
                "properties": {
                    "relevant": {
                        "type": "boolean",
                        "description": "Determine whether this claim is relevant to the goal topics. If it is not relevant, set this to False, otherwise set it to True.",
                    },
                    "debate_question": {
                        "type": "string",
                        "description": "A debate question which the claim is relevant to. Ideally the question is one which the claim directly answers or at least in which the claim is foundational to another claim.",
                    },
                    "topic": {
                        "type": "string",
                        "description": "The topic. For example, 'AI Training and Deployment'.",
                    },
                    "subtopic": {
                        "type": "string",
                        "description": "The subtopic. For example, 'New Definitions of Benefits'.",
                    },
                },
                "required": ["relevant", "debate_question", "topic_subtopic"],
            }
        }


        # iterate claims 10 at a time and pass into the claims meta function
        # For batch of parsed claims...
        # - Call function handler
        # - search for most relevant 50 pairs
        # - set relevant / not relevant, along with topic + subtopic if relevant
        # - Run 10 claims at a time parse out to function handler
        
        claim_topics = []

        # iterate through claims 10 at a time
        for j in range(0, len(claims)):
            print('process claim for ' + str(j))
            queried_topics = query_topics(
                query_texts=[summary],
                collection_name="topics",
                n_results=10,
                include=["documents"],
            )

            print('queried topics documents:\n' + str(queried_topics["documents"]))

            # add the topics to the claim_topics list
            for topic in queried_topics["documents"][0]:
                print('appending topic: ' + topic + ' to claim_topics')
                claim_topics.append(topic)

            # filter out duplicate topics ith a set
            claim_topics = list(set(claim_topics))

            metadata_prompt = (
                "Document summary:\n```"
                "" + summary + "```\n\n"
                "Topics (formatted as [Topic:Subtopic]):\n```"
                "" + str(claim_topics) + "```\n\n"
                "Claim: " + claims[j]['claim'] + "\n"
                "Source: " + claims[j]['source'] + "\n\n"
                "Task: Add claim metadata. From the list of topic:subtopic pairs, choose the most appropriate topic + subtopic. If the claim is not relevant to the goal topics, set 'relevant' to False, if it is relevant set it to True."
                "Also include a debate question which the claim would be most relevant to. For example, 'Is AI alignment possible?'."
            )

            print('***** metadata_prompt:')
            print(metadata_prompt)

            conversation = [{"role": "system", "content": system_prompt }]
            conversation.append({"role": "user", "content": metadata_prompt})

            arguments = None
            while retries < 10:
                response = None
                try:
                    response = openai.ChatCompletion.create(
                        model=model,
                        messages=conversation,
                        functions=[claim_metadata_function],
                        function_call={ "name": "add_claim_metadata" }
                    )
                except Exception as e:
                    print('exception: ' + str(e))
                    continue

                if response is None:
                    print("NO RESPONSE FROM API.")
                    continue

                message = response.choices[0].message

                if "function_call" not in message:
                    print("NO FUNCTION DETECTED IN THE RESULT.")
                    continue

                if "arguments" in message["function_call"]:
                    arguments = message["function_call"]["arguments"]
                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)

                if arguments is None:
                    print("INVALID SUMMARY RESPONSE.")
                    continue

                if "relevant" not in arguments or "debate_question" not in arguments or "topic" not in arguments or "subtopic" not in arguments:
                    print("INVALID SUMMARY RESPONSE.")
                    print(message)
                    continue

                break
            print('writing row')
            print('arguments: ' + str(arguments))
            # parse response
            claims[j]['relevant'] = arguments['relevant']
            claims[j]['debate_question'] = arguments['debate_question']
            claims[j]['topic'] = arguments['topic']
            claims[j]['subtopic'] = arguments['subtopic']
            claim = claims[j]
            writer.writerow([input_file, claim['source'], claim['claim'], claim['relevant'], claim['topic'], claim['subtopic'], claim['debate_question']])
            print('wrote row for claim: ' + str(claim))