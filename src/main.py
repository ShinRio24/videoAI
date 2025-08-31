# Standard library imports
import os
import sys
import time
import json
import glob
import difflib
import shutil
import traceback
from contextlib import redirect_stdout, redirect_stderr

# Third-party imports
from dotenv import load_dotenv
from tqdm import tqdm
from PIL import Image

# Local application imports
from .llmPrompt import prompt, prompt_single
from .genAudio import genAUDIO
from .combineMedia import combineMedia
from .contextImgSearcher import imgSearch
from .uploadVideo import uploadVideo
from .prompts import *
from .communicator import sendUpdate, update_progress, postToTelegram
import asyncio

import signal
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr

class FlushFile:
    def __init__(self, file):
        self.file = file
    def write(self, msg):
        self.file.write(msg)
        self.file.flush()
    def flush(self):
        self.file.flush()

log_file_path = "tools/output_log.txt"
log_file = open(log_file_path, "a",buffering=1)

def flush_and_close(signal_num=None, frame=None):
    print(f"[SYSTEM] Caught termination signal {signal_num}, flushing logs...", file=sys.__stdout__)
    log_file.flush()
    log_file.close()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, flush_and_close)
signal.signal(signal.SIGTERM, flush_and_close)

# Load environment variables
load_dotenv()
GEMENIKEY = os.getenv("gemeniKey", "")

#run programs with the retry
def run(func, params, max_retries=2):
    for attempt in range(1, max_retries + 1):
        try:
            return func(*params)
        except Exception as e:
            print(f"[ERROR] Attempt {attempt} failed!")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {str(e)}")
            print("Stack trace:")
            traceback.print_exc()
            sendUpdate(str(e)+" attempting another run")
            if attempt == max_retries:
                sendUpdate("code is broken after run #2, check logs for more detail")
                exit()



#removes old files
def resetSystem():
    files = glob.glob(os.path.join("media/refImgs", "*")) + glob.glob(os.path.join("media/audio", "*")) + glob.glob(os.path.join("media/usedImgs", "*"))
    for f in files:
        os.remove(f)

#gen audio and images
async def genAudioImages(title,data):
    
    imgAudioData=[]

    msg = sendUpdate(f"Processing '{title}':\n[{' ' * 20}] 0% (0/{len(data)})", main=True)
    message_id = msg['result']['message_id']

    usedQuerys={}
    for i, x in enumerate(data, start=1):
        temp ={}
        temp['audio'] ="media/audio/au"+str(i)+".mp3"

        #gen audios, run proof
        run(genAUDIO,[x,"media/audio/au"+str(i)])

        
        src_path, usedQuerys = run(imgSearch,[title, x, data,usedQuerys])

        ext = os.path.splitext(src_path)[1]
        nPath = "media/usedImgs/img"+str(i)+ext
        shutil.copy2(src_path, nPath)

        temp['path'] = nPath
        temp['phrase']=x
        
        imgAudioData.append(temp)

        await update_progress(message_id, title, i, len(data))

    return imgAudioData

import asyncio
import re

def generate_youtube_short_video(topic):         
    resetSystem()

    print("Generating script",topic)

    script = prompt(gScriptCharacter_template.format(theme=topic), model = 'gemeni')
    print(script)
    data = script["Script"]
    allowed_pattern = re.compile(r'[^A-Za-z0-9\u3040-\u309F\u30A0-\u30FF\uFF65-\uFF9F\u4E00-\u9FFF]')

    title = prompt_single(genTitle.format(theme = topic))
    title = allowed_pattern.sub('',title)
    sendUpdate("Generated Title: "+title+" for topic: "+topic)
    sendUpdate('\n'.join(data))

    print("Generating audio and images")
    imgAudioData = asyncio.run(genAudioImages(title,data))

    print("Combining Media")
    
    file = combineMedia(title, imgAudioData, output_filename="media/tempFiles/{}.mp4", preview = True)

    from .videoEdit import Videos
    videoObj = Videos(title, imgAudioData)
    #asyncio.run(postToTelegram(file))

    #sendUpdate("video posted to telegram")
    # file = combineMedia(title, imgAudioData)

    # print("Uploading")

    # video_id = uploadVideo(video_path= file, title= title, videoData=imgAudioData)

    # print('complete, video has been uploaded to YouTube with ID:', video_id)
    # print('topic:', topic)
    # return video_id
    return "video ID no longer supported"


def main():
    try:
        topic = " ".join(sys.argv[1:])
    except IndexError:
        print("No title provided")
        exit()
    
    tt = time.time()
    
    with log_file:
        try:
            with redirect_stdout(log_file), redirect_stderr(log_file):
                url = generate_youtube_short_video(topic)
                if url:
                    print(f"✅ Success! Video URL: {url}")
        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user (Ctrl+C). Flushing logs and exiting...", file=sys.__stdout__)
            log_file.flush()
            raise
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            traceback.print_exc(file=log_file)
            sendUpdate(f"Video generation failed for title!\nError: {e}", main=True)
        finally:
            log_file.flush()


    print("Total time taken:", (time.time() - tt)/ 60, "minutes")

    result = {"file": url}
    with open("tools/finalURL.json", "w") as f:
        json.dump(result, f)


    #sendUpdate("Video generation completed successfully!\nTopic: " + topic + "\nWatch it here: " + url)
    sendUpdate("Topic: " + topic +"\nGeneration time: " + str(round((time.time() - tt)/ 60)) + " minutes")


    return url


if __name__ =='__main__':
    # The user's original line is commented out to avoid immediate image generation on load,
    # as the new method will handle the full workflow.

    # Call the main video generation method. You can change the theme.
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        sendUpdate("Video generation failed for title!\nError: " + str(e))
        exit(1)
    # Optionally, you can send a message to the Telegram channel
