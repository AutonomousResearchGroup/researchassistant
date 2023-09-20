import csv

# Read URLs from collected.csv
with open('collected.csv', 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    urls = [row[0] for row in reader]

# Remove URL parameters
cleaned_urls = [url.split('?')[0] for url in urls]

# Save cleaned URLs back to collected.csv
with open('collected.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    for url in cleaned_urls:
        writer.writerow([url])
