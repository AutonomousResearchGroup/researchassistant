from easycompletion import compose_function


summarization_function = compose_function(
    name="summarize_text",
    description="Summarize the text and decide if the article is relevant to the research topic. Determine the author and when the article was written if these are available in the text, otherwise enter 'None' for these values.",
    properties={
        "summary": {
            "type": "string",
            "description": "Detailed summary of the text, along with an explanation of why the text is or isn't relevant.",
        },
        "relevant": {
            "type": "boolean",
            "description": "Is the text relevant to the research topic?",
        },
        "author": {
            "type": "string",
            "description": "Who is the author of the text? If the author is not known, enter 'None'.",
        },
        "date": {
            "type": "object",
            "description": 'Extract the date that the text was written. If one of the values (field or month) is not known, write 0. For example, if the text was written in 2020, but the month and day are not known, write "year": 2020, "month": 0, "day": 0.',
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "Year the text was written (1900-2023 or 0 if unknown)",
                },
                "month": {
                    "type": "integer",
                    "description": "Month the text was written. (1-12 or 0 if unknown)",
                },
                "day": {
                    "type": "integer",
                    "description": "Day the text was written. (1-31 or 0 if unkonwn)",
                },
            },
        },
    },
    required_properties=["summary", "relevant", "author", "date"],
)

summarization_prompt_template = """
I have the following document
```
{{text}}
```

I am a researcher with the following research topic:
{{research_topic}}

Please summarize the document and determine if the document is relevant to the research topic. In your summary, explain why it is or isn't relevant."
"""

claim_extraction_prompt_template = """\
I am a researcher with the following research topic:
{{research_topic}}

I am extracting claims from a document. {{author}}

Summary of the full document:
{{summary}}

Current section of the document I am working on:
{{text}}

TASK: Extract claims from the currect section I am working on.

- Include the specific passage of source text that the claim references as the source parameter.
- Please extract the specific and distinct claims from this text, and respond with all factual claims as a JSON array. Avoid duplicate claims.
- Each claim should be one statement. Ignore questions, section headers, fiction, feelings and rhetoric: they are not factual claims.
- DO NOT just of use pronouns or shorthand like 'he' or 'they' in claims. Use the actual complete name of the person or thing you are referring to and be very detailed and specific.
- Claims should include extensive detail so that they can stand alone without the source text. This includes detailed descriptions of who, what and when.
- ALWAYS use the full name and title of people along with any relationship to organizations. For example, instead of 'the president', use 'Current U.S. President Joe Biden'. Do not use nicknames or short names when referring to people. Instead of "Mayor Pete", use "Pete Buttigieg".
- Ignore anything that isn't relevant to the research topic, including political opinions, feelings, and rhetoric. We are only interested in claims that are factual, i.e. can be proven or disproven.
- Please disambiguate and fully describe known entities. For example, instead of 'Kim the Rocketman', use 'North Korean leader Kim Jong Un'. Instead of 'the 2016 election', use 'the 2016 U.S. presidential election'.
- Split claims up into specific statements, even if the source text has combined the claims into a single statement. There can be multiple claims for a source. For example, if a source sentence makes multiple claims, these should be separated

Output should be formatted as an array of claims, which each have the following structure:
[{
    source: string # "The exact source text referenced in the claim",
    claim: string # "The factual claim being made in the source text",
    relevant: boolean # Is the claim relevant to the research topic and summary?
    debate_question: string # "A debate question which the claim would be a viewpoint in. Ideally the question is one which the claim directly answers or at least in which the claim is foundational to another claim."
    author: string # "Who is the author of the claim, i.e. the person who is stating it? If the character is fictional or the claim is hypothetical, write 'None'. If the claim is a quote, the author is the person being quoted. If the claim is a statement by the author of the article then it is probably them."
}, {...}]
"""

claim_extraction_function = compose_function(
    name="extract_claims",
    description="Extract all factual claims from the section of text.",
    properties={
        "claims": {
            "type": "array",
            "description": "Array of claims extracted from the current section of the source text",
            "items": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "The exact source text from which the claim has been extracted",
                    },
                    "claim": {
                        "type": "string",
                        "description": "A factual claim made in the source text",
                    },
                    "relevant": {
                        "type": "boolean",
                        "description": "Determine whether this claim is relevant to the research topic. If it is not relevant, set this to False, otherwise set it to True.",
                    },
                    "author": {
                        "type": "string",
                        "description": "Who is the author of the claim, i.e. the person who is stating it? String or 'None' if not sure. The article author should be assumed if that is known and the claim is not a quote.",
                    },
                    "debate_question": {
                        "type": "string",
                        "description": "A debate question which the claim is relevant to or answers directly.",
                    }
                },
            },
        }
    },
    required_properties=["claims"],
)
