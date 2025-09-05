import os
import pickle
import shutil
import unicodedata
from .genAudio import genAUDIO
from .combineMedia import combineMedia
from .uploadVideo import uploadVideo

envFolder = "media/editEnvs/"
MASTER_FILE = os.path.join("tools", "master.pkl")


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

def listEnvsRaw():
    master = loadMaster()
    return [code for code, video in master.items()]

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

def addFrame(editingEnv,index: int, text: str, permanent_image_path: str) -> str:
    if editingEnv is None: return "❌ No environment selected"
    master = loadMaster()
    video_data = master[editingEnv].videoData

    if not (0 <= index <= len(video_data)):
        return f"❌ **Index Error:** Frame {index} is out of bounds for insertion."

    base_name_for_audio = os.path.splitext(permanent_image_path)[0]
    
    # 2. Simply append ".wav" to create the corresponding audio path

    path = genAUDIO(text, base_name_for_audio)


    new_frame = {
        "phrase": text,
        "path": permanent_image_path,
        "audio": path
    }
    video_data.insert(index, new_frame)

    # **FIX**: Save the modified master object
    saveMaster(master)
    return f"✅ **Success!** New frame added at index {index-1}."


def previewCurrent(editingEnv):

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
    removeEnv(editingEnv)


    return f"Video uploaded at: {video_id}\n Scheduled upload at"+str(uploadTime)


import os
import shutil
import pickle

# (Your other functions like loadMaster and saveMaster go here)
# ...

def removeEnv(env_code: int) -> str:
    master = loadMaster()
    env_code = int(env_code)
    if env_code not in master:
        return f"❌ Error: Environment code '{env_code}' not found in the master record."

    env_folder_path = os.path.join(envFolder, str(env_code))
    
    if os.path.isdir(env_folder_path):
        try:
            shutil.rmtree(env_folder_path)
            print(f"Successfully removed directory: {env_folder_path}")
        except OSError as e:
            print(f"Error removing folder {env_folder_path}: {e}")
            return f"❌ Error: Failed to remove environment folder. Check logs."
    else:
        print(f"Warning: Directory not found, but proceeding to clean master file")

    if env_code in master:
        del master[env_code]

    saveMaster(master)
    
    return f"🗑️ Successfully removed environment {env_code} and its master record."


from .llmPrompt import prompt
from .prompts import genTopics_template
def genTopics(idea):
    response = prompt(genTopics_template.format(idea=idea),model="gemeni-cli", printOutput=False)
    return response

from . import scriptPrompts
def getScriptFormat(contentFormat):

    if hasattr(scriptPrompts, contentFormat):
        retrieved_object = getattr(scriptPrompts, contentFormat)
        return contentFormat
    else:
        raise KeyError(f"❌ Error: Variable '{contentFormat}' not found in prompts.py.")
    
def listScriptFormats():
    variable_list = [
    attr for attr in dir(scriptPrompts) if not attr.startswith('__')
]

    return("\n".join(variable_list))


if __name__ == '__main__':
    pass