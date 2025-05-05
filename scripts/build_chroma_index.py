import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Example documents – replace with your actual support knowledge base
docs = [
    Document(page_content="If a user has issues logging in, ask them to reset their password."),
    Document(page_content="We do not offer refunds after 30 days."),
    Document(page_content="To request feature enhancements, email support with the subject 'Feature Request'."),
    Document(page_content="Technical issues are usually resolved within 48 hours."),
]

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Create and persist Chroma index
vectorstore = Chroma.from_documents(docs, embedding=embeddings, persist_directory="chroma_index")
vectorstore.persist()

print("✅ Chroma index built and saved to 'chroma_index'")
