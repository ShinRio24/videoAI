import os
import pickle
import shutil
import unicodedata
from .genAudio import genAUDIO
from .combineMedia import combineMedia
from .uploadVideo import uploadVideo

envFolder = "media/editEnvs/"
MASTER_FILE = os.path.join(envFolder, "master.pkl")


# ------------------ Master Helpers ------------------
def loadMaster():
    if not os.path.exists(MASTER_FILE):
        return {}
    with open(MASTER_FILE, "rb") as f:
        return pickle.load(f)

def saveMaster(master):
    with open(MASTER_FILE, "wb") as f:
        pickle.dump(master, f)


# ------------------ Videos Class ------------------
class Videos:
    def __init__(self,  title, videoData, caption="", tags=None):
        self.title = unicodedata.normalize("NFC", title)
        self.videoData = videoData
        self.caption = caption or "ご視聴ありがとうございます！✨..."
        self.tags = tags or ["#ショートストーリー", "#物語", "#感動"]

        master = loadMaster()
        self.code = max(master.keys(), default=0) + 1
        self.path = f"media/editEnvs/{self.code}/preview.mp4"

        # Create environment folder and move media
        self.migrateToFolder()

        # Save metadata to master
        master[self.code] = self
        saveMaster(master)



    def migrateToFolder(self):
        baseDir = os.path.join(envFolder, str(self.code))
        if os.path.exists(baseDir):
            shutil.rmtree(baseDir)
        os.makedirs(baseDir)

        for i, item in enumerate(self.videoData):
            audio = item['audio']
            video = item['path']
            shutil.move(audio, os.path.join(baseDir, os.path.basename(audio)))
            shutil.move(video, os.path.join(baseDir, os.path.basename(video)))
            self.videoData[i]['audio'] = os.path.join(baseDir, os.path.basename(audio))
            self.videoData[i]['path'] = os.path.join(baseDir, os.path.basename(video))


# ------------------ Environment Functions ------------------
def listEnvs():
    master = loadMaster()
    return [f"{code}: {video.title}" for code, video in master.items()]

def openEnv(code):
    master = loadMaster()
    code = int(code)
    if code not in master:
        raise ValueError(f"Environment {code} does not exist")
    return master[code]   # now returns Videos instance

def editEnv(code):
    master = loadMaster()
    code = int(code)
    if code not in master:
        return "Env does not exist.\nValid envs:\n" + "\n".join(listEnvs())

    data = openEnv(code).videoData
    allText = [f"{i}: {x['phrase']}" for i, x in enumerate(data)]
    return "\n".join(allText) + f"\nEnv set to {code}"

def editText(editingEnv, index, newText):
    master = loadMaster()
    env = master[editingEnv]
    data = env.videoData

    if index >= len(data):
        return "Error, index too large"

    data[index]['phrase'] = newText
    genAUDIO(newText, data[index]['audio'])

    # Save back metadata
    master[editingEnv] = env
    saveMaster(master)
    return "Adjusted audio and text"


def removeFrame(editingEnv, index: int) -> str:
    if editingEnv is None: return "❌ No environment selected"
    master = loadMaster()
    # **FIX**: Directly reference the list inside the master object
    video_data = master[editingEnv].videoData

    if not (0 <= index < len(video_data)):
        return f"❌ **Index Error:** Frame {index} is out of bounds."

    frame_to_remove = video_data.pop(index) # pop() removes the item and returns it

    # Delete associated files
    for path_key in ['path', 'audio']:
        file_path = frame_to_remove.get(path_key)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

    # **FIX**: Save the modified master object
    saveMaster(master)
    return f"✅ **Success!** Frame {index} has been removed."

def addFrame(editingEnv,index: int, text: str, temp_image_path: str) -> str:
    if editingEnv is None: return "❌ No environment selected"
    master = loadMaster()
    video_data = master[editingEnv].videoData

    if not (0 <= index <= len(video_data)):
        return f"❌ **Index Error:** Frame {index} is out of bounds for insertion."

    # **FIX**: Create new paths inside the correct environment folder
    baseDir = os.path.join(envFolder, str(editingEnv))
    file_ext = os.path.splitext(temp_image_path)[1]
    # Create a unique name to avoid conflicts
    new_image_name = f"frame_{index}_img_{hash(text)[:6]}{file_ext}"
    new_audio_name = f"frame_{index}_audio_{hash(text)[:6]}.wav"
    
    permanent_image_path = os.path.join(baseDir, new_image_name)
    permanent_audio_path = os.path.join(baseDir, new_audio_name)

    # Move image and generate new audio
    shutil.move(temp_image_path, permanent_image_path)
    genAUDIO(text, permanent_audio_path)

    new_frame = {
        "phrase": text,
        "path": permanent_image_path,
        "audio": permanent_audio_path
    }
    video_data.insert(index, new_frame)

    # **FIX**: Save the modified master object
    saveMaster(master)
    return f"✅ **Success!** New frame added at index {index}."


def cleanEnv(editingEnv):

    shutil.rmtree(os.path.join(envFolder, str(editingEnv)))
    master = loadMaster()
    master.pop(editingEnv, None)
    saveMaster(master)
    editingEnv = None
    return "Cleaned current environment"

# ------------------ Async Video Functions ------------------
async def previewCurrent(editingEnv):

    env = openEnv(editingEnv) 
    finalVideoPath = combineMedia(
        env.title, env.videoData, output_filename=os.path.join(envFolder, f"{editingEnv}/preview.mp4"),preview = True
    )

    return finalVideoPath


def pushVideo(editingEnv):
    env = openEnv(editingEnv)
    videoPath = "media/finalUploads/{}.mp4".format(env.title)
    videoPath = combineMedia(env.title, env.videoData, output_filename=videoPath, preview = False)
    env = openEnv(editingEnv)
    video_id, uploadTime = uploadVideo(
        video_path=videoPath,
        title=env.title
    )
    cleanEnv(editingEnv)


    return f"Video uploaded at: {video_id}\n Scheduled upload at"+str(uploadTime)


import os
import shutil
import pickle

# Make sure envFolder and MASTER_FILE are defined correctly at the top of your file
envFolder = "media/editEnvs/"
MASTER_FILE = os.path.join(envFolder, "master.pkl")

# (Your other functions like loadMaster and saveMaster go here)
# ...

def removeEnv(env_code: int) -> str:
    """
    Finds and deletes the environment folder and its corresponding
    entry from the master.pkl file.
    """
    master = loadMaster()
    env_code = int(env_code) # Ensure the code is an integer for dictionary key lookup

    # --- Step 1: Check if the entry exists in the master file ---
    if env_code not in master:
        return f"❌ Error: Environment code '{env_code}' not found in the master record."

    # --- Step 2: Remove the environment folder from the filesystem ---
    # Note: The path in your original code was different, I've adjusted it
    # to match the `envFolder` variable used elsewhere in the script.
    env_folder_path = os.path.join(envFolder, str(env_code))
    
    if os.path.isdir(env_folder_path):
        try:
            shutil.rmtree(env_folder_path)
            print(f"Successfully removed directory: {env_folder_path}")
        except OSError as e:
            print(f"Error removing folder {env_folder_path}: {e}")
            return f"❌ Error: Failed to remove environment folder. Check logs."
    else:
        print(f"Warning: Directory not found, but proceeding to clean master file: {env_folder_path}")

    # --- Step 3: Remove the entry from the master dictionary ---
    del master[env_code]

    # --- Step 4: Save the updated master dictionary back to the file ---
    saveMaster(master)
    
    return f"🗑️ Successfully removed environment {env_code} and its master record."


if __name__ == '__main__':
    MASTER_FILE = os.path.join(envFolder, "master.pkl")

    with open(MASTER_FILE, "rb") as f:
        master =(pickle.load(f))
    del master[1]

    with open(MASTER_FILE, "wb") as f:
        pickle.dump(master, f)