from langchain.vectorstores.base import VectorStore

def get_retriever(store: VectorStore, k: int = 3):
    return store.as_retriever(search_kwargs={"k": k})
