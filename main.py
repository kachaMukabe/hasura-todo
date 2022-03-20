import streamlit as st
import os
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from dotenv import load_dotenv

load_dotenv()


def get_gql_client(extra_headers=None):
    headers = {'x-hasura-admin-secret': os.environ["HASURA_ADMIN_SECRET"] }
    if extra_headers:
        headers += extra_headers
    transport = AIOHTTPTransport(url="https://curious-sailfish-33.hasura.app/v1/graphql", headers=headers)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client

headers = {'x-hasura-admin-secret': os.environ["HASURA_ADMIN_SECRET"] }
transport = AIOHTTPTransport(url="https://curious-sailfish-33.hasura.app/v1/graphql", headers=headers)
client = Client(transport=transport, fetch_schema_from_transport=True)


def get_todos():
    query = gql(
        """
        query getTodos {
            todos {
                id
                title
                is_completed
            }
        }
        """
    )
    result = client.execute(query)
    return result["todos"]


if 'todos' not in st.session_state:
    st.session_state['todos'] = get_todos()


def create_todo(todo):
    query = gql(
        """
        mutation createTodo($title: String!, $user_id: String!) {
            insert_todos_one(object: {title: $title, user_id: $user_id }){
                id
                title
                is_completed
            }
        }
        """
    )
    params = {"title": todo, "user_id": "1"}

    result = client.execute(query, variable_values=params)
    todo = result['insert_todos_one']
    st.session_state.todos.append(todo)
    return result


def update_todo(todo):
    query = gql(
        """
        mutation updateTodo($id: Int!, $is_completed: Boolean!){
            update_todos(where: {id: {_eq: $id}}, _set: {is_completed: $is_completed}){
                affected_rows
            }
        }
        """
    )
    params = {"id": todo["id"], "is_completed": not todo["is_completed"]}

    result = client.execute(query, variable_values=params)
    return result


def delete_todo(todo):
    query = gql(
        """
        mutation deleteTodo($id: Int!){
            delete_todos(where: {id: {_eq: $id}}){
                affected_rows
            }
        }
        """
    )
    params = {"id": todo["id"]}
    result = client.execute(query, variable_values=params)
    st.session_state.todos.remove(todo)
    return result


st.title("My todos")
with st.form(key='my_form', clear_on_submit=True):
    new_todo = st.text_input("Create a todo", value="", key="d")
    submit = st.form_submit_button("Create")
    if submit:
        create_todo(new_todo)

todos = st.session_state.todos
not_done = [todo for todo in todos if not todo["is_completed"]]
completed = [todo for todo in todos if todo["is_completed"]]
st.subheader("Not Completed")
for todo in not_done:
    col1, col2 = st.columns([3, 1])
    col1.checkbox(todo["title"],key=todo["id"], value=todo["is_completed"], on_change=update_todo, args=todo)
    col2.button("Delete", key=todo["id"], on_click=delete_todo, args=(todo, ))
st.subheader("Completed")
for todo in completed:
    st.checkbox(todo["title"],key=todo["id"], value=todo["is_completed"], on_change=update_todo, kwargs={"todo": todo})
