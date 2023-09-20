import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_google_search_results(site, query, num_results=100):
    print(f"Searching for {query} in {site}")
    search_results = set()
    query = query.replace(" ", "+")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
    for start in range(0, num_results, 10):
        url = f"https://www.google.com/search?q=site:{site}+{query}&start={start}"
        response = requests.get(url, headers=headers)
        print(response)
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            if "url?q=" in a["href"]:
                search_results.add(a["href"].split("url?q=")[1].split("&sa=U")[0])
        time.sleep(1)
    return search_results

def main(websites, topics):
    with open("collected.csv", "a", newline='', encoding='utf-8') as file:
        for website in websites:
            for topic in topics:
                results = get_google_search_results(website, topic)
                print(results)
                if results:
                    df = pd.DataFrame(list(results), columns=["URLs"])
                    df.to_csv(file, index=False, header=False, mode='a')

if __name__ == "__main__":
    # Reading websites from the first column of "sites.csv"
    websites_df = pd.read_csv("sites.csv", header=None)
    websites = websites_df.iloc[:, 0].tolist()

    topics = [
        "artificial intelligence",
        "existential risk",
        "ai takeover",
        "autonomous agent",
        "ai agent",
    ]  # Replace with your array of topics
    main(websites, topics)
