import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
GEMENIKEY = os.getenv("GEMENIKEY", "")
gemini_client = genai.Client(api_key=GEMENIKEY)

def prompt(prompt):

    response = gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
    )
    return response.text

if __name__ == '__main__':
    print(prompt('hello'))