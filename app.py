import streamlit as st
from openai import OpenAI
from db_utils import setup_database
from ai_utils import client, generate_sql, run_sql_query, generate_chatbot_response

# -------------------------
#     INTERFAZ STREAMLIT
# -------------------------

st.set_page_config(page_title="KRATOS — Asistente de Catálogo", page_icon="🤖")

st.title("🤖 KRATOS — Asistente de Catálogo")

st.image(
    "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
    width=130,
    caption="KRATOS — Asistente de productos"
)

# API KEY
api_key = st.text_input("🔑 Ingresa tu OpenAI API Key:", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    st.success("API Key configurada correctamente ✔️")


# CREAR BD
if st.button("📦 Crear Base de Datos (500 productos)"):
    setup_database()
    st.success("Base de datos creada exitosamente con 500 productos.")


# HISTORIAL DEL CHAT
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# CONSULTA DEL USUARIO
user_query = st.text_input("💬 Realiza una consulta sobre el catálogo:")

if st.button("Enviar"):
    if not api_key:
        st.error("Primero ingresa tu API KEY.")
    else:
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
