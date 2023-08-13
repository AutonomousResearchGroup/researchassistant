from agentmemory import create_memory, search_memory


def add_topics_to_memory(topic_rows):
    out_topic_rows = []
    for topic_row in topic_rows:
        topic_row_values = topic_row.split(",")
        topic = topic_row_values[0]
        # join subtopics with commas
        subtopic = ",".join(topic_row_values[1:])

        out_topic_rows.append({"topic": topic, "subtopic": subtopic})
        create_memory(
            "topics", topic + ": " + subtopic, {"topic": topic, "subtopic": subtopic}
        )

    # sort topic rows alphabetically by topic
    out_topic_rows = sorted(out_topic_rows, key=lambda k: k["topic"])

def format_topics(topic_rows):
    # set a topics_text variable with the topics and subtopics as a string
    # for each topic, create a new line with Topic: <topic>, Subtopics: <subtopics>
    # when the topic changes, create a newline
    topic_subtopics = []

    for topic_row in topic_rows:
        topic_row_topic = topic_row["metadata"]["topic"]
        topic_row_subtopic = topic_row["metadata"]["subtopic"]
        topic_subtopics.append(
            {"topic": topic_row_topic, "subtopic": topic_row_subtopic}
        )

    topic_subtopics.sort(key=lambda k: k["topic"])

    topics_text = ""
    current_topic = ""
    for topic_row in topic_subtopics:
        if topic_row["topic"] != current_topic:
            # if the last part of topics_text is "\nSubtopics: ", remove it
            if topics_text.endswith("\nSubtopics: "):
                topics_text = topics_text[:-12]
            # remove the last comma and space
            else:
                topics_text = topics_text[:-2]

            # add a new topic
            if current_topic != "":
                topics_text += "\n\n"
            topics_text += "Topic: " + '"' + topic_row["topic"] + '"' + "\n"
            topics_text += "Subtopics: "
            current_topic = topic_row["topic"]
        if (
            topic_row["subtopic"]
            and topic_row["subtopic"] is not None
            and topic_row["subtopic"] != ""
        ):
            # replace all newlines in subtopic with , and space
            subtopic = topic_row["subtopic"].replace("\n", ", ")
            topics_text += '"' + subtopic + '", '

    topics_text = topics_text[:-2]
    return topics_text
