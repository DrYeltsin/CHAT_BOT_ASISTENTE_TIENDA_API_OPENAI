import av
import numpy as np
from pydub import AudioSegment

# Convierte frames de WebRTC a WAV (bytes)
def convert_frames_to_wav(frames):
    audio = np.concatenate([f.to_ndarray() for f in frames])
    audio_segment = AudioSegment(
        audio.tobytes(),
        frame_rate=frames[0].sample_rate,
        sample_width=frames[0].format.bytes,
        channels=frames[0].layout.channels
    )
    wav_bytes = audio_segment.export(format="wav").read()
    return wav_bytes
