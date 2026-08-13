from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil

from langgraph4_rag import (
    graph,
    process_pdf,
    del_vs
)

from langgraph4_mysql import (
    create_user,
    user_login,
    chat_start,
    chat,
    show_chat,
    show_conversation,
    del_history,
    add_documents,
    delete_document,
    get_document
)


app = FastAPI(title="AI Document Assistant API")

@app.get("/")
def home():
    return {
        "message": "AI Customer Support API is running",
        "status": "online"
    }

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)



class SignupRequest(BaseModel):

    user_name:str

    email:str

    password:str


class LoginRequest(BaseModel):

    email:str

    password:str


class ChatStartRequest(BaseModel):

    user_id:int

    title:str="New Chat"





class ChatRequest(BaseModel):

    question:str

    session_id:str


@app.post("/signup")
def signup(data:SignupRequest):


    user_id = create_user(

        data.user_name,

        data.email,

        data.password

    )


    return {

        "message":"Account created successfully",

        "user_id":user_id

    }



@app.post("/login")
def login(data:LoginRequest):


    user = user_login(

        data.email,

        data.password

    )



    if user:


        return {

            "message":"Login successful",

            "user_id":user["user_id"],

            "user_name":user["user_name"],

            "role":user["role"]

        }



    return {

        "message":"Invalid email or password"

    }





@app.post("/chat/start")
def start_chat(data:ChatStartRequest):


    session_id = chat_start(

        data.user_id,

        data.title

    )


    return {

        "session_id":session_id

    }




@app.post("/chat")
def ask_ai(data:ChatRequest):


    result = graph.invoke(

        {

            "session_id":data.session_id,

            "question":data.question,

            "documents":[],

            "answer":""

        }

    )



    answer = result["answer"]





    chat(

        data.session_id,

        "user",

        data.question

    )





    chat(

        data.session_id,

        "assistant",

        answer

    )



    return {


        "answer":answer

    }


@app.get("/chat/sessions/{user_id}")
def get_sessions(user_id:int):


    sessions = show_conversation(

        user_id

    )


    return sessions



@app.get("/chat/history/{session_id}")
def get_history(session_id:str):


    messages = show_chat(

        session_id

    )



    history = []



    for role, message in messages:



        history.append(

            {

                "role":role,

                "content":message

            }

        )



    return history




@app.delete("/chat/session/{session_id}")
def delete_chat(session_id:str):


    del_history(

        session_id

    )


    return {


        "message":"Chat deleted successfully"

    }



@app.post("/admin/upload")
def upload_document(
    file: UploadFile = File(...)
):


    os.makedirs(

        "uploads",

        exist_ok=True

    )



    file_path = f"uploads/{file.filename}"



    with open(

        file_path,

        "wb"

    ) as buffer:



        shutil.copyfileobj(

            file.file,

            buffer

        )




    document_id = process_pdf(

        file_path

    )




    add_documents(

        document_id,

        file.filename

    )



    return {


        "message":"Document uploaded successfully",

        "document_id":document_id

    }






@app.get("/admin/documents")
def documents():


    return get_document()




@app.delete("/admin/delete/{document_id}")
def remove_document(document_id:str):



    del_vs(

        document_id

    )




    delete_document(

        document_id

    )



    return {


        "message":"Document deleted successfully"

    }
