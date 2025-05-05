from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


def build_rag_chain(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(splits, embeddings)
    retriever = db.as_retriever()

    llm = ChatOpenAI(temperature=0)
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa


if __name__ == "__main__":
    loader = TextLoader("data/sample.txt")
    docs = loader.load()
    qa = build_rag_chain(docs)
    query = "What is this document about?"
    result = qa.run(query)
    print(result)
