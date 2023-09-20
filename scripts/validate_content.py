from urllib.parse import urlparse, urlunparse
import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv

def check_content(url):
    try:
        # Clean URL by removing parameters
        parsed_url = urlparse(url)
        clean_url = urlunparse(
            [parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", ""])
        
        # Skip unwanted file types
        if clean_url.endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx')):
            return "skipped"
        
        response = requests.get(clean_url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        if 'artificial intelligence' in text.lower() or 'existential risk' in text.lower():
            return "relevant"
        else:
            return "irrelevant"
    except requests.exceptions.RequestException:
        return "error"

def main():
    # Read the input CSV file without a header
    df = pd.read_csv('collected.csv', header=None)
    
    # Open the output file in write mode to overwrite any existing data
    with open('output.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Relevance'])  # Write the header
        
        # Loop through each URL, check its content, and write the result to the output file
        for url in df[0]:
            relevance = check_content(url)
            writer.writerow([url, relevance])

if __name__ == "__main__":
    main()
