import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def build_rag_chain(docs):
    """Build a Retrieval-Augmented Generation (RAG) chain using LangChain."""
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = splitter.split_documents(docs)

        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(splits, embeddings)
        retriever = db.as_retriever()

        # Set up the LLM for query generation
        llm = ChatOpenAI(temperature=0)

        # Set up the QA chain
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        return qa

    except Exception as e:
        logger.error(f"Error in building RAG chain: {e}")
        return None

def main():
    """Main function to run the RAG-based document query."""
    try:
        # Load the document
        loader = TextLoader("data/sample.txt")
        docs = loader.load()

        # Build the RAG chain
        qa = build_rag_chain(docs)
        if qa is None:
            logger.error("Failed to build RAG chain.")
            return

        # Query the document
        query = "What is this document about?"
        result = qa.run(query)

        # Print the result
        print(result)

    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
