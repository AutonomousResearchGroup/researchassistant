import sys

from extract import extract_from_file_or_url
from topics import add_topics_to_memory, get_topics_from_csv
from agentbrowser import get_event_loop

add_topics_to_memory(get_topics_from_csv())

# get input_file and output_file from sys.argv
# input_file = (
#     (len(sys.argv) > 1 and sys.argv[1])
#     or "https://www.lesswrong.com/posts/gEchYntjSXk9KXorK/uncontrollable-ai-as-an-existential-risk"
# )
# output_file = (len(sys.argv) > 2 and sys.argv[2]) or "claims.csv"

goal = "I am researching existential risk and the societal impact of artificial intelligence. I am interested in anything related to AI, machine learning, and the future of humanity. I am also interested in the positive societal impacts of AI, including how it could impact other existential risks such as climate change and supply chain risks."


urls=[
"https://aiimpacts.org/three-kinds-of-competitiveness/"
# "https://www.alignmentforum.org/posts/qYzqDtoQaZ3eDDyxa/distinguishing-ai-takeover-scenarios"
# "https://www.alignmentforum.org/posts/4kYkYSKSALH4JaQ99/toy-problem-detective-story-alignment"
# "https://www.alignmentforum.org/posts/4DegbDJJiMX2b3EKm/tai-safety-bibliographic-database"
# "https://www.openphilanthropy.org/blog/ai-governance-grantmaking"
# "https://www.alignmentforum.org/posts/Tr7tAyt5zZpdTwTQK/the-solomonoff-prior-is-malign"
# "https://www.gwern.net/Scaling-hypothesis"
# "https://www.alignmentforum.org/posts/qEjh8rpxjG4qGtfuK/the-backchaining-to-local-search-technique-in-ai-alignment"
# "https://www.alignmentforum.org/s/boLPsyNwd6teK5key"
]

# input and output are the first and second arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

extract_from_file_or_url(input_file, output_file, goal)