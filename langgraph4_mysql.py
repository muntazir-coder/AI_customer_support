import os
import uuid
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        ssl_disabled=False
    )
    return connection

    return connection



def create_user(user_name, email, password):

    connection = get_connection()

    cursor = connection.cursor()


    query = """
    INSERT INTO users
    (user_name,email,password,role)
    VALUES(%s,%s,%s,%s)
    """


    cursor.execute(

        query,

        (
            user_name,
            email,
            password,
            "user"
        )

    )


    connection.commit()


    user_id = cursor.lastrowid


    cursor.close()

    connection.close()


    return user_id




def user_login(email, password):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)


    query = """
    SELECT *
    FROM users
    WHERE email=%s
    AND password=%s
    """


    cursor.execute(

        query,

        (
            email,
            password
        )

    )


    user = cursor.fetchone()


    cursor.close()

    connection.close()


    return user



def chat_start(user_id, title="New Chat"):

    connection = get_connection()

    cursor = connection.cursor()


    session_id = str(uuid.uuid4())


    query = """
    INSERT INTO conversations
    (user_id,session_id,title)
    VALUES(%s,%s,%s)
    """


    cursor.execute(

        query,

        (
            user_id,
            session_id,
            title
        )

    )


    connection.commit()


    cursor.close()

    connection.close()


    return session_id




def chat(session_id, role, message):

    connection = get_connection()

    cursor = connection.cursor()


    query = """
    INSERT INTO chat_message
    (session_id,role,message)
    VALUES(%s,%s,%s)
    """


    cursor.execute(

        query,

        (
            session_id,
            role,
            message
        )

    )


    connection.commit()


    cursor.close()

    connection.close()



def show_conversation(user_id):

    connection = get_connection()

    cursor = connection.cursor()


    query = """
    SELECT *
    FROM conversations
    WHERE user_id=%s
    ORDER BY created_at DESC
    """


    cursor.execute(

        query,

        (user_id,)

    )


    conversations = cursor.fetchall()


    cursor.close()

    connection.close()


    return conversations



def show_chat(session_id):

    connection = get_connection()

    cursor = connection.cursor()


    query = """
    SELECT role,message
    FROM chat_message
    WHERE session_id=%s
    ORDER BY created_at ASC
    """


    cursor.execute(

        query,

        (session_id,)

    )


    messages = cursor.fetchall()


    cursor.close()

    connection.close()


    return messages



def del_history(session_id):

    connection = get_connection()

    cursor = connection.cursor()


    delete_message = """
    DELETE FROM chat_message
    WHERE session_id=%s
    """


    cursor.execute(

        delete_message,

        (session_id,)

    )


    delete_conversation = """
    DELETE FROM conversations
    WHERE session_id=%s
    """


    cursor.execute(

        delete_conversation,

        (session_id,)

    )


    connection.commit()


    cursor.close()

    connection.close()



def update_conversation(session_id, title):

    connection = get_connection()

    cursor = connection.cursor()


    query = """
    UPDATE conversations
    SET title=%s
    WHERE session_id=%s
    """


    cursor.execute(

        query,

        (
            title,
            session_id
        )

    )


    connection.commit()


    cursor.close()

    connection.close()



def add_documents(document_id, document_name):

    connection = get_connection()

    cursor = connection.cursor()


    query = """
    INSERT INTO documents
    (document_id,document_name)
    VALUES(%s,%s)
    """


    cursor.execute(

        query,

        (
            document_id,
            document_name
        )

    )


    connection.commit()


    cursor.close()

    connection.close()



def delete_document(document_id):

    connection = get_connection()

    cursor = connection.cursor()


    query = """
    DELETE FROM documents
    WHERE document_id=%s
    """


    cursor.execute(

        query,

        (document_id,)

    )


    connection.commit()


    cursor.close()

    connection.close()



def get_document():

    connection = get_connection()

    cursor = connection.cursor()


    query = """
    SELECT *
    FROM documents
    ORDER BY created_at DESC
    """


    cursor.execute(query)


    documents = cursor.fetchall()


    cursor.close()

    connection.close()


    return documents
