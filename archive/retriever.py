import os
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import Pinecone
import data_loader, embeddings

os.environ["COHERE_API_KEY"] = "8NLTuQEM3hEQTXoRuem4is63QBy1VShvynabPAtX"

def retriever(index_name, embeddings):
    # (1) LOAD INDEX
    doc_search = Pinecone.from_existing_index(index_name, embeddings)
    
    # (2) INITIALIZE BASE RETRIEVER
    retriever = doc_search.as_retriever(search_kwargs={"k": 4})

    # (3) SET UP COHERE'S RERANKER
    compressor = CohereRerank()
    reranker = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=retriever
    )

    return 0

if __name__ == "__main__":
    index_name = "spark"
    docs_path = "../creatine_research"
    chunked_docs = data_loader.load_chunked_docs(docs_path)

    stored_embeddings = CohereEmbeddings(model='embed-english-light-v2.0')

    x = retriever(index_name, stored_embeddings)