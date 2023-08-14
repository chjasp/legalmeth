import os
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chat_models import ChatOpenAI
import pinecone
import chainlit as cl
from langchain.memory import ConversationTokenBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.callbacks import get_openai_callback
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from chainlit import user_session
from prompts import load_query_gen_prompt, load_spark_prompt
from chainlit import on_message, on_chat_start
import openai
from langchain.callbacks import ContextCallbackHandler
from promptwatch import PromptWatch

from dotenv import load_dotenv

load_dotenv() 

INDEX_NAME = os.environ.get("INDEX_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = "us-west1-gcp-free"

spark = load_spark_prompt()
query_gen_prompt = load_query_gen_prompt()
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(query_gen_prompt)

pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_ENVIRONMENT
)

if __name__=="__main__":
    print("ye")

@on_chat_start
def init(): 
    # Wrapper around openai LLM
    # temperature is a hyperparameter affecting the sampling processes randomness
    # verbose: Print out the response text
    llm = ChatOpenAI(temperature=0.7, verbose=True, openai_api_key=OPENAI_API_KEY, streaming=True)
    
    # If the conversation exceeds a specified token limit, the memory prunes the earliest messages until it is within the limit
    # return_messages: If set to true, past messages are returned as a list. Otherwise as string
    # CHANGED TO 100 BECAUSE OF OPENAI ERROR
    memory = ConversationTokenBufferMemory(llm=llm, memory_key="chat_history", return_messages=True, input_key='question', max_token_limit=100)
    
    # Cohere: Turn text into embedding via API
    embeddings = CohereEmbeddings(model='embed-english-light-v2.0', cohere_api_key=COHERE_API_KEY)

    # Load Pinecone vectorstore
    docsearch = Pinecone.from_existing_index(index_name=INDEX_NAME, embedding=embeddings)
    
    # Load Pinecone retriever
    retriever = docsearch.as_retriever(search_kwargs={"k": 3})

    # Load initial message
    messages = [SystemMessagePromptTemplate.from_template(spark)]
    
    # Message that is going to be sent to the user
    messages.append(HumanMessagePromptTemplate.from_template("{question}"))
    
    # Create chat with two initial messages (?)
    prompt = ChatPromptTemplate.from_messages(messages)

    # A chain to run queries against an LLM
    question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT, verbose=True)
    
    # Contruct the document string
    doc_chain = load_qa_with_sources_chain(llm, chain_type="stuff", verbose=True, prompt=prompt)

    # Chain for conversation based on retrieved documents
    chain = ConversationalRetrievalChain(
            retriever=retriever,
            question_generator=question_generator,
            combine_docs_chain=doc_chain,
            verbose=True,
            memory=memory,
            rephrase_question=False
        )
    
    # Set user session
    cl.user_session.set("conversation_chain", chain)

@on_message
async def main(message: str):
        # Read chain from user session variable
        chain = cl.user_session.get("conversation_chain")

        # Run the chain asynchronously with an async callback
        res = await chain.arun({"question": message},callbacks=[cl.AsyncLangchainCallbackHandler()])

        # Send the answer and the text elements to the UI
        await cl.Message(content=res).send()