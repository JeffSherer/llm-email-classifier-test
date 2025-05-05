from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

def build_rag_chain(retriever):
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")
