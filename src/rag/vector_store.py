from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

def build_vector_store(docs, persist_path="faiss_index"):
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(persist_path)
    return db

def load_vector_store(persist_path="faiss_index"):
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(persist_path, embeddings, allow_dangerous_deserialization=True)
