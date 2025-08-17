import os
from dotenv import load_dotenv
from google import genai
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
gemini_client = genai.Client(api_key=GEMENIKEY)



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


    text = genScript_template.format(theme="宮田 典子")
    print(ollama_prompt(text))