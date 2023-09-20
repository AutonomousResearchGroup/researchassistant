import arxiv
import csv

query = 'AI Existential Risks'

search = arxiv.Search(
    query = query,
    max_results = 100, # To get all the results, use float('inf') but it'll be slow
    sort_by = arxiv.SortCriterion.Relevance
)

results = search.results()

# Write to CSV
with open("/tmp/arxiv_results.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(["Title", "Authors", "Abstract", "Links", "PDF Link"])

    # Iterate over the results and write each row to the CSV file
    for result in results:
        author_string = ", ".join([author.name for author in result.authors])
        link_string = " ".join([f'[{link.title}]({link.href})' for link in result.links])
        writer.writerow([result.title, author_string, result.summary, link_string, result.pdf_url])