import asyncio
import aiohttp

from agentbrowser import (
    async_navigate_to,
    async_get_body_text,
    async_get_body_html,
    async_get_document_html
)

import json
from bs4 import BeautifulSoup

from agentmemory import (
    create_memory,
    get_memories,
    update_memory,
)

from researchassistant.helpers.constants import (
    skip_media_types,
    default_media_domains,
    default_link_blacklist,
    default_element_blacklist,
)

# Global set for deduplication
crawled_links = set()


def add_url_entry(
    url, text, valid=True, crawled=True, type="url", category="scraped_urls"
):
    create_memory(
        category,
        url,
        {"text": text, "url": url, "type": type, "valid": valid, "crawled": crawled},
    )


def get_entry_from_url(url):
    memory = get_memories("scraped_urls", filter_metadata={"url": url})
    memory = memory[0] if len(memory) > 0 else None
    return memory


def url_entry_exists(url):
    memory = get_entry_from_url(url)
    return memory is not None


def update_url_entry(
    url, text, valid=True, crawled=True, type="url", category="scraped_urls"
):
    update_memory(
        category, url, {"text": text, "valid": valid, "crawled": crawled, "type": type}
    )


def extract_page_title(html):
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.title
    if title_tag:
        return title_tag.string
    else:
        return None


def url_has_been_crawled(url):
    memory = get_entry_from_url(url)
    if memory is None:
        return False
    return memory["metadata"]["crawled"]


def cache_page(title, body_text, html, links):
    # check that cache folder exists

    # create a folder for the url, remove http, https, :, /, ? etc replace all special characters with _

    # save the html to raw.html

    # clean up the body, any \n\n\n\n... should be replaced by a \n
    # regex the body for header, footer, nav etc if it isnt

    # new new csv file called meta.csv

    # url, title, meta, linked_from

    return


def cache_media(url):
    # check that cache folder exists

    # create a folder for the url, remove http, https, :, /, ? etc replace all special characters with _

    # check inside that for a media folder

    # download file

    # hash it

    # rename file to <filename>_<hash>.<ext>
    return


def merge_relative_paths(url, backlink):
    # TODO: if url is relative, get backlink and combine

    # TODO: if link is hard /, get domain of backlink and combine
    return url


def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a_tag in soup.find_all("a"):
        # Check if the link has non-blank text and an href attribute
        if a_tag.text.strip() and a_tag.get("href"):
            links.append({"name": a_tag.text, "url": a_tag.get("href")})

    return links


async def crawl(url, depth=0, maximum_depth=3, context={}):
    # TODO: if url has a /# at the end of it, remove the /# (and maybe words after until ? etc) to help with dedupe
    # pass in backlink url

    # skip_media_types is a list of file extensions to skip
    # if the url ends with any of the file extensions, skip it
    if any([url.endswith("." + ext) for ext in skip_media_types]):
        print("Skipping url:", url)
        add_url_entry(url, url, valid=True, type="media", crawled=False)
        return

    # if the url includes youtube.com in the domain, return
    if any([media_url in url for media_url in default_media_domains]):
        print("Skipping media domain:", url)
        add_url_entry(url, url, valid=True, type="media_url", crawled=False)
        return

    # if the url is on the bla
    print("Attempting crawl of url:", url)
    if url_has_been_crawled(url):
        print("Url has already been crawled.")
        return
        
    async with aiohttp.ClientSession() as session:

        page = await async_navigate_to(url, None)

        # check if the body contains any of the keywords
        # if it doesn't return
        body_html = await async_get_body_html(page)

        html = await async_get_document_html(page)

        body_text = await async_get_body_text(page)

        title = extract_page_title(html)

        if title is None:
            # throw error until we see some edge cases
            raise Exception("Title is none, skipping url.")
            # print("Warning! Title is none, using body text instead.")
            # title = body_text[:10]

        # if none of the keywords are contained
        if not any([keyword in body_text for keyword in context["keywords"]]):
            print("Skipping url:", url)
            print("No keywords found in body text.")
            # add the url to the memory
            add_url_entry(url, title, valid=False, crawled=True)
            return

        # the logic here is that our scraper was too agressive, or the content wasnt loaded directly for some reason

        # if we have reached maximum depth, skip
        if depth > maximum_depth:
            return

        links = extract_links(body_html)

        cache_page(title, body_text, html, links)
        print('Adding URL to memory: "' + url + '"')
        add_url_entry(url, title, valid=True, crawled=True)

        for link in links:
            if isinstance(link, str):
                link = json.loads(link)

            if not link["url"].startswith("https://") and not link["url"].startswith("http://"):
                print('*** WARNING! Skipping link because it does not start with "https://" or "http://"')
                continue
            print("Crawling link:", link["name"])
            await crawl(link["url"], depth=depth + 1)


def validate_crawl(context):
    # TODO: scan the project directory for any already-scraped urls
    # maybe we need to just use memory for this and then we can pull this from memory into context here
    return context


from traceback import format_exc

async def crawl_all_urls(urls, context):
    # Create a coroutine for each url to crawl
    tasks = [crawl(url, 0, 3, context) for url in urls]
    
    # Now we run each coroutine
    for task in asyncio.as_completed(tasks):
        try:
            result = await task
        except Exception as e:
            print(f"Exception occurred: {e}")
            print(f"Traceback: {format_exc()}")


def main(context):
    print("Starting crawl...")
    context["skip_media_types"]: skip_media_types
    context["media_domains"]: default_media_domains
    context["link_blacklist"]: default_link_blacklist
    context["element_blacklist"]: default_element_blacklist

    urls = context["urls"]
    if not isinstance(urls, list):
        urls = urls.replace(",", "\n").split("\n")
        urls = [url.strip() for url in urls]

    print('urls')
    print(urls)

    async def start_crawl(context):
        await crawl_all_urls(urls, context)

    # context = validate_crawl(context)

    asyncio.run(start_crawl(context))

    return context