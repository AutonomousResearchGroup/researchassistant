import hashlib
import re
from agentmemory import create_memory, get_memories, update_memory

def url_to_filename(url):
    # Removing http/https part to make the filename shorter
    url = re.sub(r'^https?:\/\/', '', url)
    
    # Removing or replacing non-alphanumeric characters
    url = re.sub(r'[^a-zA-Z0-9]', '_', url)

    # get the domain from the url, basically everything before the first /
    domain = url.split("/")[0]

    # If URL is too long, hash it to ensure it fits and it's still unique
    if len(url) > 32:
        url = domain + hashlib.md5(url.encode()).hexdigest()[:32]

    return url

def add_url_entry(url, text, context, type="url", backlink=None, valid=True, crawled=True):
    project_name = context["project_name"]
    url_data = {
        "text": text,
        "url": url,
        "type": type,
        "project_name": project_name,
        "valid": valid,
        "crawled": crawled,
    }
    if backlink is not None:
        url_data["backlink"] = backlink

    create_memory(
        "scraped_urls",
        url,
        url_data,
    )
    if context.get("scraped_urls", None) is None:
        context["scraped_urls"] = []
    context["scraped_urls"].append(url_data)
    return context


def get_entry_from_url(url):
    memory = get_memories("scraped_urls", filter_metadata={"url": url})
    memory = memory[0] if len(memory) > 0 else None
    return memory

def get_url_entries(context):
    project_name = context["project_name"]
    return get_memories("scraped_urls", filter_metadata={"project_name": project_name})

def get_url_entries(context, valid=None, crawled=None):
    project_name = context["project_name"]
    # if valid and crawled are none, return all
    if valid is None and crawled is None:
        return get_memories("scraped_urls")
    dict = {
        "valid": valid,
        "crawled": crawled,
        "project_name": project_name
    }
    # if any values in dict are None, remove
    dict = {k: str(v) for k, v in dict.items() if v is not None}
    return get_memories("scraped_urls", filter_metadata=dict)


def update_url_entry(
    id, text, valid=True, crawled=True, type="url", category="scraped_urls"
):
    update_memory(
        category, id, text, {"valid": valid, "crawled": crawled, "type": type}
    )


def url_has_been_crawled(url):
    memory = get_entry_from_url(url)
    if memory is None:
        return False
    return memory["metadata"]["crawled"]
