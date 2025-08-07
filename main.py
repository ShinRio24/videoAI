import os
import json
import base64
import requests
from io import BytesIO
from dotenv import load_dotenv
import wave
import contextlib
import glob
import difflib


from llmPrompt import extract_json_between_markers
from llmPrompt import prompt
from genAudio import genAUDIO
from genImg import genIMG
from combineMedia import combineMedia
from contextImgSearcher import imgSearch
from imageDescription import descriptions
from combineMedia import combineMedia
load_dotenv()
GEMENIKEY = os.getenv("gemeniKey", "")
import re
from pydub import AudioSegment
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, AudioFileClip, ColorClip, concatenate_videoclips
from imageGetter import download



def imgMatch(input_str,options,files):
    return files[options.index(difflib.get_close_matches(input_str, options, n=1, cutoff=0.0)[0])]


theme = 'ロシア・ウクライナ紛争'
title = 'ロシア・ウクライナ紛争'

def generate_video_script():


    script_prompt = (f"""
    You are a professional Japanese YouTube scriptwriter.
Please write a short-form YouTube script in Japanese, designed to be entertaining, fun to watch, and natural-sounding, as if spoken by a charismatic YouTuber.

The theme of the section you are writing a script for is: {theme}

Because acompanying images will be given for each section of the script, break up the script accordingly. Place sentances that say similar things in the same quote, but do not make each one two long or the viewer may loose attention.

Make sure the script:
The video should cover the topic in depth.
Go straight into the section, without a intro
Add alot of commas,
Each section should be around 1 sentance
You do not have to have the quote end on a punctuation, and can have it pick up in the next quote
Feels like a YouTube short or TikTok script: casual, punchy
Is written in natural spoken Japanese, not stiff formal writing
Keeps viewer interest high with fun transitions, questions, and real-world references
Do not add excess text such as 笑 「 」


The output should be in the following JSON format:
{{
  "Script": [
      "昔のおにぎりってさ、ただの白米に具がドン、だったのに",
    "今のやつ、もはや和食の集大成レベル",
    "焼きしゃけ、たまごかけ風、牛カルビ、明太チーズとかさ",
    "いや、もはや寿司じゃんって味のやつもある",
    "ローソンの金しゃけ、マジで店より美味いって言われてるし",
    "セブンの半熟煮たまご、割った瞬間のトロッがエグい",
    "ファミマは最近、韓国風のやつまで出してきてて",
    "キンパ風？ナムル入り？誰が思いついたん？"
    ]}}
    ONLY RETURN THE RAW JSON FILE, DO NOT REUTURN ANYTHING ELSE""")
    
    response = prompt(script_prompt)
    print(response)


    
    return extract_json_between_markers(response)


import json

from PIL import Image

def resizeImage(path, target_size):
    img = Image.open(path)

    # Resize proportionally to fit within target_size
    img.thumbnail(target_size, Image.Resampling.LANCZOS)  # Safe with Pillow >= 10

    # Save to a temporary file (or use BytesIO if you want to avoid disk write)
    os.remove(path)
    img.save(path)
    return path

def generate_youtube_short_video():
    folder = "media/refImgs"

    files = glob.glob(os.path.join(folder, "*"))
    for f in files:
        os.remove(f)

    jsonOutput=generate_video_script()
    data = jsonOutput["Script"]
    print(data)
    #combined = AudioSegment.empty()

    imgAudioData=[]
    for i,x in enumerate(data):
        temp ={}
        temp['audio'] ="media/au"+str(i)+".mp3"

        genAUDIO(x,"media/au"+str(i))
        temp['path']= imgSearch(title,x)
        temp['phrase']=x
        imgAudioData.append(temp)

    print(title,imgAudioData)
    combineMedia(title, imgAudioData)
        #audio = AudioFileClip(tempAudioPath+".mp3")
        #imgFile = imgMatch(x['image_description'], description,files)
    


def main():
    generate_youtube_short_video()

if __name__ =='__main__':
    # The user's original line is commented out to avoid immediate image generation on load,
    # as the new method will handle the full workflow.
    # tt = genIMG("generate an image of YouTubeショート動画の台本を作成してください。テーマは「college」です。")
    #combineMedia(5)

    # Call the main video generation method. You can change the theme.
    main()
