from agentmemory import create_memory


def research(
    topic, # all data is stored under this
    subtopics, # subtopics, will be used for expanding search (Optional)
    description, # detailed description, will be used for evaluating if things are relevant
    type="topic",
    include_keywords=[], # Include documents which have these keywords in relevancy check (Optional)
    exclude_keywords=[], # Exclude documents which have these keywords in relevancy check (Optional)
    start_urls=[], # list of urls to start from, guaranteed to be included in research (Optional)
    path="data", # path to store data, final path will be <path>/<topic> (Optional)
    use_existing=True, # use existing data on topic fresh or start fresh (Optional)
    ):


    # if toic exists and use existing is false, wipe it

    # 
    
    # TODO ...
    pass