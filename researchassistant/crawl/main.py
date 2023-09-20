import asyncio
import json
from urllib.parse import urljoin
from traceback import format_exc
from asyncio import Semaphore
import logging

logging.basicConfig(level=logging.INFO)


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
from researchassistant.shared.custom_html import extract_links, extract_page_title
from researchassistant.shared.urls import (
    add_url_entry,
    url_has_been_crawled,
)
from researchassistant.shared.transcribe import transcribe

# Global set for deduplication
crawled_links = set()

async def crawl(url, context, backlink=None, sem=None, depth=0, maximum_depth=3):
    logging.info(f"Starting crawl function for URL {url} at depth {depth}")

    # if we have reached maximum depth, skip
    if depth > maximum_depth:
        return

    print("crawling", url)

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
    transcribed_text = ""
    if any([media_url in url for media_url in default_media_domains]):
        try:
            transcribed_text = await transcribe(url)
        except Exception as e:
            print(f"Error transcribing the URL {url}: {e}")
            print("Skipping media domain:", url)
            context = add_url_entry(
                url, url, context, valid=True, type="media_url", crawled=False
            )
            return
    page = await async_create_page(url)

    try:
        page = await async_navigate_to(url, page)
        
        body_html = await async_get_body_html(page)
        html = await async_get_document_html(page)
        body_text = await async_get_body_text(page)
        body_text = "".join([body_text, transcribed_text])

        title = extract_page_title(html) or body_text[:10]

        if not any(keyword in body_text for keyword in context["keywords"]):
            add_url_entry(url, title, context, valid=False, crawled=True)
            return

        links = extract_links(body_html)
        links = list(set(urljoin(url, link["url"]) for link in links if link["url"] not in {"#", "", "/"}))

        metadata = {
            "title": title,
            "document_html": html,
            "body_html": body_html,
            "text": body_text,
            "source": url,
            "links": json.dumps(links),
            "status": "crawled",
        }

        memories = get_memories(
            context["project_name"] + "_documents", contains_text=body_text.strip()
        )
        if len(memories) > 0:
            print("Skipping url:", url)
            print("Document already exists. Text is the same.")
            return
        memories = get_memories(
            context["project_name"] + "_documents", filter_metadata={"source": url}
        )
        # sanity check that same url doesnt already exist
        if len(memories) > 0:
            print("Skipping url:", url)
            print("Document already exists. Url is the same.")
            return

        # then sanity check that same text doesnt already exist
        memories = search_memory(
            category=context["project_name"] + "_documents",
            search_text=body_text,
            max_distance=0.05,
        )
        if len(memories) > 0:
            related_document_id = memories[0]["id"]
            metadata["related_to"] = related_document_id

            # TODO: related_to should be determined by which one is older


        print('creating memory')
        create_memory(
            context["project_name"] + "_documents",
            body_text,
            metadata,
        )

        add_url_entry(url, title, context, backlink=backlink, valid=True, crawled=True)

        print('crawling valid links')
        tasks = [asyncio.create_task(crawl(link, context, sem=sem, depth=depth+1, maximum_depth=maximum_depth)) for link in links]
        await asyncio.gather(*tasks)

        logging.info(f"Finishing crawl function for URL {url} at depth {depth}")

    finally:
        if page is not None:
            await page.close()

    return context


async def crawl_all_urls(urls, context, sem, backlink=None, depth=0, maximum_depth=3):
    logging.info(f"Starting crawl_all_urls with urls: {urls} at depth {depth}")
    
    async def bound_crawl(sem, url):
        logging.info(f"Starting bound_crawl for URL {url}")

        async with sem: 
            try:
                await crawl(url, context, backlink, sem, depth, maximum_depth)
            except Exception as e:
                logging.error(f"Exception in bound_crawl: {e}")
                logging.error(f"Traceback: {format_exc()}")

        logging.info(f"Finishing bound_crawl for URL {url}")

    try:
        tasks = [asyncio.create_task(bound_crawl(sem, url)) for url in urls]
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Exception in crawl_all_urls: {e}")
        logging.error(f"Traceback: {format_exc()}")
    finally:
        # Ensure resources are freed in case of failure
        for task in tasks:
            task.cancel()

    logging.info(f"Finishing crawl_all_urls with urls: {urls} at depth {depth}")




def main(context):
    logging.info("Starting main function")
    
    context["skip_media_types"] = skip_media_types
    context["media_domains"] = default_media_domains
    context["link_blacklist"] = default_link_blacklist
    context["element_blacklist"] = default_element_blacklist

    urls = context["urls"]
    if not isinstance(urls, list):
        urls = urls.replace(",", "\n").split("\n")
        urls = [url.strip() for url in urls]

    print("Starting crawl...")

    sem = asyncio.Semaphore(value=3)
    
    crawl_all_urls_coro = crawl_all_urls(urls, context, sem) # Get coroutine object

    try:
        asyncio.run(crawl_all_urls_coro) # Run the coroutine here
    except Exception as e:
        logging.error(f"An error occurred during crawling: {e}")
        # Here, you might want to add code to gracefully handle the error, perhaps by retrying the operation a limited number of times
    finally:
        # If agentmemory library provides a way to cleanly close the database connection, do it here
        pass
    
    logging.info("Finishing main function")
    return context
