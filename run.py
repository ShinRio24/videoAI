import sys
print(sys.path)


from TikTok_Voice_TTS import tts, Voice

text = 'Tangerines are smaller and less rounded than the oranges. The taste is considered less sour, as well as sweeter and stronger, than that of an orange. A ripe tangerine is firm to slightly soft, and pebbly-skinned with no deep grooves, as well as orange in color. The peel is thin, with little bitter white mesocarp. All of these traits are shared by mandarins generally. Peak tangerine season lasts from autumn to spring. Tangerines are most commonly peeled and eaten by hand. The fresh fruit is also used in salads, desserts and main dishes. The peel is used fresh or dried as a spice or zest for baking and drinks. Fresh tangerine juice and frozen juice concentrate are commonly available in the United States.'

# arguments:
#   - input text
#   - voice which is used for the audio
#   - output file name
#   - play sound after generating the audio
def run(text, voiceInp,output="output.mp3"):

    voice: Voice | None = Voice.from_string(voiceInp)
    if voice == None:
        raise ValueError("no valid voice has been selected")
    tts(text, voice,output)
        
if __name__ == '__main__':
    run(text,Voice.US_MALE_1)