summarization_function = compose_function(
    name="summarize_text",
    description="Summarize the text and decide if the article is relevant to the research topic.",
    properties={
        "summary": {
            "type": "string",
            "description": "Detailed summary of the text, along with an explanation of why the text is or isn't relevant.",
        },
        "relevant": {
            "type": "boolean",
            "description": "Is the text relevant to the research topic?",
        },
    },
    required_properties=["summary", "relevant"],
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
                },
            },
        }
    },
    required_properties=["claims"],
)
