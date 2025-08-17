import sys
import os
import glob
from pathlib import Path
from PIL import Image
import os

# Append the inner folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "better_bing_image_downloader", "better_bing_image_downloader"))


from download import downloader

def normalize_images(folder, target_ext=".jpg"):
    folder = Path(folder)
    for img_path in folder.glob("*"):
        if not img_path.is_file():
            continue

        try:
            with Image.open(img_path) as im:
                im = im.convert("RGB")

                new_path = img_path.with_suffix(target_ext)

                im.save(new_path, quality=95)

                if new_path != img_path:
                    os.remove(img_path)

        except Exception as e:
            print(f"⚠️ Skipping {img_path.name}: {e}")

def download(query):
    folder= "media/refImgs"
    for f in os.listdir(folder):
        os.remove(os.path.join(folder, f))
        
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

if __name__=='__main__':
    print(download(['dog']))