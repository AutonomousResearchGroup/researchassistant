# researchassistant

Research a topic in-depth and make it searchable

# TODO
This is not ready for use yet

<img src="resources/image.jpg">

# Installation

```bash
pip install researchassistant
```

# Usage

## Importing into your project

```python
from researchassistant import research, search, export_archive, import_archive
```

## Research

Your research will be organized under the topic, and tagged with metadata by subtopic. Each document will also get a summary and be added to the search index.

The current types are "topic" and "code". The main difference is that "topic" will focus on news, encyclopedic knowledge, scientific data and research, while "code" will focus on code, documentation, and tutorials.

### Research a topic

```python
research(
    type="topic",
    topic="societal impact of artificial intelligence", # all data is stored under this
    subtopics=["existential risk", "impact of ai on the economy"], # subtopics, will be used for expanding search (Optional)
    description="This is a detailed description of existential risk, blah blah.", # detailed description, will be used for evaluating if things are relevant
    start_urls=["https://gwern.net/math-error"], # list of urls to start from, guaranteed to be included in research (Optional)
    path="data", # path to store data, final path will be <path>/<topic> (Optional)
    use_existing=True, # use existing data on topic fresh or start fresh (Optional)
    include_keywords=["artificial intelligence", "machine learning"], # Include documents which have these keywords in relevancy check (Optional)
    exclude_keywords=["e/acc"] # Exclude documents which have these keywords in relevancy check (Optional)
    )
```

### Research code

```python
research(
    type="code",
    topic="smt solver", # all data is stored under this
    subtopics=["satisfiability modulo theory", "boolean satisfiability problem"], # subtopics, will be used for expanding search (Optional)
    description="In computer science and mathematical logic, satisfiability modulo theories (SMT) is the problem of determining whether a mathematical formula is satisfiable. We are trying to create an IC3 library using PySMT. IC3 is a model checking technique used for formally verifying finite-state systems (like hardware and software designs).", # detailed description, will be used for evaluating if things are relevant
    start_urls=["https://pysmt.org"], # list of urls to start from, guaranteed to be included in research (Optional)
    path="data", # path to store data, final path will be <path>/<topic> (Optional)
    use_existing=True, # use existing data on topic fresh or start fresh (Optional)
    include_keywords=["ic3", "smt", "Satisfiability Modulo Theory", "Incremental Inductive Cube Checker"], # Include documents which have these keywords in relevancy check (Optional)
    exclude_keywords=["Internet Crime Complaint Center", "Digital Literacy Certification", "Surface-mount technology"] # Exclude documents which have these keywords in relevancy check (Optional)
    )
```

## Search

Search requires a topic and search_query. The topic should be the same as the topic you used for calling research. The search_query is the query you want to search for. You can also filter by domains, subtopics and keywords.

## Search topic

```python
search(
    topic="societal impact of artificial intelligence", # same topic as you used in research
    search_query="thermodynamic god", # search query
    contains_text="e/acc", # Only include documents which include one of these strings (Optional)
    domains=["https://www.effectiveacceleration.org/"], # filter by domains (Optional)
    subtopics=["existential risk"], # filter by subtopics (Optional)
    path="data", # path to store data, final path will be <path>/<topic> (Optional)
    )
```

## Export archive

Dumps everything you need to recreate the research into a folder. This is useful for sharing your research with others.

```python
export_archive(
    topic="all", # same topic as you used in research, or all to export all topics (Optional)
    path="data", # path to store data, final path will be <path>/<topic> (Optional)
    output_path="archive", # path to store data, final path will be <path>/<topic> (Optional)
    )
```

```python
import_archive(
    path_to_archive="archive", # path to store data, final path will be <path>/<topic> (Optional)
    replace_existing=False, # replace existing data - destructive! (Optional)
)
```

# Publishing

```bash
bash publish.sh --version=<version> --username=<pypi_username> --password=<pypi_password>
```

# Contributions Welcome

If you like this library and want to contribute in any way, please feel free to submit a PR and I will review it. Please note that the goal here is simplicity and accesibility, using common language and few dependencies.

# Questions, Comments, Concerns

If you have any questions, please feel free to reach out to me on [Twitter](https://twitter.com/spatialweeb) or Discord @new.moon.
