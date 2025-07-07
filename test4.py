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

# Load multilingual high-quality model
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)

print("Available speakers:", tts.speakers)  # Optional
print("Languages supported:", tts.languages)  # Optional

tts.tts_to_file(
    text="こんにちは、私はりおです。元気ですか？",
    speaker="Tammie Ema",        # Or pick one from tts.speakers
    language="ja",           # Explicitly set language
    file_path="output.wav"
)