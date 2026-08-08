import streamlit as st
import requests
import time


API_URL = "http://127.0.0.1:8000"


st.set_page_config(

    page_title="AI Document Assistant",

    page_icon="🤖",

    layout="wide"

)


default_state = {

    "logged_in": False,

    "signup_mode": False,

    "user_id": None,

    "username": "",

    "role": "user",

    "session_id": None,

    "messages": []

}



for key,value in default_state.items():

    if key not in st.session_state:

        st.session_state[key] = value



st.markdown(

"""
<h1 style="text-align:center;">
🤖 AI Document Assistant
</h1>
""",

unsafe_allow_html=True

)



if not st.session_state.logged_in:



    left,center,right = st.columns([1,2,1]) 
    with center:



        st.container()



        if st.session_state.signup_mode:



            st.subheader(

                "Create Account"

            )



            name = st.text_input(

                "Username"

            )



            email = st.text_input(

                "Email"

            )



            password = st.text_input(

                "Password",

                type="password"

            )





            if st.button(

                "Signup",

                use_container_width=True

            ):



                status = st.empty()



                try:



                    status.info(

                        "Creating account..."

                    )


                    time.sleep(0.5)



                    status.info(

                        "Saving user data..."

                    )



                    response = requests.post(

                        f"{API_URL}/signup",

                        json={

                            "user_name":name,

                            "email":email,

                            "password":password

                        }

                    )



                    if response.status_code == 200:



                        status.success(

                            "Account created successfully"

                        )


                        time.sleep(1)



                        st.session_state.signup_mode=False


                        st.rerun()



                    else:



                        st.error(

                            "Signup failed"

                        )



                except Exception:



                    st.error(

                        "FastAPI server is not running"

                    )





            if st.button(

                "Already have account? Login",

                use_container_width=True

            ):



                st.session_state.signup_mode=False

                st.rerun()







        else:



            st.subheader(

                "Login"

            )



            email = st.text_input(

                "Email"

            )


            password = st.text_input(

                "Password",

                type="password"

            )





            if st.button(

                "Login",

                use_container_width=True

            ):



                status = st.empty()



                try:



                    status.info(

                        "Checking credentials..."

                    )



                    response = requests.post(

                        f"{API_URL}/login",

                        json={

                            "email":email,

                            "password":password

                        }

                    )



                    if response.status_code == 200:



                        data = response.json()



                        if "user_id" in data:



                            status.info(

                                "Loading profile..."

                            )



                            time.sleep(0.5)



                            st.session_state.user_id = data["user_id"]


                            st.session_state.username = data["user_name"]


                            st.session_state.role = data["role"]


                            st.session_state.logged_in=True


                            st.session_state.messages=[]


                            status.success(

                                "Login successful"

                            )



                            time.sleep(1)


                            st.rerun()



                        else:



                            st.error(

                                "Invalid email or password"

                            )



                    else:



                        st.error(

                            "Login failed"

                        )



                except Exception:



                    st.error(

                        "FastAPI server is not running"

                    )







            if st.button(

                "Create new account",

                use_container_width=True

            ):



                st.session_state.signup_mode=True


                st.rerun()





    st.stop()




with st.sidebar:


    st.title("🤖 AI Assistant")


    st.write(
        f"👤 {st.session_state.username}"
    )


    st.write(
        f"Role: {st.session_state.role}"
    )


    st.divider()


    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):


        try:


            response = requests.post(

                f"{API_URL}/chat/start",

                json={

                    "user_id": st.session_state.user_id,

                    "title": "New Chat"

                }

            )



            if response.status_code == 200:


                st.session_state.session_id = (

                    response.json()["session_id"]

                )


                st.session_state.messages = []


                st.rerun()



            else:


                st.error(
                    "Cannot create chat"
                )


        except Exception:


            st.error(
                "FastAPI connection error"
            )




    st.divider()



    st.subheader(
        "💬 Chat Sessions"
    )



    try:



        response = requests.get(

            f"{API_URL}/chat/sessions/{st.session_state.user_id}"

        )



        if response.status_code == 200:



            sessions = response.json()



            if sessions:



                for session in sessions:



                    database_id = session[0]

                    session_id = session[2]

                    title = session[3]



                    col1,col2 = st.columns(

                        [5,1]

                    )



                    with col1:



                        if st.button(

                            title,

                            key=f"open_{database_id}",

                            use_container_width=True

                        ):



                            history_response = requests.get(

                                f"{API_URL}/chat/history/{session_id}"

                            )



                            if history_response.status_code == 200:



                                st.session_state.messages = (

                                    history_response.json()

                                )


                                st.session_state.session_id = (

                                    session_id

                                )


                                st.rerun()





                    with col2:



                        if st.button(

                            "🗑",

                            key=f"delete_{database_id}"

                        ):



                            delete_response = requests.delete(

                                f"{API_URL}/chat/session/{session_id}"

                            )



                            if delete_response.status_code == 200:



                                if st.session_state.session_id == session_id:



                                    st.session_state.session_id = None


                                    st.session_state.messages = []



                                st.success(

                                    "Deleted"

                                )


                                time.sleep(0.5)


                                st.rerun()



            else:



                st.info(

                    "No chat sessions"

                )



        else:



            st.error(

                "Cannot load sessions"

            )



    except Exception:



        st.error(

            "FastAPI connection error"

        )




    st.divider()



    if st.button(

        "Logout",

        use_container_width=True

    ):



        st.session_state.clear()

        st.rerun()



st.title("💬 Chat")




for message in st.session_state.messages:



    with st.chat_message(

        message["role"]

    ):



        st.write(

            message["content"]

        )







question = st.chat_input(

    "Ask your question..."

)



if question:



    if st.session_state.session_id is None:



        with st.spinner(

            "Creating chat session..."

        ):



            session_response = requests.post(

                f"{API_URL}/chat/start",

                json={

                    "user_id":st.session_state.user_id,

                    "title": question[:40]

                }

            )



            if session_response.status_code == 200:



                st.session_state.session_id = (

                    session_response.json()["session_id"]

                )



            else:



                st.error(

                    "Cannot create session"

                )



                st.stop()







    st.session_state.messages.append(

        {

            "role":"user",

            "content":question

        }

    )



    with st.chat_message(

        "user"

    ):



        st.write(

            question

        )








    status = st.empty()



    try:



        status.info(

            "🔍 Searching documents..."

        )


        time.sleep(0.5)



        status.info(

            "📄 Processing context..."

        )


        time.sleep(0.5)



        status.info(

            "🤖 Generating answer..."

        )





        response = requests.post(

            f"{API_URL}/chat",

            json={

                "question":question,

                "session_id":

                    st.session_state.session_id

            }

        )





        if response.status_code == 200:



            answer = response.json().get(

                "answer",

                "I don't know."

            )



            status.success(

                "Answer generated"

            )



            time.sleep(0.5)



            status.empty()





            st.session_state.messages.append(

                {

                    "role":"assistant",

                    "content":answer

                }

            )



            with st.chat_message(

                "assistant"

            ):



                st.write(

                    answer

                )



        else:



            status.error(

                "AI response failed"

            )



    except Exception as e:



        status.error(

            "FastAPI connection error"

        )



if st.session_state.role == "admin":



    st.sidebar.divider()

    st.sidebar.title(

        "⚙️ Admin Panel"

    )



    st.title(

        "📚 Document Management"

    )



    st.write(

        "Upload PDF documents for AI knowledge base"

    )



    st.divider()







    uploaded_file = st.file_uploader(

        "Choose PDF file",

        type=["pdf"]

    )





    if uploaded_file:



        if st.button(

            "Upload Document",

            use_container_width=True

        ):



            status = st.empty()



            try:



                status.info(

                    "📤 Uploading file..."

                )


                time.sleep(0.5)



                status.info(

                    "📄 Extracting text..."

                )


                time.sleep(0.5)



                status.info(

                    "🧠 Creating embeddings..."

                )


                time.sleep(0.5)



                response = requests.post(

                    f"{API_URL}/admin/upload",

                    files={

                        "file":(

                            uploaded_file.name,

                            uploaded_file,

                            "application/pdf"

                        )

                    }

                )



                if response.status_code == 200:



                    status.info(

                        "💾 Updating knowledge base..."

                    )


                    time.sleep(1)



                    status.success(

                        "Document uploaded successfully"

                    )


                    time.sleep(1)


                    st.rerun()



                else:



                    status.error(

                        "Upload failed"

                    )



            except Exception:



                status.error(

                    "FastAPI connection error"

                )








    st.divider()







    st.subheader(

        "📄 Uploaded Documents"

    )



    try:



        response = requests.get(

            f"{API_URL}/admin/documents"

        )



        if response.status_code == 200:



            documents = response.json()



            if documents:



                for doc in documents:




                    database_id = doc[0]

                    document_id = doc[1]

                    document_name = doc[2]



                    col1,col2 = st.columns(

                        [5,1]

                    )



                    with col1:



                        st.write(

                            "📄",

                            document_name

                        )



                    with col2:



                        if st.button(

                            "🗑",

                            key=f"delete_doc_{database_id}"

                        ):



                            delete_response = requests.delete(

                                f"{API_URL}/admin/delete/{document_id}"

                            )



                            if delete_response.status_code == 200:



                                st.success(

                                    "Document deleted"

                                )


                                time.sleep(0.5)


                                st.rerun()



            else:



                st.info(

                    "No documents found"

                )



        else:



            st.error(

                "Cannot load documents"

            )



    except Exception:



        st.error(

            "FastAPI connection error"

        )
                            