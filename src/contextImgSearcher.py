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

def imgMatch(input_str,options,files):
    return files[options.index(difflib.get_close_matches(input_str, options, n=1, cutoff=0.0)[0])]    

def removeUsedImgs(files):
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
    usedFiles = [f for f in files if f.lower().endswith(image_extensions)]
    for img1Path in files:

        for img2Path in usedFiles:
            img1 = cv2.imread(img1Path, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(img2Path, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            score, diff = ssim(img1, img2, full=True)
            if score > 0.9:
                files.remove(img1Path)
                break
    return files

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

def imgSearch(title, quote):

    queryPrompt = queryPrompt_template.format(title=title, quote=quote)

    response = prompt(queryPrompt)
    outputQuery = response['query']
    
    files = download([outputQuery])

    #incase all the outputted images have been used
    bUpFiles = files
    files = removeUsedImgs(files)
    autoCropImages(files)

    if not files:
        files = bUpFiles

    description, files = descriptions(files)
    
    correctIMG = correctIMG_template.format(quote=quote, description=chr(10).join(description))
    matchedImage = prompt(correctIMG)
    matchedImage = matchedImage['image_description']
    
    return imgMatch(matchedImage, description,files)



if __name__ == '__main__':
    #test
    #format is title, quote
    #result = imgSearch("Jeff Bezos", "jeff bezos and donald trump have met in the #past, although it is not often.")
    #print(result)

    autoCropImages(["bro.jpg"])
    print("done")