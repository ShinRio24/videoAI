import os
from dotenv import load_dotenv

load_dotenv()
TTS_API_KEY = os.getenv("gemeniKey", "")
import requests
import wave
import re
import subprocess
from pydub import AudioSegment
from getBearer import getBearer


def split_text_smart(text, max_len=2500):
    sentences = re.split(r'(?<=[。、「」！？])', text)
    chunks = []
    current = ''

    for sentence in sentences:
        if len(current) + len(sentence) <= max_len:
            current += sentence
        else:
            if current:
                chunks.append(current.strip())
            if len(sentence) > max_len:
                # Fallback: force-break long sentence
                parts = [sentence[i:i+max_len] for i in range(0, len(sentence), max_len)]
                chunks.extend(part.strip() for part in parts)
                current = ''
            else:
                current = sentence
    if current:
        chunks.append(current.strip())
    
    return chunks

def change_speed(sound, speed=1.0):
    altered_frame_rate = int(sound.frame_rate * speed)
    return sound._spawn(sound.raw_data, overrides={'frame_rate': altered_frame_rate}).set_frame_rate(sound.frame_rate)


def genAUDIO(context,output):
    genSpeechify(context,output)



def genSpeechify(context,output):

    url = "https://audio.api.speechify.com/v3/synthesis/get"



    with open("bearer.txt", "r") as file:
        bearer_token = file.read().strip()


    chunk = split_text_smart(context)
    #print(chunk)
    combined = AudioSegment.empty()
    cleanUp = []
    response =''

    for i,context in enumerate(chunk):  
    
        while not (hasattr(response, "status_code") and (response.status_code==200)):
            headers = {
                "Authorization": bearer_token,
                "Content-Type": "application/json",
                "x-speechify-client": "WebApp",
                "x-speechify-client-version": "2.22.1",
                "Origin": "https://app.speechify.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            }
            json_data = {
                "ssml": "<speak>{}</speak>".format(context),
                #"voice": "mayu",
                "voice": "keita",
                #"voice": "nanami",
                #"voice": "shiori",
                #"voice": "daichi",
                #"voice": "naoki",
                "forcedAudioFormat": "mp3",
            }

            response = requests.post(url, headers=headers, json=json_data)
            print("Status:", response.status_code, context)
            #print(type(response.status_code))
            #print("Text content:", response.text)
            if response.status_code!=200:
                getBearer()
                print('got bearer')
                with open("bearer.txt", "r") as file:
                    bearer_token = file.read().strip()


        with open(output+str(i)+".mp3", "wb") as f:
            f.write(response.content)

        print("Saved output.mp3")
        
        combined += AudioSegment.from_mp3(output+str(i)+'.mp3')
        cleanUp.append(output+str(i)+'.mp3')
    
    combined = change_speed(combined, 1.1)
    combined.export(output+'.mp3', format="mp3")
    for file_path in cleanUp:
        os.remove(file_path)
    print(output)



def genTiktok(context,output):
    chunk = split_text_smart(context)
    #print(chunk)
    combined = AudioSegment.empty()
    cleanUp = []
    for i,context in enumerate(chunk):  
        
        # Path to your JavaScript file
        js_file_path = r"C:\Users\Rioss\Desktop\Code\videoAI\index.js"
        # Parameters to pass to the JavaScript file
        params = [output+str(i),context]

        # Run the JavaScript file with parameters using Node.js
        node_path = r"C:\Program Files\nodejs\node.exe"

        result = subprocess.run([node_path, js_file_path] + params, check=True,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
        
        combined += AudioSegment.from_mp3(output+str(i)+'.mp3')
        cleanUp.append(output+str(i)+'.mp3')

        #print(result.stdout)
        #print(result.stderr)
    
    combined = change_speed(combined, 1.3)
    combined.export(output, format="mp3")
    for file_path in cleanUp:
        os.remove(file_path)
    print(output)



if __name__ == '__main__':
    genAUDIO("Amazonのインパクトは計り知れません。私たちの買い物体験を根底から変えただけでなく、AWS（アマゾン・ウェブ・サービス）がインターネットの膨大なサービスを裏で支えてるんです。NetflixもAdobeも、AWSのお世話になってるって聞いたら、もうAmazonが世界のインフラだってことが分かるはず！", "media/test")
