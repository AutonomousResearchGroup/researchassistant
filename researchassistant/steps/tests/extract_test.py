import sys

from researchassistant.steps.b_extract import extract_from_file_or_url

research_topic = "I am researching existential risk and the societal impact of artificial intelligence. I am interested in anything related to AI, machine learning, and the future of humanity. I am also interested in the positive societal impacts of AI, including how it could impact other existential risks such as climate change and supply chain risks."

urls=[
"https://test-page-to-crawl.vercel.app/nolinks"
]

# input and output are the first and second arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

extract_from_file_or_url(input_file, output_file, research_topic)