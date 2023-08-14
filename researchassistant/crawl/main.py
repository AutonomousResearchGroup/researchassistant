import asyncio
import json
from urllib.parse import urljoin
from traceback import format_exc

from agentmemory import create_memory, get_memories, search_memory
from agentbrowser import (
    async_navigate_to,
    async_get_body_text,
    async_get_body_html,
    async_create_page,
    async_get_document_html,
)

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
)

# Global set for deduplication
crawled_links = set()


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

    # convert links to a list
    links = list(links)

    metadata = {
            "title": title,
            "document_html": html,
            "body_html": body_html,
            "text": body_text,
            "source": url,
            "links": json.dumps(links),
            "status": "crawled",
        }
    
    memories = get_memories(context["project_name"] + "_documents", contains_text=body_text.strip())
    if(len(memories) > 0):
        print("Skipping url:", url)
        print("Document already exists. Text is the same.")
        return
    memories = get_memories(context["project_name"] + "_documents", filter_metadata={"source": url})
    # sanity check that same url doesnt already exist
    if(len(memories) > 0):
        print("Skipping url:", url)
        print("Document already exists. Url is the same.")
        return
    
    # then sanity check that same text doesnt already exist
    memories = search_memory(context["project_name"] + "_documents", max_distance=0.05)
    if(len(memories) > 0):
        related_document_id = memories[0]["id"]
        metadata["related_to"] = related_document_id

        # TODO: related_to should be determined by which one is older
    
    create_memory(
        context["project_name"] + "_documents",
        body_text,
        metadata,
    )

    add_url_entry(url, title, context, backlink=backlink, valid=True, crawled=True)

    valid_links = []

    for link in links:
        # skip common hrefs that don't lead anywhere
        if link["url"] in ["#", "", "/"]:
            continue

        link["url"] = urljoin(url, link["url"])
        valid_links.append(link)
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
