import streamlit as st
import requests
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Carga de variables de entorno (opcional)
load_dotenv()

# Función para obtener datos del cliente mediante una API
def obtener_datos_cliente(nombre_cliente):
    url = "https://des-apps.azucarera.es/sugar/gptbot/buscar_cliente"
    headers = {
        "key": "azutoken",  # Asumiendo que 'key' es el nombre del header y 'azutoken' el nombre de la clave
        "azutoken": "QXp1Y2FyZXJhTGFWaWRhU2FiZU1lam9ySGByYXY="  # El valor del token proporcionado
    }
    payload = {"nombre_cliente": nombre_cliente}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error en la API: {response.status_code}, {response.text}")


# Configuración de la página de Streamlit
st.set_page_config(page_title="Client Info Bot", page_icon="🤖")
st.title("Client Info Bot")

# Función para obtener respuesta usando Langchain
def get_response(user_query, chat_history):
    # Obtener datos del cliente
    datos_cliente = obtener_datos_cliente(user_query)
    
    # Formatear los datos para incluirlos en el prompt
    datos_formato = f"Datos del cliente: {datos_cliente}"
    
    template = f"""
    You are a helpful assistant. Here is the customer data you requested:
    {datos_formato}

    Chat history: {chat_history}

    User question: {user_query}
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI()
        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "chat_history": chat_history,
        "user_question": user_query,
    })

# Manejo del estado de la sesión para la historia de la conversación
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Visualización de la conversación anterior
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# Entrada de usuario
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    response = get_response(user_query, st.session_state.chat_history)
    with st.chat_message("AI"):
        st.write(response)

    st.session_state.chat_history.append(AIMessage(content=response))


