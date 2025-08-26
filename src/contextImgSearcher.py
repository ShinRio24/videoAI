from .llmPrompt import prompt
from .llmPrompt import ollama_prompt_img
from .imageGetter import download

import os
import glob
import difflib
from .prompts import *
from skimage.metrics import structural_similarity as ssim
import cv2
import subprocess
from pathlib import Path

from .communicator import sendUpdate


import signal
import sys
import traceback
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
            sendUpdate(str(e))
            if attempt == max_retries:
                return e

def imgMatch(input_str,options,files):
    return files[options.index(difflib.get_close_matches(input_str, options, n=1, cutoff=0.0)[0])]    

def removeUsedImgs(files):
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
    used_folder = "/home/riosshin/code/videoAI/media/usedImgs"

    usedFiles = []
    for ext in image_extensions:
        usedFiles.extend(glob.glob(os.path.join(used_folder, f"*{ext}")))

    nonSimilarImgs = []
    for img1Path in files:
        img1 = cv2.imread(img1Path, cv2.IMREAD_GRAYSCALE)
        if img1 is None:
            sendUpdate(f"image not readable: {img1Path}")
            continue  # skip this image

        is_used = False
        for img2Path in usedFiles:
            img2 = cv2.imread(img2Path, cv2.IMREAD_GRAYSCALE)
            if img2 is None:
                print(f"[WARNING] Skipping unreadable used image: {img2Path}")
                continue

            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            score, _ = ssim(img1, img2, full=True)

            if score >= 0.9:
                print('image was used', img1Path)
                is_used = True
                break

        if not is_used:
            nonSimilarImgs.append(img1Path)

    return nonSimilarImgs


def autoCropImages(files):
    fuzz = "10%"
    for image_path in files:
        img_path = Path(image_path)

        cmd = [
            "convert", str(img_path), 
            "-fuzz", fuzz,
            "-trim", "+repage",
            str(image_path)
        ]
        subprocess.run(cmd, check=True)

def descriptions(files):
    description = []
    for file in files:
        desc = ollama_prompt_img(imageDescription_template, file)
        description.append(desc)
    return description, files

def imgSearch(title, quote, data, usedQuerys):

    queryPrompt = queryPrompt_template.format(title=title, quote=quote, data = '\n'.join(data))

    response = run(prompt,[queryPrompt])
    outputQuery = response['query']
    
    if outputQuery in usedQuerys:
        files = usedQuerys[outputQuery].copy()
        print('code1: same image used')
    else:
        files = download([outputQuery], 30)

    files = removeUsedImgs(files)
    print(files)

    description, files = descriptions(files)
    
    correctIMG = correctIMG_template.format(quote=quote, description=chr(10).join(description))
    matchedImage = prompt(correctIMG)
    matchedImage = matchedImage['image_description']
    matchedImage = imgMatch(matchedImage, description,files)

    files.remove(matchedImage)
    usedQuerys[outputQuery]=files
    return matchedImage,usedQuerys



if __name__ == '__main__':
    #test
    #format is title, quote
    #result = imgSearch("Jeff Bezos", "jeff bezos and donald trump have met in the #past, although it is not often.")
    #print(result)

    autoCropImages(["bro.jpg"])
    print("done")