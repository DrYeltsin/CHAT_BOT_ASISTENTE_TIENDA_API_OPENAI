import streamlit as st
from openai import OpenAI
import os
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
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

    # Streamlit Cloud requiere que la API key esté en variable de entorno
    os.environ["OPENAI_API_KEY"] = api_key

    return OpenAI()  # sin parámetros → compatibilidad garantizada

client = get_client()

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="KRATOS — Asistente Virtual", page_icon="🤖")
st.title("🤖 KRATOS — Asistente Virtual")

st.image(
    "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
    width=130,
    caption="KRATOS — Tu asistente de catálogo"
)

# ---------------------------
# BOTÓN CREAR BDD
# ---------------------------
if st.button("📦 Crear Base de Datos (500 productos)"):
    setup_database()
    st.success("La base de datos fue creada exitosamente con 500 productos.")


# ---------------------------
# HISTORIAL DEL CHAT
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


st.subheader("🗂️ Conversación")
for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")


# ---------------------------
# PROCESADOR DE AUDIO
# ---------------------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame):
        self.frames.append(frame)
        return frame


st.subheader("🎙️ Habla con KRATOS (Micrófono)")


# ---------------------------
# COMPONENTE WEBRTC (CORREGIDO)
# ---------------------------
webrtc_ctx = webrtc_streamer(
    key="speech-to-text-kratos",
    mode=WebRtcMode.RECVONLY,           # ← FIX IMPORTANTE
    audio_receiver_size=2048,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
    processor_factory=AudioProcessor
)

# ---------------------------
# PROCESAR AUDIO RECIBIDO
# ---------------------------
if webrtc_ctx and webrtc_ctx.state.playing:
    if webrtc_ctx.audio_receiver:
        frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)

        if frames:
            st.info("🎤 Procesando tu audio...")

            wav_audio = convert_frames_to_wav(frames)

            # Transcripción con OpenAI
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=("kratos_audio.wav", wav_audio)
            ).text

            st.success(f"🗣️ Dijiste: {transcript}")

            # Guardar historial
            st.session_state.chat_history.append(("Usuario (audio)", transcript))

            # SQL basado en la transcripción
            sql_query = generate_sql(client, transcript)
            products = run_sql_query(sql_query)

            # Respuesta del bot
            first_msg = len(st.session_state.chat_history) == 0
            answer = generate_chatbot_response(client, transcript, products, first_msg)

            st.session_state.chat_history.append(("KRATOS", answer))
            st.rerun()


# ---------------------------
# INPUT DE TEXTO
# ---------------------------
st.subheader("⌨️ Escribe tu consulta")

user_text = st.chat_input("Haz tu consulta sobre el catálogo")

if user_text:
    st.session_state.chat_history.append(("Usuario", user_text))

    sql = generate_sql(client, user_text)
    products = run_sql_query(sql)

    first_msg = len(st.session_state.chat_history) == 0
    answer = generate_chatbot_response(client, user_text, products, first_msg)

    st.session_state.chat_history.append(("KRATOS", answer))
    st.rerun()
