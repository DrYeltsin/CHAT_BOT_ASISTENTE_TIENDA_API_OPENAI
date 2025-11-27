import streamlit as st
from openai import OpenAI
import os
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
from webrtc_utils import convert_frames_to_wav

from db_utils import setup_database
from ai_utils import generate_sql, run_sql_query, generate_chatbot_response

# ---------------------------
# CONFIG CLIENTE OPENAI
# ---------------------------
def get_client():
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

client = get_client()

# ---------------------------
# STREAMLIT
# ---------------------------
st.set_page_config(page_title="KRATOS — Asistente Virtual", page_icon="🤖")
st.title("🤖 KRATOS — Asistente Virtual")

st.image(
    "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
    width=130,
    caption="KRATOS — Asistente Virtual"
)

# ---------------------------
# BOTÓN BDD
# ---------------------------
if st.button("📦 Crear Base de Datos (500 productos)"):
    setup_database()
    st.success("Base de datos creada exitosamente con 500 productos.")


# ---------------------------------------------------
# HISTORIAL DEL CHAT
# ---------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------------------------------------------
# MOSTRAR HISTORIAL
# ---------------------------------------------------
st.subheader("📁 Conversación")
for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")


# ---------------------------------------------------
# PROCESADOR DE AUDIO (STREAMLIT-WEBRTC)
# ---------------------------------------------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame):
        self.frames.append(frame)
        return frame


st.subheader("🎙️ Puedes hablarle a KRATOS")

webrtc_ctx = webrtc_streamer(
    key="speech-to-text-kratos",
    mode="receive",
    audio_receiver_size=2048,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)


# ---------------------------------------------------
# PROCESAR AUDIO GRABADO
# ---------------------------------------------------
if webrtc_ctx and webrtc_ctx.state.playing:
    if webrtc_ctx.audio_receiver:
        frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        if frames:
            wav_audio = convert_frames_to_wav(frames)

            st.info("🎤 Procesando audio...")

            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=("audio.wav", wav_audio)
            ).text

            st.success(f"🗣️ Dijiste: {transcript}")

            # Guardar en historial
            st.session_state.chat_history.append(("Usuario (audio)", transcript))

            # Ejecutar consulta SQL
            sql_query = generate_sql(client, transcript)
            products = run_sql_query(sql_query)

            # Generar respuesta KRATOS
            first_msg = len(st.session_state.chat_history) == 0
            answer = generate_chatbot_response(client, transcript, products, first_msg)

            st.session_state.chat_history.append(("KRATOS", answer))
            st.rerun()


# ---------------------------------------------------
# INPUT DE TEXTO
# ---------------------------------------------------
st.subheader("⌨️ O escríbele a KRATOS")

user_text = st.chat_input("Escribe tu consulta y presiona ENTER")

if user_text:
    st.session_state.chat_history.append(("Usuario", user_text))

    sql = generate_sql(client, user_text)
    products = run_sql_query(sql)

    first_msg = len(st.session_state.chat_history) == 0
    answer = generate_chatbot_response(client, user_text, products, first_msg)

    st.session_state.chat_history.append(("KRATOS", answer))
    st.rerun()
