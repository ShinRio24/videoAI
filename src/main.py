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
from .communicator import sendUpdate


import signal
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr

log_file = open("tools/output_log.txt", "w")

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
            print(f"Ecode000 Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                return e



#removes old files
def resetSystem():
    files = glob.glob(os.path.join("media/refImgs", "*")) + glob.glob(os.path.join("media/audio", "*")) + glob.glob(os.path.join("media/usedImgs", "*"))
    for f in files:
        os.remove(f)

#gen audio and images
def genAudioImages(title,data):
    
    imgAudioData=[]

    for i, x in enumerate(tqdm(data, desc="Processing phrases", unit="phrase", file=sys.__stdout__ )):
        temp ={}
        temp['audio'] ="media/audio/au"+str(i)+".mp3"

        #gen audios, run proof
        run(genAUDIO,[x,"media/audio/au"+str(i)])

        
        src_path = run(imgSearch,[title, x, data])

        ext = os.path.splitext(src_path)[1]
        nPath = "media/usedImgs/img"+str(i)+ext
        shutil.copy2(src_path, nPath)

        temp['path'] = nPath
        temp['phrase']=x
        
        imgAudioData.append(temp)

        tqdm.write(f"Current phrase: {x}")
    return imgAudioData

def generate_youtube_short_video(topic,stdOut):         
    resetSystem()

    print("Generating script",topic, file=stdOut)

    script = prompt(gScriptCharacter_template.format(theme=topic))
    data = script["Script"]

    title = prompt_single(genTitle.format(theme = topic))
    sendUpdate("Generated Title: "+title+" for topic: "+topic)

    print("Generating audio and images", file=stdOut)
    imgAudioData = genAudioImages(title,data)

    print("Combining Media", file=stdOut)

    file = combineMedia(title, imgAudioData)

    print("Uploading", file=stdOut)
    video_id = uploadVideo(video_path= file, title= title)

    print('complete, video has been uploaded to YouTube with ID:', video_id, file=stdOut)
    print('topic:', topic, file=stdOut)
    return f"https://www.youtube.com/watch?v={video_id}"


def main():
    try:
        topic = " ".join(sys.argv[1:])
    except IndexError:
        print("No title provided")
        exit()
    
    tt = time.time()
    
    original_stdout = sys.stdout
    with redirect_stdout(log_file), redirect_stderr(log_file):
        try:
            url = generate_youtube_short_video(topic, original_stdout)
        except Exception as e:
            print("An error occurred:", e)
            traceback.print_exc()
            sendUpdate("Video generation failed for title!\nError: " + str(e), main=True)
            print('An error occurred, check log', file=sys.__stdout__)
        finally:
            log_file.flush()

    print("Total time taken:", (time.time() - tt)/ 60, "minutes")

    result = {"file": url}
    with open("tools/finalURL.json", "w") as f:
        json.dump(result, f)


    sendUpdate("Video generation completed successfully!\nTopic: " + topic + "\nWatch it here: " + url)
    sendUpdate("generation time: " + str((time.time() - tt)/ 60) + " minutes")


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
