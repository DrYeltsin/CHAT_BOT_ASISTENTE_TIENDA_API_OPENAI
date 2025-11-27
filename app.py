import streamlit as st
import openai
import os
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

from db_utils import setup_database
from ai_utils import generate_sql, run_sql_query, generate_chatbot_response
from webrtc_utils import convert_frames_to_wav

# ---------------------------------------------
# Configurar API KEY
# ---------------------------------------------
def load_api_key():
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        openai.api_key = api_key
    return api_key

load_api_key()

# ---------------------------------------------
# UI principal
# ---------------------------------------------
st.set_page_config(page_title="KRATOS — Asistente Virtual", page_icon="🤖")
st.title("🤖 KRATOS — Asistente Virtual")

st.image(
    "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
    width=130,
    caption="KRATOS — Tu asistente de catálogo"
)

# ---------------------------------------------
# Base de datos
# ---------------------------------------------
if st.button("📦 Crear Base de Datos (500 productos)"):
    setup_database()
    st.success("La base de datos fue creada correctamente.")

# ---------------------------------------------
# Historial
# ---------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("🗂️ Conversación")
for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")

# ---------------------------------------------
# Procesador de audio
# ---------------------------------------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame):
        self.frames.append(frame)
        return frame

st.subheader("🎙️ Hablar con KRATOS")

webrtc_ctx = webrtc_streamer(
    key="kratos-mic",
    mode=WebRtcMode.RECVONLY,
    audio_receiver_size=2048,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
    processor_factory=AudioProcessor
)

if webrtc_ctx and webrtc_ctx.state.playing:
    if webrtc_ctx.audio_receiver:
        frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)

        if frames:
            st.info("🎤 Procesando tu audio...")

            wav_bytes = convert_frames_to_wav(frames)

            resp = openai.Audio.transcribe(
                model="whisper-1",
                file=("audio.wav", wav_bytes)
            )

            transcript = resp["text"]
            st.success(f"🗣️ Dijiste: {transcript}")

            st.session_state.chat_history.append(("Usuario (audio)", transcript))

            sql = generate_sql(transcript)
            products = run_sql_query(sql)

            first = len(st.session_state.chat_history) == 0
            answer = generate_chatbot_response(transcript, products, first)

            st.session_state.chat_history.append(("KRATOS", answer))
            st.rerun()

# ---------------------------------------------
# Chat input
# ---------------------------------------------
st.subheader("⌨️ Escribe tu consulta")

user_query = st.chat_input("Haz tu consulta sobre el catálogo")

if user_query:
    st.session_state.chat_history.append(("Usuario", user_query))

    sql = generate_sql(user_query)
    products = run_sql_query(sql)

    first = len(st.session_state.chat_history) == 0
    answer = generate_chatbot_response(user_query, products, first)

    st.session_state.chat_history.append(("KRATOS", answer))
    st.rerun()
