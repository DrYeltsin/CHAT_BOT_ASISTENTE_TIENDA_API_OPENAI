import streamlit as st
import openai
import os

from db_utils import setup_database
from ai_utils import generate_sql, run_sql_query, generate_chatbot_response

from streamlit_webrtc import webrtc_streamer
from pydub import AudioSegment
import io


# ---------------------------------------------
# CONFIGURAR OPENAI API KEY
# ---------------------------------------------
def configurar_openai():
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    if not api_key:
        return False
    openai.api_key = api_key
    return True

configurar_openai()


# ---------------------------------------------
# FUNCION: convertir audio WebRTC → WAV
# ---------------------------------------------
def convert_frames_to_wav(frames):
    audio = AudioSegment.empty()
    for frame in frames:
        audio += AudioSegment(
            frame.to_ndarray().tobytes(),
            frame.sample_rate,
            sample_width=frame.format.bytes,
            channels=frame.layout.channels
        )
    buf = io.BytesIO()
    audio.export(buf, format="wav")
    return buf.getvalue()


# ---------------------------------------------
# STREAMLIT UI
# ---------------------------------------------
st.set_page_config(page_title="KRATOS — Asistente Virtual", page_icon="🤖")
st.title("🤖 KRATOS — Asistente Virtual")

st.image(
    "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
    width=130,
    caption="KRATOS — Asistente Virtual"
)


# Crear BD
if st.button("📦 Crear Base de Datos (500 productos)"):
    setup_database()
    st.success("Base de datos creada.")


# Historial de chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------------------------------------
# CONSULTA POR TEXTO
# ---------------------------------------------
user_query = st.text_input("💬 Realiza una consulta sobre el catálogo:")

if st.button("Enviar"):
    sql = generate_sql(user_query)
    st.code(sql, language="sql")

    data = run_sql_query(sql)

    first_message = len(st.session_state.chat_history) == 0
    response = generate_chatbot_response(user_query, data, first_message)

    st.session_state.chat_history.append(("Usuario", user_query))
    st.session_state.chat_history.append(("KRATOS", response))


# ---------------------------------------------
# CONSULTA POR AUDIO (VERSIÓN LEGAL PARA STREAMLIT CLOUD)
# ---------------------------------------------
st.subheader("🎙️ Hablar con KRATOS")

webrtc_ctx = webrtc_streamer(
    key="kratos-audio",
    mode="recvonly",
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True
)

if webrtc_ctx and webrtc_ctx.state.playing:
    if webrtc_ctx.audio_receiver:
        frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        if frames:
            st.info("🎧 Procesando audio...")

            wav_bytes = convert_frames_to_wav(frames)

            # Whisper con SDK 0.28.1
            transcript_response = openai.Audio.transcribe(
                model="whisper-1",
                file=("audio.wav", wav_bytes)
            )
            transcript = transcript_response["text"]

            st.success(f"🗣️ Dijiste: {transcript}")

            st.session_state.chat_history.append(("Usuario (audio)", transcript))

            sql = generate_sql(transcript)
            data = run_sql_query(sql)

            first_message = len(st.session_state.chat_history) == 0
            answer = generate_chatbot_response(transcript, data, first_message)

            st.session_state.chat_history.append(("KRATOS", answer))

            st.rerun()


# ---------------------------------------------
# HISTORIAL
# ---------------------------------------------
st.subheader("🗂️ Conversación")
for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")
