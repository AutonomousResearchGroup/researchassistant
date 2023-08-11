from bs4 import BeautifulSoup


def extract_page_title(html):
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.title
    if title_tag:
        return title_tag.string
    else:
        return None
    

def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a_tag in soup.find_all("a"):
        # Check if the link has non-blank text and an href attribute
        if a_tag.text.strip() and a_tag.get("href"):
            links.append({"name": a_tag.text, "url": a_tag.get("href")})

    return links

