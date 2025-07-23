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


from llmPrompt import prompt
from genAudio import genAUDIO
from genImg import genIMG
from combineMedia import combineMedia
from imgSearch import imgSearch
from imageDescription import descriptions
from combineMedia import combineMedia
load_dotenv()
GEMENIKEY = os.getenv("gemeniKey", "")
import re
from pydub import AudioSegment
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, AudioFileClip, ColorClip, concatenate_videoclips
from imageGetter import download


theme = 'Amazon'
title = '世界の“1兆ドル企業”を紹介'

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

def imgMatch(input_str,options,files):
    return files[options.index(difflib.get_close_matches(input_str, options, n=1, cutoff=0.0)[0])]

def generate_video_script():


    script_prompt = (f"""
    You are a professional Japanese YouTube scriptwriter.
Please write a short-form YouTube script in Japanese, designed to be entertaining, fun to watch, and natural-sounding, as if spoken by a charismatic YouTuber.

The theme of the section you are writing a script for is is: {theme}
This is part of a larger ranking video, but only write the section about {theme}. Do **not** mention other sections of the video.

The theme of the overall video title is: {title}
Make your script relevant to the topic, but still about your sepecific section. For example, if the video title about financials, talk about the financials for your specific section

Make sure the script:
The video should cover the topic in depth, in around 1 minute.
Go straight into the section, without a intro
Add alot of commas.
Feels like a YouTube short or TikTok script: casual, punchy
Is written in natural spoken Japanese, not stiff formal writing
Keeps viewer interest high with fun transitions, questions, and real-world references
Each line should be one sentance, Or two if both are short.
Do not add excess text such as 笑, 「, 」
Total runtime: 1 minute of speech (~500–600 characters)

The output should be in the following JSON format:
{{
  "Script": [
      "今日は、非常に人気のある哲学的理論を深く掘り下げて紹介します。これらの理論は、現代の思考に大きな影響を与え、私たちの理解を深めるための道しるべとなっています。",
      "まずは、ソクラテス的対話について話しましょう。この理論は、自己反省を促し、深い思考を行うための手法として広く使用されています。ソクラテスの方法は、質問を通じて相手の考えを掘り下げ、深い理解を得るというものです。現代の教育においては、批判的思考を養うために多く使用されており、特にディスカッションを通じて問題解決のアプローチを学ぶ場面で見かけます。たとえば、ビジネスの現場では、課題解決のために異なる視点を引き出し、チームメンバー間の建設的な対話を促進するためにこのアプローチが活用されています。",
      "次に功利主義を取り上げましょう。功利主義は、行動の結果が社会全体にとって最も利益をもたらすかどうかに基づいて判断される倫理理論です。現代社会では、政策決定や法律制定の場面でこの理論が応用されています。たとえば、公共政策におけるリソース配分や、医療の優先順位を決める際に、最大の社会的利益を追求するために功利主義の考え方が使われます。"
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
    jsonOutput=generate_video_script()
    data = jsonOutput["Script"]
    print(data)
    #combined = AudioSegment.empty()

    download(['jeff bezos', 'amazon'])

    folder = "media/refImgs"

    files = glob.glob(os.path.join(folder, "*"))
    description, files = descriptions(files)
    
    correctIMG = f"""
        You are an AI assistant tasked with selecting the best image for each segment of a video script.

You are given:

A list of script phrases or sentences (typically short video narration lines). Each phrase is separated by a new line. As given here: {chr(10).join(data)}

A list of image descriptions generated from automatic tools or captions (these may not always be perfectly clear or explicit). Each phrase is separated by a new line. As given here {chr(10).join(description)}

Your job is to match each script segment with the most relevant image, even if the image description:

Doesn't explicitly mention the exact name or subject

Refers to the subject indirectly or abstractly

Describes the scene, person, or activity related to the phrase

Your matches should be based on understanding of context, implied meaning, and background knowledge.

For example:

If a script says “Jeff Bezos started Amazon in his garage,” and an image description says “a man in a small room surrounded by boxes,” you should correctly infer that the image matches, even if it doesn’t name him.

For each phrase, return:

The best-matching image description

A short explanation of why this match makes sense (including inferred or indirect context)

Avoid choosing irrelevant or misleading images just because they contain a keyword. Prioritize semantic relevance, narrative flow, and viewer clarity.
Example Format for Output
json
[
  {{
    "phrase": "Jeff Bezos started Amazon in his garage.",
    "image_description": "A man working on a computer in a cluttered garage.",
    "reason": "The image indirectly represents Jeff Bezos’ early Amazon days, matching the garage startup context."
  }},
  {{
    "phrase": "Apple changed the way we listen to music.",
    "image_description": "White earbuds plugged into a phone showing a music app.",
    "reason": "The description reflects Apple's impact on music through products like the iPod and iPhone, even if Apple isn't named."
  }}
]
    """

    response = prompt(correctIMG)
    imgMatches = extract_json_between_markers(response)
    print(imgMatches)


    
    for i,x in enumerate(imgMatches):
        x['audio'] ="media/au"+str(i)+".mp3"

        genAUDIO(x['phrase'],"media/au"+str(i))
        x['path']=imgMatch(x['image_description'], description,files)

    combineMedia(title, imgMatches)
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
