from pydub import AudioSegment

combined = AudioSegment.empty()
for i in range(9):
    combined += AudioSegment.from_mp3("media/"+str(i)+'.mp3')
combined.export('media/final.mp3', format="mp3")