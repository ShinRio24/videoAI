from moviepy import AudioFileClip

clip = AudioFileClip("media/audio/au0.mp3")
print(clip.duration)  # should be > 0