import streamlit as st
from openai import OpenAI
import os

from db_utils import setup_database
from ai_utils import client, generate_sql, run_sql_query, generate_chatbot_response


# ---------------------------
# CLIENTE OPENAI SEGURO
# ---------------------------

def get_client():
    # Streamlit Cloud → usa secrets
    if "OPENAI_API_KEY" in st.secrets:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # Local
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = get_client()


# ---------------------------
# UI
# ---------------------------

st.set_page_config(page_title="KRATOS — Asistente de Tienda", page_icon="🤖")
st.title("🤖 KRATOS — Asistente de Virtual")

st.image(
    "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
    width=130,
    caption="KRATOS — Asistente de Virtual"
)


# CREAR BD
if st.button("📦 Crear Base de Datos (500 productos)"):
    setup_database()
    st.success("Base de datos creada exitosamente con 500 productos.")


# HISTORIAL
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# CONSULTA
user_query = st.text_input("💬 Realiza una consulta sobre el catálogo:")

if st.button("Enviar"):
    sql = generate_sql(user_query)
    st.code(sql, language="sql")

    data = run_sql_query(sql)

    first_message = len(st.session_state.chat_history) == 0

    response = generate_chatbot_response(
        user_query,
        data,
        first_message=first_message
    )

    st.session_state.chat_history.append(("Usuario", user_query))
    st.session_state.chat_history.append(("KRATOS", response))


# MOSTRAR HISTORIAL
st.subheader("🗂️ Conversación")
for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")
