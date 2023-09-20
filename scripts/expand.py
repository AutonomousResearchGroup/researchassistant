import pandas as pd
from easycompletion import text_completion



# Step 2: Loop through the CSV file in chunks and process each chunk
def process_csv_chunks(input_csv, output_csv):
    chunksize = 25

    for i, chunk in enumerate(pd.read_csv(input_csv, chunksize=chunksize, on_bad_lines='skip')):
        # Convert the chunk to a CSV formatted string
        csv_data_str = chunk.to_csv(index=False, sep=",")

        # Prepare the prompt
        prompt = (
            f"{csv_data_str}\n```" + """The above is comma separated data. The columns are "category", "topic", "subtopic", "description", "original topic" and "original subtopic"
TASK:
- Add more topics to each category by creating new rows with the same category and a new topic and subtopic
- Add more subtopics to each topic by creating new rows with the same category and topic and a new subtopic and description
- Each topic/subtopic pair must also have a description
- Descriptions should be 1 complete sentence, with at least 10 words, and should include real-world examples that are under the subtopic
- Output should be in CSV format, comma separated with " quotations around each row
- Do not include a header row
- Column A should be "category", Column B should be "topic", Column C should be "subtopic", Column D should be "description", Column E should have the text 'generated'
"""
        )

        # Call the function
        response = text_completion(
            text=prompt,
            model="gpt-4",
        )
        
        # Print the response
        print(response)

        # save response to ./dump.txt
        with open(output_csv, "a") as f:
            f.write(response['text'] + "\n")



# Specify the paths to the input and output CSV files
input_csv = "topics_out.csv"
output_csv = "expanded.csv"

# Run the function to process the CSV file in chunks and save the cleaned data to a new CSV file
process_csv_chunks(input_csv, output_csv)
