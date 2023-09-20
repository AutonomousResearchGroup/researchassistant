import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

subscription_key = "2cfa95473a494a88bc4fcdeab8798ec0"
endpoint = "https://api.bing.microsoft.com/v7.0/search"

# Construct a request


def get_bing_search_results(site, query, num_results=100):
    print(f"Searching for \"{query}\" in {site}")
    search_results = set()
    mkt = "en-US"
    query_formatted = f'site:{site} "{query}"'
    params = {"q": query_formatted, "mkt": mkt}
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}

    for offset in range(0, num_results, 50):  
        params.update({'count': 50, 'offset': offset})
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()

        print('response')
        print(response)
        
        if response.status_code == 200:
            try:
                result_items = response.json()['webPages']['value']
                for item in result_items:
                    url = item['url']
                    resp = requests.get(url)
                    if resp.status_code == 200:
                        page_content = resp.text.lower()
                        soup = BeautifulSoup(page_content, 'html.parser')
                        page_text = soup.get_text()
                        if query.lower() in page_text:
                            search_results.add(url)
                            print(url)
                    elif resp.status_code == 404:
                        print(f"URL returned 404: {url}")
                    else:
                        print(f"URL returned status code {resp.status_code}: {url}")
            except KeyError:
                print("No results returned or reached the end of results.")
            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve page content: {e}")
        else:
            print(f"Failed to retrieve the results. Status code: {response.status_code}")

    return search_results


def main(websites, topics):
    with open("collected.csv", "a", newline='', encoding='utf-8') as file:
        for website in websites:
            for topic in topics:
                results = get_bing_search_results(website, topic)
                print(results)
                if results:
                    df = pd.DataFrame(list(results), columns=["URLs"])
                    df.to_csv(file, index=False, header=False, mode='a')

if __name__ == "__main__":
    # Reading websites from the first column of "sites.csv"
    websites_df = pd.read_csv("sites.csv", usecols=[0])
    websites = websites_df.iloc[:, 0].tolist()

    topics = [
        "artificial intelligence",
        "existential risk",
        "ai takeover",
        "autonomous agent",
        "ai agent",
    ]  # Replace with your array of topics

    ignore = [
        'covid',
        'coronavirus',
        'pandemic',
        'climate change',
        'global warming',
        'stable diffusion'
    ]
    main(websites, topics)
