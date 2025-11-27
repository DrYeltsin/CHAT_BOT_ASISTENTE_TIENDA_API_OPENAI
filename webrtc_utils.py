import av
import numpy as np
from pydub import AudioSegment

def convert_frames_to_wav(frames):
    audio = np.concatenate([f.to_ndarray() for f in frames])
    
    audio_segment = AudioSegment(
        audio.tobytes(),
        frame_rate=frames[0].sample_rate,
        sample_width=frames[0].format.bytes,
        channels=frames[0].layout.channels
    )
    
    return audio_segment.export(format="wav").read()
