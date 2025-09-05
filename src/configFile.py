import json
from datetime import datetime
configDir = "tools/config.json"
outputDir = "outputLogs/"
class Config:
    def __init__(self, filename=configDir):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.data = json.load(f)  
        
        for key, value in self.data.items():
            setattr(self, key, value)

    def getConfig(self):
        return self.data
    
    def nOutputStream(self):
        curDatTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.data["curOutputStream"]=outputDir+curDatTime+".txt"
        with open(self.data["curOutputStream"], "w") as file:
            file.write('\n')
        
        with open(configDir, "w") as json_file:
            json.dump(self.data, json_file, indent=4)
    
    def outputStream(self, output):
        output = str(output)
        with open(self.data["curOutputStream"], 'a') as file:
            file.write(output)

    def update_and_save(self, key, value):
        print(f"🔄 Updating '{key}' from '{self.data.get(key)}' to '{value}'...")
        self.data[key] = value
        setattr(self, key, value)
        self.save()

    def save(self):
        with open(self.filename, "w") as json_file:
            json.dump(self.data, json_file, indent=4)