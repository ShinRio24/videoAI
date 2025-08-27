import os
import pickle
import shutil
import unicodedata
from .genAudio import genAUDIO
from .combineMedia import combineMedia
from .uploadVideo import uploadVideo

envFolder = "media/editEnvs/"
MASTER_FILE = os.path.join(envFolder, "master.pkl")
editingEnv = None


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
    def __init__(self, path, title, videoData, caption="", tags=None):
        self.title = unicodedata.normalize("NFC", title)
        self.videoData = videoData
        self.path = path
        self.caption = caption or "ご視聴ありがとうございます！✨..."
        self.tags = tags or ["#ショートストーリー", "#物語", "#感動"]

        master = loadMaster()
        self.code = max(master.keys(), default=0) + 1

        # Create environment folder and move media
        self.migrateToFolder()

        # Save metadata to master
        master[self.code] = self.getAttributes()
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

    def getAttributes(self):
        return {
            "title": self.title,
            "caption": self.caption,
            "tags": self.tags,
            "videoData": self.videoData,
            "path": self.path,
            "code": self.code
        }


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
    global editingEnv
    master = loadMaster()
    code = int(code)
    if code not in master:
        return "Env does not exist.\nValid envs:\n" + "\n".join(listEnvs())

    editingEnv = code
    data = openEnv(code).videoData
    allText = [f"{i}: {x['phrase']}" for i, x in enumerate(data)]
    return "\n".join(allText) + f"\nEnv set to {code}"

def editText(index, newText):
    if editingEnv is None:
        return "No environment selected"
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

def editFrame(index, newFrame):
    if editingEnv is None:
        return "No environment selected"
    env = openEnv(editingEnv)
    data = env.videoData

    if index >= len(data):
        return "Error, index too large"
    if os.path.exists(data[index]['path']):
        os.remove(data[index]['path'])

    shutil.move(newFrame, data[index]['path'])
    return "File adjusted"

def cleanEnv():
    global editingEnv
    if editingEnv is None:
        return "No environment selected"
    
    shutil.rmtree(os.path.join(envFolder, str(editingEnv)))
    master = loadMaster()
    master.pop(editingEnv, None)
    saveMaster(master)
    editingEnv = None
    return "Cleaned current environment"

# ------------------ Async Video Functions ------------------
async def previewCurrent():
    if editingEnv is None:
        return "Not in an environment"

    env = openEnv(editingEnv)  # env is a Videos instance
    finalVideoPath = combineMedia(
        editingEnv, env.videoData, output_filename=os.path.join(envFolder, f"{editingEnv}.mp4")
    )
    video_id = uploadVideo(
        video_path=finalVideoPath,
        title=env.title,
        videoData=env
    )
    return finalVideoPath


async def pushVideo():
    if editingEnv is None:
        return "Not in an environment"

    videoPath = os.path.join(envFolder, f"{editingEnv}.mp4")
    if not os.path.exists(videoPath):
        return "Make sure to preview file, video does not exist"

    env = openEnv(editingEnv)
    video_id = uploadVideo(
        video_path=videoPath,
        title=env['title'],
        videoData=env
    )
    cleanEnv()
    return f"Video uploaded at: {video_id}"


if __name__ =='__main__':
    import pickle
    import os

    # Load the master file
    with open("media/editEnvs/master.pkl", 'rb') as f:
        loaded_data = pickle.load(f)

    # Fix paths for all environments
    for code, env in loaded_data.items():
        for x in range(len(env.videoData)):
            env.videoData[x]['path'] = os.path.basename(env.videoData[x]['path'])
            env.videoData[x]['audio'] = os.path.basename(env.videoData[x]['audio'])  # optional: also fix audio

    # Save back to master.pkl
    with open("media/editEnvs/master.pkl", "wb") as f:
        pickle.dump(loaded_data, f)

    print("Fixed paths in master.pkl")