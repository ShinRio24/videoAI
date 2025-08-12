from tiktok_voice import tts, Voice

text = """1995年、地下鉄サリン事件は日本中を震撼させました。オウム真理教というカルト教団が東京の地下鉄に猛毒のサリンガスを散布し、13人が死亡、数千人が負傷しました。"""

# arguments:
#   - input text
#   - voice which is used for the audio
#   - output file name
#   - play sound after generating the audio
tts(text, Voice.JP_FEMALE_KAORISHOJI, "output.mp3")

