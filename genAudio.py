import os
from dotenv import load_dotenv

load_dotenv()
TTS_API_KEY = os.getenv("gemeniKey", "")

import wave
import re
import subprocess
from pydub import AudioSegment

def split_text_smart(text, max_len=100):
    sentences = re.split(r'(?<=[。、「」！？])', text)
    chunks = []
    current = ''

    for sentence in sentences:
        if len(current) + len(sentence) <= max_len:
            current += sentence
        else:
            if current:
                chunks.append(current.strip())
            if len(sentence) > max_len:
                # Fallback: force-break long sentence
                parts = [sentence[i:i+max_len] for i in range(0, len(sentence), max_len)]
                chunks.extend(part.strip() for part in parts)
                current = ''
            else:
                current = sentence
    if current:
        chunks.append(current.strip())
    
    return chunks

def change_speed(sound, speed=1.0):
    altered_frame_rate = int(sound.frame_rate * speed)
    return sound._spawn(sound.raw_data, overrides={'frame_rate': altered_frame_rate}).set_frame_rate(sound.frame_rate)


def genAUDIO(context,output):
    genTiktok(context,output)

<<<<<<< HEAD
def genTiktok(context,output):
    chunk = split_text_smart(context)
    #print(chunk)
    combined = AudioSegment.empty()
    cleanUp = []
    for i,context in enumerate(chunk):  
=======

def genAUDIO(context,num):
    google= False
    if google:
        genWGoogle(context,num)
    else:
        genLib(context,num)

def genLib(context,num):
    from melo.api import TTS

    # Speed is adjustable
    speed = 1.2
    device = 'cpu' # or cuda:0

    text = context

    client = genai.Client(api_key=TTS_API_KEY)
    model = TTS(language='JP', device=device)
    speaker_ids = model.hps.data.spk2id

    output_path = f'media/audio-{num}.wav'
    model.tts_to_file(text, speaker_ids['JP'], output_path, speed=speed)

def genWGoogle(context,num):

    @contextlib.contextmanager
    def wave_file(filename, channels=1, rate=24000, sample_width=2):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            yield wf

    def play_audio_blob(blob):
        fname = f'media/audio-{num}.wav'
        with wave_file(fname) as wav:
            wav.writeframes(blob.data)

        return Audio(fname, autoplay=True)

    def play_audio(response):
        return play_audio_blob(response.candidates[0].content.parts[0].inline_data)

    client = genai.Client(api_key=TTS_API_KEY)

    MODEL_ID="gemini-2.5-flash-preview-tts"
    voice_name = "kore" # @param ["Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede", "Callirhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba", "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar", "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi", "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafar"]
    #https://ai.google.dev/gemini-api/docs/speech-generation#voices

    response = client.models.generate_content(
    model=MODEL_ID,
    contents=context,
    config={
        "response_modalities": ['Audio'],
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {
                    "voice_name": voice_name
                }
            }
        }
    },
    )

    play_audio(response)
>>>>>>> ba30b9d9baa7a07152c5361186d1d5364c81d0d4
        
        # Path to your JavaScript file
        js_file_path = r"C:\Users\Rioss\Desktop\Code\videoAI\index.js"
        # Parameters to pass to the JavaScript file
        params = [output+str(i),context]

        # Run the JavaScript file with parameters using Node.js
        node_path = r"C:\Program Files\nodejs\node.exe"

        result = subprocess.run([node_path, js_file_path] + params, check=True,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
        
        combined += AudioSegment.from_mp3(output+str(i)+'.mp3')
        cleanUp.append(output+str(i)+'.mp3')

        #print(result.stdout)
        #print(result.stderr)
    
    combined = change_speed(combined, 1.25)
    combined.export(output, format="mp3")
    for file_path in cleanUp:
        os.remove(file_path)
    print(output)



if __name__ == '__main__':
<<<<<<< HEAD
    genAUDIO("皆さん、こんにちは！「知の探求」へようこそ。このチャンネルでは、私たちの世界の見方、考え方。", "media/test.mp3")
=======
    genAUDIO("彼は毎朝ジョギングgoogleをして体を健康に保っています。",99)
>>>>>>> ba30b9d9baa7a07152c5361186d1d5364c81d0d4
