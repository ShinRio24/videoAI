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

from .llmPrompt import prompt
from .genAudio import genAUDIO
from .combineMedia import combineMedia
from .contextImgSearcher import imgSearch
from .communicator import sendUpdate, update_progress
import asyncio

import signal
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr


from .configFile import Config
cfg = Config()
cfg.nOutputStream()
log_file = open(cfg.curOutputStream, "a",buffering=1)

def flush_and_close(signal_num=None, frame=None):
    print(f"[SYSTEM] Caught termination signal {signal_num}, flushing logs...", file=sys.__stdout__)
    log_file.flush()
    log_file.close()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, flush_and_close)
signal.signal(signal.SIGTERM, flush_and_close)

# Load environment variables
from dotenv import load_dotenv
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
                sendUpdate("code is broken after run #2, check logs for more detail", main=True)
                exit()



#removes old files
def resetSystem():
    import glob
    import shutil

    # Get a list of all files and directories in the target folders
    paths_to_delete = glob.glob(os.path.join("media/refImgs", "*")) \
                    + glob.glob(os.path.join("media/audio", "*")) \
                    + glob.glob(os.path.join("media/usedImgs", "*"))

    # Loop through the list
    for path in paths_to_delete:
        try:
            # Check if it's a file or a symbolic link
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            # Check if it's a directory
            elif os.path.isdir(path):
                shutil.rmtree(path) # This removes the directory and all its contents
        except Exception as e:
            print(f'Failed to delete {path}. Reason: {e}')

#gen audio and images
async def genAudioImages(title,data):
    
    imgAudioData=[]

    msg = sendUpdate(f"Processing '{title}':\n[{' ' * 20}] 0% (0/{len(data)})", main=False)
    message_id = msg['result']['message_id']

    for i, x in enumerate(data, start=1):
        temp ={
}
        temp['audio'] ='media/audio/au'+str(i)+'.mp3'

        #gen audios, run proof
        run(genAUDIO,[x,"media/audio/au"+str(i)])

        
        src_path = run(imgSearch,[title, x, data])

        ext = os.path.splitext(src_path)[1]
        nPath = "media/usedImgs/img"+str(i)+ext
        shutil.copy2(src_path, nPath)

        temp['path'] = nPath
        temp['phrase']=x
        
        imgAudioData.append(temp)

        await update_progress(message_id, title, i, len(data))

    return imgAudioData

from . import scriptPrompts
def getScriptFormat(contentFormat):

    if hasattr(scriptPrompts, contentFormat):
        retrieved_object = getattr(scriptPrompts, contentFormat)
        return retrieved_object
    else:
        raise KeyError(f"❌ Error: Variable '{contentFormat}' not found in prompts.py.")

import asyncio
import re
from . import prompts
def generate_youtube_short_video(topic, contentFormat):         
    resetSystem()
    scriptFormat = getScriptFormat(contentFormat)

    print("Generating script",topic)
    data = prompt(scriptFormat.format(theme=topic), model = 'gemeni')
    print(data)
    allowed_pattern = re.compile(r'[^A-Za-z0-9\u3040-\u309F\u30A0-\u30FF\uFF65-\uFF9F\u4E00-\u9FFF]')

    title = prompt(prompts.genTitle.format(theme = topic))
    title = allowed_pattern.sub('',title)
    sendUpdate("Generated Title: "+title+" for topic: "+topic)
    sendUpdate('\n'.join(data))

    print("Generating audio and images")
    imgAudioData = asyncio.run(genAudioImages(title,data))

    print("Combining Media")
    from .videoEdit import Videos
    videoObj = Videos(title, imgAudioData)

    file = combineMedia(title, imgAudioData, output_filename=f"media/editEnvs/{videoObj.code}/preview.mp4", preview = True)

    return videoObj


def main(topic, format):
    
    tt = time.time()
    
    with log_file:
        try:
            with redirect_stdout(log_file), redirect_stderr(log_file):
                videoObj = generate_youtube_short_video(topic, format)
                if videoObj:
                    print(f"✅ Success! Video obj: {videoObj}")

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user (Ctrl+C). Flushing logs and exiting...", file=sys.__stdout__)
            log_file.flush()
            raise
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            traceback.print_exc(file=log_file)
            sendUpdate(f"Video generation failed for title!\nError: {e}", main=True)
            raise
        finally:
            log_file.flush()


    print("Total time taken:", (time.time() - tt)/ 60, "minutes")

    #sendUpdate("Video generation completed successfully!\nTopic: " + topic + "\nWatch it here: " + url)
    sendUpdate("Topic: " + topic +"\nGeneration time: " + str(round((time.time() - tt)/ 60)) + " minutes\n"+f"Video Code: {videoObj.code}")

    return videoObj


import argparse

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str,required=True)
    parser.add_argument("--format", type=str, default="general")

    args = parser.parse_args()
    try:
        main(**vars(args))
    except Exception as e:
        print(f"An error occurred: {e}")
        sendUpdate("Video generation failed for title!\nError: " + str(e))
        exit(1)
