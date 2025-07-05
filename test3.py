from TTS.api import TTS
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"


import torch
from torch.serialization import add_safe_globals

# Add all classes that cause UnpicklingError
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

# Allow them explicitly
add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])

# Load XTTS v2 model
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# Generate speech to a file
tts.tts_to_file(
    text="こんにちは、元気ですか？",            # Japanese input
    speaker_wav=r"C:\Users\Rioss\Downloads\jp_001.mp3.wav",                 # Path to your voice sample (must be WAV, ~3+ seconds)
    language="ja",                             # Japanese language code
    file_path="output.wav"                     # Output file
)
