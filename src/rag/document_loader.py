from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

def load_and_split(path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    loader = TextLoader(path)
    documents = loader.load()
    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)
