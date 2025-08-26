from .communicator import postToTelegram
from .genAudio import genAUDIO
import pickle
import os
import shutil

envFolder ="media/editEnvs/"
editingEnv = None

class Videos:

    def __init__(self, 
                 path, 
                 title, 
                 videoData,
                 caption="""ご視聴ありがとうございます！✨
ご意見や感想がありましたら、ぜひコメントで教えてください。いつもとても嬉しく、参考にさせていただいています😊""", 
                 tags= ["#ショートストーリー", "#物語", "#感動", "#日常", "#心に響く", "#面白い", "#ストーリーテリング", "#短編動画", "#共感", "#泣ける", "#笑える", "#感情", "#話題", "#TikTokJapan", "#tiktok短編"]):
        postToTelegram(path)
        self.path = path
        self.title = title
        self.caption = caption
        self.tags = tags
        self.videoData = videoData

        self.migrateToCustomFile()
        self.saveVideo()

    def migrateToCustomFile(self):
        baseDir = envFolder+self.title
        if os.path.exists(baseDir):
            shutil.rmtree(baseDir)
        os.makedirs(baseDir)

        for f in self.videoData:
            audio = f['audio']
            path = f['path']
            shutil.move(audio, os.path.join(baseDir, os.path.basename(audio)))
            shutil.move(path, os.path.join(baseDir, os.path.basename(path)))
            self.videoData['audio']=os.path.join(baseDir, os.path.basename(audio))
            self.videoData['path']=os.path.join(baseDir, os.path.basename(path))

def saveVideo(title):
    with open(envFolder+title+".pkl", "wb") as f:
        pickle.dump(self, f)

def listEnvs():
    dirs = [d for d in os.listdir(envFolder) if os.path.isdir(os.path.join(envFolder, d))]
    global editingEnv
    editingEnv = None
    return dirs

def editEnv(title):
    if title in listEnvs():
        global editingEnv
        editingEnv = title
    else:
        return "env does not exist"
    data = openEnv(title)
    allText = []
    for i,x in enumerate(data):
        allText.append(str(i)+": "+x['phrase'])
    
    return '\n'.join(allText)+"\n env set to "+title

def openEnv(title):
    with open(envFolder+title+".pkl", "rb") as f:
        return pickle.load(f)

def editFrame(index, newFrame):
    data = openEnv(editingEnv)
    if index+1>len(data):
        return "error, index too large"    
    if os.path.exists(data[index]['path']):
        os.remove(data[index]['path'])

    shutil.move(newFrame, data[index]['path'])
    return 'file adjusted'

def editText(index, newText):
    data = openEnv(editingEnv)
    if index+1>len(data):
        return "error, index too large"    
    data[index]['phrase']= newText
    genAUDIO(newText,data[index]['audio'])
    self.saveVideo()

    return "Adjusted audio and text"


#might have to make this async cus it takes a while
def pushVideo()