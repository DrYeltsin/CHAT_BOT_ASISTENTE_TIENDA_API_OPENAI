import streamlit as st
from openai import OpenAI
import os

from db_utils import setup_database
from ai_utils import generate_sql, run_sql_query, generate_chatbot_response


# ---------------------------------------
# CLIENTE OPENAI SEGURO
# ---------------------------------------

def get_client():
    # Streamlit Cloud → usa secrets
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        return OpenAI()   # SDK nuevo → sin parámetros

    # Local (variable de entorno)
    if os.getenv("OPENAI_API_KEY"):
        return OpenAI()

    return None


client = get_client()


# ---------------------------------------
# UI
# ---------------------------------------

st.set_page_config(page_title="KRATOS — Asistente de Tienda", page_icon="🤖")
st.title("🤖 KRATOS — Asistente Virtual")

st.image(
    "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
    width=130,
    caption="KRATOS — Asistente Virtual"
)


# ---------------------------------------
# BOTÓN PARA CREAR BD
# ---------------------------------------

if st.button("📦 Crear Base de Datos (500 productos)"):
    setup_database()
    st.success("Base de datos creada exitosamente con 500 productos.")


# ---------------------------------------
# HISTORIAL DEL CHAT
# ---------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("🗂️ Conversación")
for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")


# ---------------------------------------
# INPUT: TEXTO + VOZ (Speech-to-Text)
# ---------------------------------------

st.write("### 🎤 Puedes escribir o hablarle a KRATOS")

col1, col2 = st.columns([2, 1])

# 📌 Entrada por texto
with col1:
    user_query = st.chat_input("Escribe tu consulta y presiona ENTER:")

# 📌 Entrada por voz (audio)
with col2:
    audio_file = st.file_uploader(
        "Habla con KRATOS (wav/mp3/m4a)",
        type=["wav", "mp3", "m4a"],
        accept_multiple_files=False
    )

    audio_transcribed = None

    if audio_file is not None:
        st.audio(audio_file)

        with st.spinner("🎧 Transcribiendo tu voz..."):
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file
            )
            audio_transcribed = transcript.text

        st.success("✔️ Tu voz fue convertida a texto")
        st.write(f"🗣️ **Dijiste:** {audio_transcribed}")

        user_query = audio_transcribed


# ---------------------------------------
# PROCESAR CONSULTA
# ---------------------------------------

if user_query:
    if client is None:
        st.error("❌ No se ha configurado la API Key de OpenAI.")
    else:
        sql = generate_sql(client, user_query)
        st.code(sql, language="sql")

        data = run_sql_query(sql)

        first_message = len(st.session_state.chat_history) == 0

        response = generate_chatbot_response(
            client,
            user_query,
            data,
            first_message
        )

        st.session_state.chat_history.append(("Usuario", user_query))
        st.session_state.chat_history.append(("KRATOS", response))

        st.rerun()
