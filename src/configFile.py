import json
from datetime import datetime
configDir = "config.json"
class Config:
    def __init__(self, filename=configDir):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.data = json.load(f)  

    def getConfig(self):
        return self.data
    
    def nOutputStream(self):
        curDatTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.data["curOutputStream"]=self.data['outputStream']+curDatTime+".txt"
        with open(self.data["curOutputStream"], "w") as file:
            file.write('\n')
        
        with open(configDir, "w") as json_file:
            json.dump(self.data, json_file, indent=4)
    
    def outputStream(self, output):
        output = str(output)
        with open(self.data["curOutputStream"], 'a') as file:
            file.write(output)

        self.data['outputStream']