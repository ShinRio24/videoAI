import sys
import os
import glob

# Append the inner folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "better_bing_image_downloader", "better_bing_image_downloader"))


from download import downloader


def download(query):
    folder = "media/refImgs"

    files = glob.glob(os.path.join(folder, "*"))
    for f in files:
        os.remove(f)

    for i,x in enumerate(query):
        downloader(
            query=x,
            limit=50,
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
    return glob.glob(os.path.join(folder, "*"))