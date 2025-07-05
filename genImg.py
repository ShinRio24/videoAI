import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("gemeniKey", "")

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

def genIMG(content, output):
    client = genai.Client(api_key=GEMINI_API_KEY)


    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=content,
        config=types.GenerateContentConfig(
        response_modalities=['TEXT','IMAGE']
        )
    )
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save('media/{output}.png')


if __name__ == '__main__':
    genIMG('Visualizing: a student wakes up',-1)