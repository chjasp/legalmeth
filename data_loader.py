from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import TokenTextSplitter
import tiktoken

def load_chunked_docs(path: str):
    """Load docs from a directory and chunk them"""
    loader = PyPDFDirectoryLoader(path)
    text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=25)
    chunked_docs = loader.load_and_split(text_splitter)
    return chunked_docs

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

if __name__ == "__main__":
    path = "../creatine_research"
    chunked_docs = load_chunked_docs(path)
    print(chunked_docs)