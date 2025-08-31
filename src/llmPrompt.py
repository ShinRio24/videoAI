import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
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


modelGemeni = genai.GenerativeModel('gemini-2.5-flash')
ollamaModel = "gemma2-9b-long:latest"



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
                json_string = json_string.replace("“", '"').replace("”", '"')
                json_string = json_string.replace("‘", "'").replace("’", "'")
                json_string = json_string.replace('\u00a0', ' ')
                json_string = re.sub(r'[\x00-\x1F\x7F]', '', json_string)
                parsed_json = json.loads(json_string)
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


def prompt(prompt, model = "ollama"):

    print(f"START OF PROMPT  --------------------------------------------\n {prompt}")
    if model == "gemeni-cli":
        output = gemeniCli(prompt)
    elif model =="ollama":
        output = ollama_prompt(prompt)
    elif model =='gemeni':
        today = date.today()
        last_failure = get_last_failure_date()

        if last_failure == today:
            # Already failed today, skip function_a
            output = ollama_prompt(prompt)
        else:
            try:
                output = promptGemeni(prompt)
                print('used gemeni')
            except Exception as e:
                print(f"gemeni failed: {e}", file=sys.__stderr__)
                set_last_failure_date(today)
                output = ollama_prompt(prompt)
    else:
        raise ValueError("Model does not exist")
    
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



def ollama_prompt(prompt, model=ollamaModel):

    #chat will give the thinking process, generate will give the final answer
    #url = "http://localhost:11434/api/chat"
    #Sure! In Ollama’s /chat API, each message has a role that tells the model how to interpret the text. In your example:

    print('prompting local')
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()
    output = r.json()["response"]

    print(output)
    #print(r.json())

    # Remove <think>...</think> block if present
    #output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
    return output

import subprocess
def gemeniCli(prompt):
    try:
        gemini_executable_path = "/home/linuxbrew/.linuxbrew/bin/gemini"
        result = subprocess.run(
            [gemini_executable_path, "-p", prompt],
            capture_output=True, text=True,
            check=True  # raises exception if exit code != 0
        )
        return (result.stdout)
    except subprocess.CalledProcessError as e:
        print("Command failed!")
        raise (e.stderr)  # error output

def ollama_prompt_img(prompt,image_path, model=ollamaModel):

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
    try:
        global modelGemeni
        response = modelGemeni.generate_content(
        prompt
        )
        return response.text
    except ResourceExhausted as e:
            # This block runs ONLY if a 429 error occurs
            print(f"⚠️ Warning: Rate limit exceeded.")
            
            modelGemeni = genai.GenerativeModel('gemini-2.5-flash')
            return promptGemeni(prompt)

    except Exception as e:
        print(f"An unexpected error occurred with with api generation")
        return f"Error: An unexpected error occurred. Details: {e}"


if __name__ == '__main__':
    #text  = imageDescription_template
    #print(ollama_prompt_img(text, "media/refImgs/img0_1.jpg"))
    from .prompts import gScriptCharacter_template

    #text = gScriptCharacter_template.format(theme="加藤智大 - 秋葉原通り魔事件を引き起こした")
    text = queryPrompt_template.format(title="加藤智大 - 秋葉原通り魔事件を引き起こした", quote=" 秋葉原通り魔事件を引き起こした")
    print(prompt(text,model = 'gemeni'))

#     text = """
# this is a test, how are you doing
# ```
# """
#     print(prompt(text))