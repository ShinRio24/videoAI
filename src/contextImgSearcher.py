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
    return files[options.index(difflib.get_close_matches(input_str, options, n=1, cutoff=0.0)[0])]    

def removeUsedImgs(described_files: list[dict]) -> list[dict]:
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
    used_folder = "/home/riosshin/code/videoAI/media/usedImgs"

    # Get a list of already used image paths
    usedFiles = []
    for ext in image_extensions:
        usedFiles.extend(glob.glob(os.path.join(used_folder, f"*{ext}")))

    available_items = []
    for item in described_files:
        img1Path = item['path'] # Get path from the dictionary
        img1 = cv2.imread(img1Path, cv2.IMREAD_GRAYSCALE)
        if img1 is None:
            print(f"Image not readable: {img1Path}")
            continue

        is_used = False
        for img2Path in usedFiles:
            img2 = cv2.imread(img2Path, cv2.IMREAD_GRAYSCALE)
            if img2 is None:
                continue

            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            score, _ = ssim(img1, img2, full=True)

            if score >= 0.9:
                print('Image was used', img1Path)
                is_used = True
                break

        if not is_used:
            # If the image is not a duplicate, add the whole dictionary item
            available_items.append(item)

    return available_items

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

def imgSearch(title, quote, data, usedQuerys):
    queryPrompt = queryPrompt_template.format(title=title, quote=quote, data='\n'.join(data))
    response = prompt(queryPrompt, model='gemeni-cli')
    outputQuery = response['query']

    if outputQuery in usedQuerys:
        # 1. HIT: Get the FULL list of described files from the cache.
        # The cache now contains: [{'path': '...', 'description': '...'}, ...]
        described_files = usedQuerys[outputQuery].copy()
        print(f"'{outputQuery}' found in cache, using stored descriptions.")
    else:
        # 2. MISS: Download files, generate descriptions ONCE, and cache them.
        print(f"'{outputQuery}' not in cache. Downloading and generating descriptions.")
        
        # a. Download a fresh list of file paths.
        fresh_files = download([outputQuery], 15)
        
        # b. Generate descriptions and create the structured data.
        #    This now happens only when a query is new.
        described_files = descriptions(fresh_files) # NOTE: descriptions() must be updated.
        
        # c. Save the FULL, original list of described files to the cache.
        usedQuerys[outputQuery] = described_files.copy()

    # 3. Filter the list of described files against the master "used" folder.
    #    NOTE: removeUsedImgs() must be updated to handle this new data structure.
    available_files = removeUsedImgs(described_files)
    print(f"{len(available_files)} usable images remain after filtering.")

    if not available_files:
        print("[ERROR] No usable images found after filtering. Cannot proceed.")
        return None, usedQuerys


    description_list = [item['description'] for item in available_files]
    
    correctIMG_prompt = correctIMG_template.format(quote=quote, description='\n'.join(description_list))
    matchedImage_desc = prompt(correctIMG_prompt)['image_description']
    
    # 5. Find the final matching image.
    #    NOTE: imgMatch() must be updated.
    matchedImage = imgMatch(matchedImage_desc, available_files)

    return matchedImage, usedQuerys



if __name__ == '__main__':
    #test
    #format is title, quote
    #result = imgSearch("Jeff Bezos", "jeff bezos and donald trump have met in the #past, although it is not often.")
    #print(result)

    autoCropImages(["bro.jpg"])
    print("done")