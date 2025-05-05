import asyncio
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Load Chroma vectorstore from disk
vectorstore = Chroma(persist_directory="chroma_index", embedding_function=embeddings)

async def get_relevant_context(query: str, k: int = 3) -> str:
    # Chroma's similarity_search function is synchronous, so we use asyncio.to_thread to run it in a separate thread
    docs = await asyncio.to_thread(vectorstore.similarity_search, query, k)
    
    return "\n\n".join([doc.page_content for doc in docs]) if docs else ""
