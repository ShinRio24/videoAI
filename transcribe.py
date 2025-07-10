import subprocess
from funasr import AutoModel
import os
import whisper
from llmPrompt import prompt
import re
import json


import yt_dlp

def download_youtube_video(url, output_path='downloads/%(title)s.%(ext)s'):
    ydl_opts = {
        'outtmpl': output_path,  # Customize output folder and file name
        'format': 'best',        # Downloads the best quality
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

#from sakana AI AI Scientist
def extract_json_between_markers(llm_output):
    # Regular expression pattern to find JSON content between ```json and ```
    json_pattern = r"```json(.*?)```"
    matches = re.findall(json_pattern, llm_output, re.DOTALL)

    if not matches:
        # Fallback: Try to find any JSON-like content in the output
        json_pattern = r"\{.*?\}"
        matches = re.findall(json_pattern, llm_output, re.DOTALL)

    for json_string in matches:
        json_string = json_string.strip()
        try:
            parsed_json = json.loads(json_string)
            return parsed_json
        except json.JSONDecodeError:
            # Attempt to fix common JSON issues
            try:
                # Remove invalid control characters
                json_string_clean = re.sub(r"[\x00-\x1F\x7F]", "", json_string)
                parsed_json = json.loads(json_string_clean)
                return parsed_json
            except json.JSONDecodeError:
                continue  # Try next match

    return None 


def extract_audio(video_path: str, wav_path: str = "audio.wav"):
    """
    Extracts 16 kHz mono WAV audio from a video file using ffmpeg.
    """
    subprocess.run(
        ["ffmpeg", "-i", video_path, "-ar", "16000", "-ac", "1", wav_path],
        check=True
    )

def transcribe_with_speakers(wav_path: str):
    #large takes much longer but more accurate
    model = whisper.load_model("base") 
    #model = whisper.load_model("large") 
    result = model.transcribe(wav_path)
    return result

def findSeg(fullTranscript,video_file):
    inp = f"""
    You're an expert YouTube Shorts editor. Your job is to extract 3–5 engaging, entertaining, shocking, or motivating *sequences* from a transcript of a video. Understand the viewer will only see the clip. They will not know or see the context of the clip, so make sure it is understandable by everyone.

    Each clip should:
    - Be *at least 20 seconds long*
    - Include enough *context* before and after the main quote to make it compelling
    - Feel like a *cohesive moment*, not just a standalone sentence
    - Make the viewer *curious*, *laugh*, or *think*

    Here is the transcript with timestamps:
    {fullTranscript}

    Return a list of timestamps and quotes that would be compelling for a short clip. Use this format:

    [
    {{
        "start": 123.4,
        "end": 128.7,
        "reason": "This is a surprising joke."
    }},
    ...
    ]
    """
    response = prompt(inp)
    print(response)
    clips = extract_json_between_markers(response)
    for i, clip in enumerate(clips):
        if os.path.exists(f"clips/clip_{i+1}.mp4"):
            os.remove(f"clips/clip_{i+1}.mp4")
        subprocess.run([
        "ffmpeg", "-i", video_file,
        "-ss", str(clip["start"]),
        "-to", str(clip["end"]),
        "-c:v", "libx264", "-c:a", "aac",
        f"clips/clip_{i+1}.mp4"
    ])


def main(video_file):
    audioPath = 'audio.wav'
    if os.path.exists(audioPath):
        os.remove(audioPath)
    extract_audio(video_file, audioPath)
    segments = transcribe_with_speakers(audioPath)['segments']
    #print(segments['segments'][0],111)
    #print(segments['segments'][1],111)
    #for seg in segments['segments']:
    #    st = seg["start"]
    #    et = seg["end"]
    #    text = seg["text"]
        
    full_transcript = "\n".join(f"[{s['start']:.2f}-{s['end']:.2f}] {s['text']}" for s in segments)
    findSeg(full_transcript,video_file)

def next_available_filename(folder='media', prefix='video', extension='.mp4'):
    pattern = re.compile(rf'^{re.escape(prefix)}(\d+){re.escape(extension)}$')
    existing_numbers = set()

    for filename in os.listdir(folder):
        match = pattern.match(filename)
        if match:
            existing_numbers.add(int(match.group(1)))

    i = 1
    while i in existing_numbers:
        i += 1

    return f"media/{prefix}{i}{extension}"


if __name__ == "__main__":
    print('input youtube video link')
    l = input()
    fileName = next_available_filename()
    download_youtube_video(l, fileName)
    print('created '+ fileName)
    #fileName = "media/video2.mp4"
    main(fileName)

