import sys
sys.path.append("/home/riosshin/code/videoAI")

from TTS.api import TTS

# List available models
print(TTS().list_models())