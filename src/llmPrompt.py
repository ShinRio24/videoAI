import os
from dotenv import load_dotenv
import google.generativeai as genai
import re
import json
import requests
import json
from datetime import date
import sys
from .prompts import *
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


LAST_FAILURE_FILE = "tools/last_failure.json"

load_dotenv()
GEMENIKEY = os.getenv("GEMENIKEY", "")
genai.configure(api_key=GEMENIKEY)

# Create a model object
#   gemini_client = genai.GenerativeModel("gemini-1.5-flash")  # or "gemini-1.5-pro"




#taken from sakana ai, ai scientist
#https://github.com/SakanaAI/AI-Scientist
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

def get_last_failure_date():
    with open(LAST_FAILURE_FILE, "r") as f:
        data = json.load(f)
        return date.fromisoformat(data.get("last_failure"))

def set_last_failure_date(failure_date):
    with open(LAST_FAILURE_FILE, "w") as f:
        json.dump({"last_failure": failure_date.isoformat()}, f)


def prompt(prompt):

    print(f"START OF PROMPT  --------------------------------------------\n {prompt}")

    today = date.today()
    last_failure = get_last_failure_date()

    if last_failure == today:
        # Already failed today, skip function_a
        output = ollama_prompt(prompt)
    else:
        try:
            output = promptGemeni(prompt)
        except Exception as e:
            print(f"function_a failed: {e}", file=sys.__stderr__)
            set_last_failure_date(today)
            output = ollama_prompt(prompt)
        
    #output = promptGemeni(prompt)
    print(f"END OF PROMPT  --------------------------------------------\n")
    print(f"LLM output: {output}")
    print(f"END OF LLM OUTPUT --------------------------------------------\n")

    extracted = extract_json_between_markers(output)
    print(extracted, "this is the extracted output")
    return extracted

def prompt_single(prompt):

    print(f"START OF PROMPT  --------------------------------------------\n {prompt}")

    today = date.today()
    last_failure = get_last_failure_date()

    if last_failure == today:
        # Already failed today, skip function_a
        output = ollama_prompt(prompt)
    else:
        try:
            output = promptGemeni(prompt)
        except Exception as e:
            print(f"function_a failed: {e}", file=sys.__stderr__)
            set_last_failure_date(today)
            output = ollama_prompt(prompt)
        
    #output = promptGemeni(prompt)
    print(f"END OF PROMPT  --------------------------------------------\n")
    print(f"LLM output: {output}")
    print(f"END OF LLM OUTPUT --------------------------------------------\n")

    extracted = (output)

    return extracted

def ollama_prompt(prompt, model="gemma3:latest"):

    #chat will give the thinking process, generate will give the final answer
    #url = "http://localhost:11434/api/chat"
    #Sure! In Ollama’s /chat API, each message has a role that tells the model how to interpret the text. In your example:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()
    output = r.json()["response"]
    #print(r.json())

    # Remove <think>...</think> block if present
    #output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
    return output

def ollama_prompt_img(prompt,image_path, model="gemma3:latest"):

    #chat will give the thinking process, generate will give the final answer
    #url = "http://localhost:11434/api/chat"
    #Sure! In Ollama’s /chat API, each message has a role that tells the model how to interpret the text. In your example:

    print(f"START OF PROMPT  --------------------------------------------\n {prompt}")
    print(f"Image path: {image_path}")

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_to_base64(image_path)],
        "stream": False
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()
    output = r.json()["response"]

    

    print(f"END OF PROMPT  --------------------------------------------\n")
    print(f"LLM output: {output}")
    print(f"END OF LLM OUTPUT --------------------------------------------\n")

    # Remove <think>...</think> block if present
    #output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
    #output = extract_json_between_markers(output)
    return output


def promptGemeni(prompt):
    response = gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
    )
    return response.text


if __name__ == '__main__':
    #text  = imageDescription_template
    #print(ollama_prompt_img(text, "media/refImgs/img0_1.jpg"))


    #text = genScript_template.format(theme="宮田 典子")
    #print(ollama_prompt(text))

    text = """
### Instruction:
あなたはプロの日本語YouTubeスクリプトライターです。

タスク：
テーマ「パブロ・エスコバル」について短編YouTubeスクリプトを日本語で作成してください。  
カリスマ的なYouTuberが話すような自然な口語で、面白く楽しく語ってください。  

- その人物の生い立ちや歩み、どのようにして現在の地位に至ったのか、そして今どんな影響を与えているのかを中心に語ること。  
- 必要に応じて背景・原因・エピソード・意外な一面も加えること。  

要件：  
- スクリプト全体は必ず約600文字（±5%以内）  
- 各フレーズは平均30文字前後。ただし20〜40文字の揺らぎをつけること  
- 各フレーズをJSONリストに分割してください（画像表示用のブレイクポイント）  
- 同じ画像が9秒以上表示されないように調整してください  
- 各フレーズは文として完結していなくても良いが、全体の流れで意味が通ること  
- スクリプトの冒頭は必ずキャッチーな質問形式で始めること  
  （例：知っていますか、実はこんな事実があるんです、など）  
- 箇条書きのように事実を並べず、会話の流れで自然につなげること  
- 前後のフレーズをつなぐ「でも」「だから」「実は」「一方で」などを適度に入れること  
- です・ます調は基本だが、すべての文を終わらせない  
- 語尾に「なんです」「だったんですね」など変化をつける  
- 驚きや感情を少し混ぜて自然に話す  
- トーンはドキュメンタリー風だが楽しく魅力的に  
- 禁止事項：  
  - 「」や""などの引用符を一切使わないこと  
  - 「笑」や特殊記号を使わないこと  
- 句読点は「、」と「。」のみ使用可  


出力形式：
必ず次のフォーマットに従ってください。他のテキストは絶対に出力しないでください。

正しい形式の例：
json```
{
  "Script": [
    "文1",
    "文2",
    "文3"
  ]
}```
"""
    print(prompt(text))