import requests
from fuzzywuzzy import fuzz


def get_wayback_captures(url):
    wayback_url = f"https://web.archive.org/cdx/search/cdx?url={url}&output=json&fl=timestamp,original&filter=statuscode:200"
    response = requests.get(wayback_url)
    return response.json()[1:] if response.status_code == 200 else []


def fetch_content_from_wayback(url, timestamp):
    archived_url = f"https://web.archive.org/web/{timestamp}id_/{url}"
    response = requests.get(archived_url)
    return response.text if response.status_code == 200 else ""


def find_earliest_date_with_fuzzy_match(url, body, threshold=80):
    captures = get_wayback_captures(url)
    for capture in captures:
        timestamp, original_url = capture
        archived_content = fetch_content_from_wayback(original_url, timestamp)
        if fuzz.ratio(archived_content, body) >= threshold:
            return timestamp
        # lowercase archived_content
        archived_content = archived_content.lower()
        body = body.lower()
        if archived_content in body or body in archived_content:
            return timestamp
    return None
