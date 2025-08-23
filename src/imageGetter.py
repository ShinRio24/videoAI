import sys
import os
import glob
from pathlib import Path
from PIL import Image
import os

# Append the inner folder to sys.path
#sys.path.append(os.path.join(os.path.dirname(__file__), "better_bing_image_downloader", "better_bing_image_downloader"))

import sys
import os

# Add Google-Image-Scraper folder to sys.path
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "../Google-Image-Scraper")))

from customScrape import customScrape


folder= "media/refImgs"
#from download import downloader

def normalize_images(paths, target_ext=".jpg"):

    normalized_paths = []

    for img_path in paths:
        img_path = Path(img_path) 

        try:
            with Image.open(img_path) as im:
                im = im.convert("RGB")

                new_path = img_path.with_suffix(target_ext)

                im.save(new_path, quality=95)

                if new_path != img_path:
                    os.remove(img_path)
                
                normalized_paths.append(str(new_path)) 

        except Exception as e:
            print(f"⚠️ Skipping {img_path}: {e}")

    return normalized_paths

def downloadBing(query):
        
    for i,x in enumerate(query):
        downloader(
            query=x,
            limit=15,
            output_dir=folder,
            adult_filter_off=True,
            force_replace=False,
            timeout=60,
            filter="photo",  # Options: "line", "photo", "clipart", "gif", "transparent"
            verbose=True,
            badsites=["stock.adobe.com", "shutterstock.com"],
            name="img"+str(i),
            max_workers=8  # Parallel downloads
        )

    normalize_images(folder)


    return glob.glob(os.path.join(folder, "*"))

def downloadGoogle(query, imgCount):
    response = customScrape(query, imgCount)

    return response


def download(query, imgCount):
    for f in os.listdir(folder):
        os.remove(os.path.join(folder, f))

    paths = downloadGoogle(query, imgCount)
    paths = normalize_images(paths)
    return paths

if __name__=='__main__':
    print(download('dog'))