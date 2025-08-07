import os
from dotenv import load_dotenv
from google import genai
import re
import json

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


def prompt(prompt):

    response = gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
    )
    return response.text

if __name__ == '__main__':
    print(prompt('hello'))