import sys
import os
import glob
from pathlib import Path
from PIL import Image
import requests
import json
from dotenv import load_dotenv
import base64

load_dotenv()
API_KEY = os.getenv("SEARCHKEY", "")

# --- Replace with your actual credentials ---
CSE_ID = "c6fcff51d3b604e3b"                                              


# Add Google-Image-Scraper folder to sys.path
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "../Google-Image-Scraper")))

from customScrape import customScrape


folder= "media/refImgs"

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


def downloadGoogle(query, imgCount):
    response = customScrape(query, imgCount)

    return response
                                                     

import requests
from pathlib import Path

def _download_image_from_url(url: str, filepath: str) -> bool:
    headers = {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
 

        response = requests.get(url, headers=headers, stream=True, timeout=(5, 15))
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {url}: {e}")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred for {url}: {e}")
        return False


def imgSearch(query: str, img_count: int, cachePath) -> list[str]:
    """
    Performs a Google image search, downloads the results, and returns their local file paths.
    This function now replaces the functionality of `downloadGoogle`.
    """
    print(f"🔎 Searching for {img_count} images of '{query}'...")
    downloaded_paths = []
    
    # The API is paginated, so we loop to get the desired number of images
    for i in range(0, img_count, 10):
        num_to_fetch = min(10, img_count - i)
        start_index = i + 1
        
        params = {
            'q': query,
            'cx': CSE_ID,
            'key': API_KEY,
            'searchType': 'image',
            'num': num_to_fetch,
            'start': start_index,
            'safe': 'high'
        }

        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            response.raise_for_status()
            data = response.json()

            if 'items' not in data:
                print("No more results found.")
                break

            for idx, item in enumerate(data['items']):
                img_url = item.get('link')
                if not img_url:
                    continue
                
                # Create a simple, clean filename
                file_ext = Path(img_url).suffix or '.jpg'
                if len(file_ext) > 5: file_ext = '.jpg' # handle long/invalid extensions
                
                local_filepath = os.path.join(cachePath, f"img_{len(downloaded_paths):03d}{file_ext}")
                
                if _download_image_from_url(img_url, local_filepath):
                    downloaded_paths.append(local_filepath)

        
        # --- MODIFIED ERROR HANDLING BLOCK ---
        except requests.exceptions.RequestException as e:
            # Now 'e' is defined and contains the specific error details
            print(f"❌ A network error occurred: {e}")
            raise
    
    print(f"✅ Successfully downloaded {len(downloaded_paths)} images.")
    return downloaded_paths

def download(query, imgCount, cachePath):

    try:
        paths = imgSearch(query, imgCount, cachePath)

    except:
        print(paths)
        downloadGoogle(query,imgCount, cachePath)

    paths = normalize_images(paths)
    return paths

if __name__=='__main__':
    print(download('dog',10))