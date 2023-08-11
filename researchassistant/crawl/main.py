import asyncio
import os
from urllib.parse import urljoin
from traceback import format_exc
from researchassistant.shared.documents import split_document
from agentbrowser import (
    async_navigate_to,
    async_get_body_text,
    async_get_body_html,
    async_create_page,
    async_get_document_html,
)

import json
from bs4 import BeautifulSoup

from researchassistant.shared.constants import (
    skip_media_types,
    default_media_domains,
    default_link_blacklist,
    default_element_blacklist,
)
from researchassistant.shared.html import extract_links, extract_page_title
from researchassistant.shared.urls import (
    add_url_entry,
    url_has_been_crawled,
    url_to_filename,
)

# Global set for deduplication
crawled_links = set()


def cache_page(url, context, title, body_text, html, body_html, links):
    clean_url = url_to_filename(url)
    # check that cache folder exists
    project_dir = context.get("project_dir", None)
    if project_dir is None:
        project_dir = "./project_data/" + context["project_name"]
        os.makedirs(project_dir, exist_ok=True)
        context["project_dir"] = project_dir

    page_dir = project_dir + "/" + clean_url
    # save the html to raw.html
    os.makedirs(page_dir, exist_ok=True)

    # write title, body_text to body.txt
    with open(page_dir + "/body.txt", "w") as f:
        print("Writing body text to file.")
        f.write(body_text)

    body_text_sentences = split_document(body_text)

    with open(page_dir + "/body_sentences.txt", "w") as f:
        print("Writing body text sentences to file.")
        f.write("\n".join(body_text_sentences))

    # new new csv file called meta.csv
    # url, title, meta, linked_from
    with open(page_dir + "/meta.csv", "w") as f:
        f.write("url,title,meta,linked_from\n")
        f.write(url + "," + title)

    # save links to links.csv
    with open(page_dir + "/links.csv", "w") as f:
        f.write("name,url\n")
        for link in links:
            if isinstance(link, str):
                link = json.loads(link)
            f.write(link["name"] + "," + link["url"] + "\n")

    # save html to raw.html
    with open(page_dir + "/document.html", "w") as f:
        f.write(html)

    with open(page_dir + "/body.html", "w") as f:
        f.write(body_html)

    return


async def crawl(url, context, backlink=None, depth=0, maximum_depth=3):
    # if we have reached maximum depth, skip
    if depth > maximum_depth:
        return

    if url_has_been_crawled(url, context):
        print("Url has already been crawled.")
        return

    # skip_media_types is a list of file extensions to skip
    # if the url ends with any of the file extensions, skip it
    if any([url.endswith("." + ext) for ext in skip_media_types]):
        print("Skipping url:", url)
        context = add_url_entry(
            url, url, context, valid=True, type="media", crawled=False
        )
        return

    # if the url includes youtube.com in the domain, return
    if any([media_url in url for media_url in default_media_domains]):
        print("Skipping media domain:", url)
        context = add_url_entry(
            url, url, context, valid=True, type="media_url", crawled=False
        )
        return

    page = await async_create_page(url)

    page = await async_navigate_to(url, page)

    # check if the body contains any of the keywords
    # if it doesn't return
    body_html = await async_get_body_html(page)

    html = await async_get_document_html(page)

    body_text = await async_get_body_text(page)

    title = extract_page_title(html)

    if title is None:
        # throw error until we see some edge cases
        # raise Exception("Title is none, skipping url.")
        print("Warning! Title is none, using body text instead.")
        title = body_text[:10]

    # if none of the keywords are contained
    if not any([keyword in body_text for keyword in context["keywords"]]):
        print("Skipping url:", url)
        print("No keywords found in body text.")
        # add the url to the memory
        add_url_entry(url, title, context, valid=False, crawled=True)
        return

    links = extract_links(body_html)

    cache_page(url, context, title, body_text, html, body_html, links)
    print('Adding URL to memory: "' + url + '"')
    add_url_entry(url, title, context, backlink=backlink, valid=True, crawled=True)

    valid_links = []

    for link in links:
        # skip common hrefs that don't lead anywhere
        if link["url"] in ["#", "", "/"]:
            continue

        link["url"] = urljoin(url, link["url"])
        valid_links.append(link)
        print("link is")
        print(link)
        print("Crawling link:", link["name"])
    print("crawling ", valid_links)
    context = await crawl_all_urls(valid_links, context, backlink)
    return context


async def crawl_all_urls(urls, context, backlink=None):
    # Create a coroutine for each url to crawl
    tasks = [crawl(url, context, backlink) for url in urls]

    # Now we run each coroutine
    for task in asyncio.as_completed(tasks):
        try:
            result = await task
        except Exception as e:
            print(f"Exception occurred: {e}")
            print(f"Traceback: {format_exc()}")


def main(context):
    context["skip_media_types"]: skip_media_types
    context["media_domains"]: default_media_domains
    context["link_blacklist"]: default_link_blacklist
    context["element_blacklist"]: default_element_blacklist

    urls = context["urls"]
    if not isinstance(urls, list):
        urls = urls.replace(",", "\n").split("\n")
        urls = [url.strip() for url in urls]

    # context = validate_crawl(context)
    print("Starting crawl...")

    loop = context["event_loop"]

    loop.run_until_complete(crawl_all_urls(urls, context))
    print("Crawled")
    return context
