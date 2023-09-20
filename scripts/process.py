import pandas as pd
from easycompletion import chat_completion, function_completion, compose_function, text_completion



# Step 2: Loop through the CSV file in chunks and process each chunk
def process_csv_chunks(input_csv, output_csv):
    chunksize = 75

    for i, chunk in enumerate(pd.read_csv(input_csv, chunksize=chunksize)):
        # Convert the chunk to a CSV formatted string
        csv_data_str = chunk.to_csv(index=False, sep=",")

        # Prepare the prompt
        prompt = (
            f"{csv_data_str}\n```" + """The above is comma separated data. The colums are "category", "topic", "subtopic"

TASK:
- Fill in any categories that are set to <unknown>
- Categories are: Capabilities, Challenges, Ethics, Regulation, Threats, Goals/Paths, Impact, Safety, Terms/Understanding, Timelines, Other
- Transform any questions or unclear topics/subtopics into a topic/subtopic pair
- Add any missing topics or subtopics
- Add a description for each topic/subtopic pair
- All entries must have a topic, subtopic and description

Task example input:
"Regulation","Should we limit any specific type of content which AI may generate?",""
Task example output:
"AI Content Limitations", "Content Restriction Criteria","Discussion on the criteria for determining restrictions on AI-generated content"

Task example input:
"Threats","Threats","What are the potential threats / concerns posed by AI/AGI", "Cult-like following deployes AI/AGI to disrupt civilization for a number of reasons"
Task example output:
"Threats", "Terrorism", "AI Cults", "Humans or human-led organizations using AI to commit acts of terrorism"

- Please DO NOT use "AI" as a category, topic or subtopic, since that is the parent topic of our domain research and is too broad
- Again, the topic CAN NOT be as broad as "AI"-- everything we are researching is about AI, topics need to be much more specific.
- Topics and subtopics should be very specific. You must be more descriptive and specific with topics.
- Try to group and consolidate topics where they are very similar
- All entries MUST have a detailed description. Description cannot be left blank.
- Description should include examples and definition of the subtopic
- Topics and subtopics must be topic statements, NOT questions. Questions are not topics.
- Descriptions should be 1-2 complete sentences, including examples that would be included under the subtopic
- Output should be in CSV format, comma separated with " quotations around each row
- Do not include header row
- Include the original topic and subtopic after the topic, subtopic and description
- Column A should be "category", Column B should be "topic", Column C should be "subtopic", Column D should be "description", Column E should be the original topic and column F should be the original subtopic
"""
        )

        print(prompt)

        # Call the function
        response = text_completion(
            text=prompt,
            model="gpt-4",
        )
        
        # Print the response
        print(response)

        with open(output_csv, "a") as f:
            f.write(response['text'] + "\n")



# Specify the paths to the input and output CSV files
input_csv = "topics.csv"
output_csv = "topics_out.csv"

# Run the function to process the CSV file in chunks and save the cleaned data to a new CSV file
process_csv_chunks(input_csv, output_csv)
