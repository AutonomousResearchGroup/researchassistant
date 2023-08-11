# researchassistant

Research a topic in-depth and make it searchable

<img src="resources/image.jpg">

# Usage

### CLI:

```sh
python3 start.py
```

### Testing:

```sh
python -m pip install pytest
python -m pytest test.py
```

# Modules

## Crawl

Pull data from various sources, determine if its relevant, crawl the links from those sources and build up the source data set.

- Current this supports accepting a list of URLs and crawling them for links.
- In the future, will accept a folder of items, link to a Google Drive folder, links to social profiles etc.

## Extract

Extract summary, facts and metadata from the source data set.

- Extracts facts in batches from the text with GPT-3.5 -- verifies that they aren't hallucinations and prepares context for clustering.

## Cluster

Relate the extracted data to each other and cluster them into topics.

- Using DBScan to cluster the data into topics.
- Topics are derived from the clusters.

## Shared

Various code that is shared across the steps of the research process.

# API Documentation

Coming soon... for now, please see the code.

# Contributions Welcome

If you like this library and want to contribute in any way, please feel free to submit a PR and I will review it. Please note that the goal here is simplicity and accesibility, using common language and few dependencies.

# Questions, Comments, Concerns

If you have any questions, please feel free to reach out to me on [Twitter](https://twitter.com/spatialweeb) or Discord @new.moon.
