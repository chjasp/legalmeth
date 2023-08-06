from langchain.document_loaders import PyPDFLoader

file_path = "../creatine_research/nutrients-14-00921.pdf"

loader = PyPDFLoader(file_path)
pages = loader.load_and_split()

if __name__ == "__main__":
    print(pages[0])