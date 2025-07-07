import os
import json
import base64
import requests
from io import BytesIO
from dotenv import load_dotenv
import wave
import contextlib



from llmPrompt import prompt
from genAudio import genAUDIO
from genImg import genIMG
from combineMedia import combineMedia
from imgSearch import imgSearch
load_dotenv()
GEMENIKEY = os.getenv("gemeniKey", "")
import re
from pydub import AudioSegment

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

def generate_video_script():
    """
    Generates a YouTube short video script based on a given theme.
    Returns a list of parsed statements from the script.
    """

    script_prompt = ("""
    Generate a script in Japanese for a YouTube video that should be around 1 minutes long, or approximately 500 words. The video should explore several prominent philosophical theories in great depth, explaining their key concepts, key philosophers who developed them, and their lasting impact on modern thought. The script should also include real-world examples of how these theories apply to contemporary issues or everyday life, making the content engaging and relatable for a broad audience.

The focus should be on:

The nature and impact of major philosophical theories.

How these theories influenced fields such as ethics, politics, education, and human behavior.

Practical, real-world examples or applications of the theories to help the audience connect with the ideas.

Please ensure that the content is informative, clear, and deeply engaging, providing in-depth explanations of the theories while also connecting them to the real world.

The output should be in the following JSON format:
{
  "Script": [
    {
      "Title": "哲学の理論についての紹介",
      "text": "今日は、非常に人気のある哲学的理論を深く掘り下げて紹介します。これらの理論は、現代の思考に大きな影響を与え、私たちの理解を深めるための道しるべとなっています。これから説明する理論は、教育、倫理、政治、社会などの分野において、私たちの日常生活にも影響を与え続けています。"
    },
    {
      "Title": "理論1: ソクラテス的対話と批判的思考",
      "text": "まずは、ソクラテス的対話について話しましょう。この理論は、自己反省を促し、深い思考を行うための手法として広く使用されています。ソクラテスの方法は、質問を通じて相手の考えを掘り下げ、深い理解を得るというものです。現代の教育においては、批判的思考を養うために多く使用されており、特にディスカッションを通じて問題解決のアプローチを学ぶ場面で見かけます。たとえば、ビジネスの現場では、課題解決のために異なる視点を引き出し、チームメンバー間の建設的な対話を促進するためにこのアプローチが活用されています。"
    },
    {
      "Title": "理論2: 功利主義と社会的利益",
      "text": "次に功利主義を取り上げましょう。功利主義は、行動の結果が社会全体にとって最も利益をもたらすかどうかに基づいて判断される倫理理論です。現代社会では、政策決定や法律制定の場面でこの理論が応用されています。たとえば、公共政策におけるリソース配分や、医療の優先順位を決める際に、最大の社会的利益を追求するために功利主義の考え方が使われます。"
    }]}
    ONLY RETURN THE RAW JSON FILE, DO NOT REUTURN ANYTHING ELSE""")
    
    response = prompt(script_prompt)
    print(response)


    
    return extract_json_between_markers(response)


import json

def generate_youtube_short_video():
    jsonOutput=generate_video_script()
    data = jsonOutput["Script"]
    combined = AudioSegment.empty()
    for i,x in enumerate(data):
        genAUDIO(x['text'],"media/au"+str(i))
        combined += AudioSegment.from_mp3("media/"+str(i)+'.mp3')
    combined.export('media/final.mp3', format="mp3")
    
   

if __name__ =='__main__':
    # The user's original line is commented out to avoid immediate image generation on load,
    # as the new method will handle the full workflow.
    # tt = genIMG("generate an image of YouTubeショート動画の台本を作成してください。テーマは「college」です。")
    #combineMedia(5)

    # Call the main video generation method. You can change the theme.
    generate_youtube_short_video()
