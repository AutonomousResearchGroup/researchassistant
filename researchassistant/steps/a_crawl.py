from agentbrowser import create_page
from agentbrowser.browser import (
    navigate_to,
    get_body_text,
)

import json
import re

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


def url_has_been_crawled(url):
    memory = get_entry_from_url(url)
    if memory is None:
        return False
    return memory["metadata"]["crawled"]


def cache_page(topic_data, title, body_text, html, links):
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


default_options = {
    "keywords": [],
    "skip_media_types": skip_media_types,
    "media_domains": default_media_domains,
    "link_blacklist": default_link_blacklist,
    "element_blacklist": default_element_blacklist,
}


async def crawl(url, depth=0, maximum_depth=3, options={}):
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
    
    page = create_page()

    page = await navigate_to(url, page)

    # check if the body contains any of the keywords
    # if it doesn't return
    body_text = await get_body_text(page)

    title = await page.title()

    # if none of the keywords are contained
    if not any([keyword in body_text for keyword in options["keywords"]]):
        print("Skipping url:", url)
        print("No keywords found in body text.")
        # add the url to the memory
        add_url_entry(url, title, valid=False, crawled=True)
        return

    # Extract the links and crawl them too. Return a list of links as { "innerText": "link" }
    # filter out any links where the innerText is in the blacklist (check all in lowercase)
    # also filter out any links where the a element is inside any element that has an id or class which contains any of the element_blacklist items (check all in lowercase)
    # object should be returned like { "text": a.innerText, "href": a.href }
    # pack element_blacklist into a str with commas
    element_blacklist_str = ",".join(options["element_blacklist"])

    # extract links the easy way
    a_elements = await page.querySelectorAll("a")

    a_links = []

    for a_element in a_elements:
        # Get the href attribute value of each <a> element
        a_href = await page.evaluate(
            '(element) => element.getAttribute("href")', a_element
        )
        # Get the innerText of each <a> element
        a_text = await page.evaluate("(element) => element.innerText", a_element)
        # Get the innerHTML of each <a> element
        a_html = await page.evaluate("(element) => element.innerHTML", a_element)
        # if a_text is none, regex the a_html to get the innerText by removing any tags
        if not a_text:
            a_text = re.sub(r"<.*?>", "", a_html)
        # if a_href is none, skip this link
        if not a_href:
            continue
        # add the link to the list
        a_links.append({"href": a_href, "text": a_text})

    # TODO: get the document html

    html = await page.content()

    # extract links the hard way
    body = await page.evaluate("() => document.body.innerHTML")

    # replace all '\' with ''
    body = body.replace("\n", "").replace("\t", "").replace("\r", "").replace("\\", "")

    re_links = re.findall(r'<a.*?href="(.*?)".*?>(.*?)</a>', body)

    # for each link, the second value in the tuple is the inner text
    # remove any tags from the inner text
    re_links = [(link[0], re.sub(r"<.*?>", "", link[1])) for link in re_links]

    # map re_links to a list of objects with the keys "href" and "text"
    re_links = [{"href": link[0], "text": link[1]} for link in re_links]

    # merge a_links and re_links by checking if the href is the same
    # if either doesn't have text, use the other one
    # if href and text is the same, skip
    # if href is the same but text is different, use the text from a_links
    for re_link in re_links:
        for a_link in a_links:
            if re_link["href"] == a_link["href"]:
                if not re_link["text"]:
                    re_link["text"] = a_link["text"]
                break
        else:
            # if the link is not in a_links, add it
            a_links.append(re_link)

    links = await page.evaluate(
        '''() => {
            const element_blacklist_str = "'''
        + element_blacklist_str
        + """";
            // convert to array
            const element_blacklist = element_blacklist_str.split(',');
            function filterLinks(links) {
                return links.filter(link => {
                    if (link === {} || link === "{}" || !link || !link.href) {
                        return false;
                    }
                    let parent = link.parentElement;
                    while (parent) {
                        if (element_blacklist.includes(parent.id.toLowerCase()) || element_blacklist.includes(parent.className.toLowerCase()) || element_blacklist.includes(parent.tagName.toLowerCase())) {
                            // if the parent element type is a footer, nav, header, etc. then skip this link
                            if (parent.tagName === 'NAV' || parent.tagName === 'FOOTER' || parent.tagName === 'HEADER')
                            return false;
                        }
                        parent = parent.parentElement;
                    }
                    return true;
                });
            }
            // get all links that have an href
            const links = Array.from(document.querySelectorAll('a')).map(a => {
                return {
                    href: a.href,
                    text: a.innerText || a.innerHTML
                }
            });
            // filter out any links where the innerText is in the blacklist (check all in lowercase)
            const filteredLinks = filterLinks(links);
            // return the filtered links
            return filteredLinks;

        }"""
    )

    # if the length of links is less than 3, and the length of a_links is greater than 3, use a_links
    if len(links) < 3 and len(a_links) > 3:
        links = a_links

    # the logic here is that our scraper was too agressive, or the content wasnt loaded directly for some reason, for example on lesswrong, so we gotta yolo it

    # if we have reached maximum depth, skip
    if depth > maximum_depth:
        return

    cache_page(title, body_text, html, links)
    print('Adding URL to memory: "' + url + '"')
    add_url_entry(url, title, valid=True, crawled=True)

    # Otherwise, crawl the next level of links
    for link in links:
        # if link is a string, convert it to an object
        if isinstance(link, str):
            link = json.loads(link)
        # if the href doesn't contain https or http, skip it
        if not link["href"].startswith("https://") and not link["href"].startswith(
            "http://"
        ):
            print(
                '*** WARNING! Skipping link because it does not start with "https://" or "http://"'
            )
            continue
        print("Crawling link:", link["text"])
        await crawl(link["href"], depth=depth + 1)


# # debug crawling stuff
# # Read initial links from the file and start crawling
# with open("urls.txt", "r") as f:
#     initial_links = f.read().splitlines()

#     options = default_options
#     options["keywords"] = [
#         "existential risk",
#         "societal impact",
#         "ai",
#         "artificial intelligence",
#     ]

#     async def start_crawl():
#         tasks = []
#         for i in range(0, len(initial_links), 10):
#             # grouping 10 links together
#             links_group = initial_links[i : i + 10]

#             # create a task for each link and append to the tasks list
#             for link in links_group:
#                 tasks.append(crawl(link, options=options))

#             # use asyncio.gather to run all tasks concurrently
#             await asyncio.gather(*tasks)

#     # create a new asyncio loop
#     asyncio.get_event_loop().run_until_complete(start_crawl())
