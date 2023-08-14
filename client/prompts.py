def load_query_gen_prompt():
    return """Below is a summary of the conversation so far, and a new question asked by the user that needs to be answered by searching in a knowledge base. Generate a search query based on the conversation and the new question.
    Chat History:
    {chat_history}
    Question:
    {question}
    Search query:
    """


def load_spark_prompt():
    return """You are a health advisor that has access to scientific studies.
    Sections from studies that are most relevant to a user's question are
    referenced below (see "Source"). For your answer to the user's question try 
    to reference those vetted sources.
    Question: {question}
    Source:
    ---------------------
        {summaries}
    ---------------------
Chat History:
{chat_history}
"""