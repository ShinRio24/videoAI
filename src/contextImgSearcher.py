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
        img1Path = item
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
        if not os.path.exists(path):
            print(f"Warning: Cannot describe non-existent file: {path}")
            continue
        try:
            desc_text = ollama_prompt_img(imageDescription_template, path)
            described_files.append({"path": path, "description": desc_text})
        except Exception as e:
            print(f"Error generating description for {path}: {e}")
    return described_files

def imgSearch(title, quote, data):
    # 1. Generate the search query
    queryPrompt = queryPrompt_template.format(title=title, quote=quote, data='\n'.join(data))
    response = prompt(queryPrompt, model='gemeni-cli')
    outputQuery = response['query']

    # 2. Define the cache directory for the current query
    cache_dir = os.path.join("/home/riosshin/code/videoAI/media/refImgs", outputQuery)
    metadata_path = os.path.join(cache_dir, "_descriptions.json") # The "card catalog"

    import json
    # 3. Check if the cache directory exists
    if os.path.exists(cache_dir):
        # 4a. CACHE HIT: Use the images from the cache directory
        print(f"'{outputQuery}' descriptions found in cache. Loading from {metadata_path}")
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                available_files = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading cache file {metadata_path}: {e}. Regenerating.")
            # Treat as a cache miss if file is corrupt
            available_files = None 
    else:
        # 4b. CACHE MISS: Generate descriptions and create the cache file
        available_files = None

    
    if available_files is None:
        print(f"'{outputQuery}' descriptions not in cache. Generating...")
        if not os.path.exists(cache_dir):
            print(f"Image directory not found. Downloading images for '{outputQuery}'.")
            os.makedirs(cache_dir)
            image_files = download(outputQuery, 30, cache_dir)
        else:
            print(f"Using existing images from {cache_dir}")
            image_files = glob.glob(os.path.join(cache_dir, "*[.jpg,.jpeg,.png]"))

        if not image_files:
            print(f"[ERROR] No images found or downloaded for query: {outputQuery}")
            return None
        image_files = removeUsedImgs(image_files)

        # This is the slow part that now only runs on a cache miss
        available_files = descriptions(image_files)

        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(available_files, f, ensure_ascii=False, indent=4)
            print(f"Saved descriptions to cache at {metadata_path}")
        except IOError as e:
            print(f"Error saving description cache file: {e}")


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
