import os
import uuid

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from langgraph.graph import StateGraph, START, END

from typing import TypedDict
from langchain_core.documents import Document


load_dotenv()


llm = ChatGroq(

    model="llama-3.3-70b-versatile",

    temperature=0,

    api_key=os.getenv("GROQ_API_KEY")

)

embedding = HuggingFaceEmbeddings(

    model_name="sentence-transformers/all-MiniLM-L6-v2"

)


vector_store = Chroma(

    collection_name="customer_support_document",

    embedding_function=embedding,

    persist_directory="chroma_db"

)



retriever = vector_store.as_retriever(

    search_kwargs={
        "k":5
    }

)




def process_pdf(file_path):


    loader = PyPDFLoader(file_path)


    documents = loader.load()



    splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,

        chunk_overlap=50

    )


    chunks = splitter.split_documents(documents)



    document_id = str(uuid.uuid4())



    for chunk in chunks:

        chunk.metadata["document_id"] = document_id



    vector_store.add_documents(chunks)



    return document_id




def del_vs(document_id):


    vector_store.delete(

        where={
            "document_id":document_id
        }

    )



class ChatState(TypedDict):

    session_id:str

    question:str

    documents:list[Document]

    answer:str


def retrieve_node(state:ChatState):


    documents = retriever.invoke(

        state["question"]

    )


    return {

        "documents":documents

    }



def answer_node(state:ChatState):


    context = "\n\n".join(

        doc.page_content

        for doc in state["documents"]

    )



    prompt = f"""

You are an AI Customer Support Assistant.

Answer only from the company documents.

Rules:

1. Do not create information.

2. Use only provided context.

3. If answer is not available,
say "I don't know."


Company Documents:

{context}


Customer Question:

{state["question"]}

"""



    response = llm.invoke(prompt)



    return {

        "answer":response.content

    }


builder = StateGraph(ChatState)



builder.add_node(

    "retrieve",

    retrieve_node

)



builder.add_node(

    "answer",

    answer_node

)



builder.add_edge(

    START,

    "retrieve"

)



builder.add_edge(

    "retrieve",

    "answer"

)



builder.add_edge(

    "answer",

    END

)

graph = builder.compile()