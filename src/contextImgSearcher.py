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
    print(input_str,options, files)
    return files[options.index(difflib.get_close_matches(input_str, options, n=1, cutoff=0.0)[0])]['path']

def removeUsedImgs(described_files: list[dict]) -> list[dict]:
    # This function will now deduplicate images within the provided list
    unique_files = []
    seen_images = []

    for item in described_files:
        img1Path = item['path']
        img1 = cv2.imread(img1Path, cv2.IMREAD_GRAYSCALE)
        if img1 is None:
            print(f"Image not readable: {img1Path}")
            continue

        is_duplicate = False
        for seen_img_path in seen_images:
            img2 = cv2.imread(seen_img_path, cv2.IMREAD_GRAYSCALE)
            if img2 is None:
                continue

            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            score, _ = ssim(img1, img2, full=True)

            if score >= 0.9:
                print(f'Found duplicate image: {img1Path} is similar to {seen_img_path}')
                is_duplicate = True
                break

        if not is_duplicate:
            unique_files.append(item)
            seen_images.append(img1Path)

    return unique_files

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

def descriptions(file_paths: list[str]) -> list[dict]:
    described_files = []
    for path in file_paths:
        # Your existing logic to generate a description for a single path
        desc_text = ollama_prompt_img(imageDescription_template, path)
        
        # Append the structured dictionary to the list
        described_files.append({
            "path": path,
            "description": desc_text
        })
        
    return described_files

def imgSearch(title, quote, data):
    # 1. Generate the search query
    queryPrompt = queryPrompt_template.format(title=title, quote=quote, data='\n'.join(data))
    response = prompt(queryPrompt, model='gemeni-cli')
    outputQuery = response['query']

    # 2. Define the cache directory for the current query
    cache_dir = os.path.join("/home/riosshin/code/videoAI/media/refImgs", outputQuery)

    # 3. Check if the cache directory exists
    if os.path.exists(cache_dir):
        # 4a. CACHE HIT: Use the images from the cache directory
        print(f"'{outputQuery}' found in cache. Using images from {cache_dir}")
        image_files = glob.glob(os.path.join(cache_dir, "*"))
    else:
        # 4b. CACHE MISS: Download new images and cache them
        print(f"'{outputQuery}' not in cache. Downloading images.")
        os.makedirs(cache_dir)
        # The download function now needs to save to the specific directory
        image_files = download(outputQuery, 30, cache_dir) # Pass the query and the cache_dir
        

    # 5. Describe the images
    described_files = descriptions(image_files)

    # 6. Deduplicate the images for the current query
    
    print(f"{len(available_files)} usable images remain after filtering.")

    if not available_files:
        print("[ERROR] No usable images found after filtering. Cannot proceed.")
        return None

    # 7. Find the best image
    description_list = [item['description'] for item in available_files]
    correctIMG_prompt = correctIMG_template.format(quote=quote, description='\n'.join(description_list))
    matchedImage_desc = prompt(correctIMG_prompt)['image_description']
    matchedImage = imgMatch(matchedImage_desc, description_list, available_files)

    return matchedImage



if __name__ == '__main__':
    #test
    #format is title, quote
    #result = imgSearch("Jeff Bezos", "jeff bezos and donald trump have met in the #past, although it is not often.")
    #print(result)

    autoCropImages(["bro.jpg"])
    print("done")
