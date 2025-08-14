import os
import json
from dotenv import load_dotenv
import glob
import difflib
from contextlib import redirect_stdout


import time
import json
from llmPrompt import prompt
from genAudio import genAUDIO
from combineMedia import combineMedia
from contextImgSearcher import imgSearch
from combineMedia import combineMedia
load_dotenv()
GEMENIKEY = os.getenv("gemeniKey", "")
from uploadVideo import uploadYoutube
import sys
import sys
from contextlib import redirect_stdout, redirect_stderr
from tqdm import tqdm
from prompts import *
import json
from PIL import Image



def imgMatch(input_str,options,files):
    return files[options.index(difflib.get_close_matches(input_str, options, n=1, cutoff=0.0)[0])]


def resizeImage(path, target_size):
    img = Image.open(path)

    # Resize proportionally to fit within target_size
    img.thumbnail(target_size, Image.Resampling.LANCZOS)  # Safe with Pillow >= 10

    # Save to a temporary file (or use BytesIO if you want to avoid disk write)
    os.remove(path)
    img.save(path)
    return path

def generate_youtube_short_video(title,stdOut):
    folder = "media/refImgs"

    files = glob.glob(os.path.join(folder, "*"))
    for f in files:
        os.remove(f)
    print("Generating script", file=stdOut)

    jsonOutput = prompt(genScript_template.format(theme=title))

    data = jsonOutput["Script"]
    #print(data)
    #combined = AudioSegment.empty()
    print("Generating audio and images", file=stdOut)
    imgAudioData=[]
    usedImages=[]


    for i, x in enumerate(tqdm(data, desc="Processing phrases", unit="phrase", file=stdOut)):
        temp ={}
        temp['audio'] ="media/audio/au"+str(i)+".mp3"

        genAUDIO(x,"media/audio/au"+str(i))
        temp['path'], usedImageDescription= imgSearch(title,x, usedImages)
        usedImages.append(usedImageDescription)
        temp['phrase']=x
        imgAudioData.append(temp)

        tqdm.write(f"Current phrase: {x}")
    

    print("Combining Media", file=stdOut)
    #print(title,imgAudioData)
    file = combineMedia(title, imgAudioData)
    #audio = AudioFileClip(tempAudioPath+".mp3")
    #imgFile = imgMatch(x['image_description'], description,files)

    print("Uploading", file=stdOut)
    video_id = uploadYoutube(
        video_file= file,
        title= title,
        tags=["動画", "#shorts"],
        privacy_status="public",
    )
    print('complete, video has been uploaded to YouTube with ID:', video_id, file=stdOut)
    print('title:', title, file=stdOut)
    return f"https://www.youtube.com/watch?v={video_id}"


def main():
    try:
        title = sys.argv[1]
    except IndexError:
        print("No title provided")
        exit()
    print("generating video script for title:", title)

    tt = time.time()
    
    original_stdout = sys.stdout
    with open("tools/output_log.txt", "w") as f, redirect_stdout(f), redirect_stderr(f):
        url = generate_youtube_short_video(title, original_stdout)

    print("Total time taken:", (time.time() - tt)/ 60, "minutes")

    result = {"file": url}
    with open("tools/finalURL.json", "w") as f:
        json.dump(result, f)

    return url


if __name__ =='__main__':
    # The user's original line is commented out to avoid immediate image generation on load,
    # as the new method will handle the full workflow.
    # tt = genIMG("generate an image of YouTubeショート動画の台本を作成してください。テーマは「college」です。")
    #combineMedia(5)

    # Call the main video generation method. You can change the theme.
    main()
