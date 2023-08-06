from langchain.vectorstores import Pinecone
import pinecone
from langchain.embeddings import CohereEmbeddings
import data_loader

def create_and_store_embeddings(chunked_docs):
    # (1) CREATE EMBEDDINGS
    cohere_api_key = "8NLTuQEM3hEQTXoRuem4is63QBy1VShvynabPAtX"
    embeddings = CohereEmbeddings(model='embed-english-light-v2.0',cohere_api_key=cohere_api_key)

    # (2) CREATE VECTOR DATABASE
    pinecone_api_key = "fb34b8b4-740d-4efa-8ab4-759561788dad"
    index_name = "spark"

    pinecone.init(api_key=pinecone_api_key, environment='us-west1-gcp-free')
    doc_search = Pinecone.from_documents(chunked_docs, embeddings, index_name=index_name)

    return embeddings, doc_search

if __name__ == "__main__":
    path = ("../creatine_research")
    chunked_docs = data_loader.load_chunked_docs(path)

    e, ds = create_and_store_embeddings(chunked_docs)

    print(e)
    print(ds)