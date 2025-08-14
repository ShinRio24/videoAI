import os
import subprocess
import json # Import json to parse ffprobe output

from moviepy import AudioFileClip, VideoFileClip, TextClip, CompositeVideoClip, ImageClip, ColorClip, concatenate_videoclips, CompositeAudioClip,afx
from moviepy.audio import AudioClip
from moviepy.video.tools.cuts import find_video_period
from moviepy import concatenate_audioclips
from pydub import AudioSegment
import os

def ensure_wav(audio_path):
    """
    Converts the input audio to WAV if it isn't already.
    Returns the path to the WAV file.
    """
    if audio_path.lower().endswith(".wav"):
        return audio_path  # Already WAV

    # Convert to WAV
    wav_path = audio_path.rsplit(".", 1)[0] + ".wav"
    if not os.path.exists(wav_path):
        audio = AudioSegment.from_file(audio_path)
        audio.export(wav_path, format="wav")
    return wav_path


def split_duration_weighted(total_duration, text_parts):
    # Use character length (or len(text.split()) for word-based)
    weights = [len(part) for part in text_parts]
    total_weight = sum(weights)

    durations = [(w / total_weight) * total_duration for w in weights]

    start = 0
    timings = []
    for d in durations:
        end = start + d
        timings.append(end-start)
        start = end
    return timings

def addTextBlock(
    videoPath,
    audioPath,
    title,
    caption,
    titleColor ='white',
    titleSize = 100,
    #titleMargin = (0,40),
    titleFont = "fonts/NotoSansJP-SemiBold.ttf",
    titlePosition = ("center", 000),
    captionColor ='white',
    captionSize = 80,
    #captionMargin = (0,40),
    captionFont = "fonts/NotoSansJP-SemiBold.ttf",
    captionPosition = ("center", 1200)
):
    audio = AudioFileClip(audioPath)
    addedImage = ImageClip(videoPath)
    video_width, video_height = (1080, 1920)
    target_text_width = int(video_width * 0.8)
    #https://fonts.google.com/
    #https://fonts.google.com/noto/specimen/Noto+Sans+JP

    
    titleClip = TextClip(
        text = title,
        color= titleColor,
        size=(target_text_width, video_height // 3), 
        method='caption',
        text_align='center',
        font_size = titleSize,
        #margin = titleMargin,
        font = titleFont,
        duration = audio.duration
    ).with_position(titlePosition).with_start(0)

    caption = caption.replace("？", "").replace("。", "").replace("！", "")
    segments = list(caption.split('、'))
    timings = split_duration_weighted(audio.duration, segments)
    tSum=0
    captions = []
    for i,x in enumerate(timings):
        captionClip = TextClip(
            text = segments[i],
            color= captionColor,
            size=(target_text_width, video_height // 3), 
            method='caption',
            text_align='center',
            font_size = captionSize,
            #margin = captionMargin,
            font = captionFont,
            duration = x
        ).with_position(captionPosition).with_start(tSum)
        tSum += x
        captions.append(captionClip)

    canvas_width = 1080
    canvas_height = 1920
    background = ColorClip(size=(canvas_width, canvas_height), color=(0, 0, 0), duration=audio.duration)
    imWidth,imHeight = addedImage.size
    addedImage = addedImage.resized(width=canvas_width)
    imWidth,imHeight = addedImage.size
    maxHeight= 800
    if imHeight>maxHeight:
        addedImage = addedImage.resized(height= maxHeight)

    addedImage = addedImage.with_duration(audio.duration).with_position('center')


    final_clip = CompositeVideoClip([background, addedImage, titleClip]+captions)
    final_clip = final_clip.with_audio(audio)
    return final_clip


def combineMedia(title, imgMatches, background_music="media/bgm/bgm1-escort.wav", output_filename="media/finalUploads/{}.mp4"):

    output_filename = output_filename.format(title)
    allClips = []
    for i,x in enumerate(imgMatches):
        #print(x)
        input_video = x['path']
        input_audio = ensure_wav(x['audio'])
        text_to_add = x['phrase']


        allClips.append(addTextBlock(
            title = title,
            caption =text_to_add,
            videoPath=input_video,
            audioPath=input_audio,

        ))

    final_video=concatenate_videoclips(allClips)

    import math
     # If background music is provided
     #https://dova-s.jp/bgm/play568.html
     #https://www.youtube.com/watch?v=p1O7tSN5_Co
     #https://audiotrimmer.com/
     #https://cloudconvert.com/mp3-to-wav
    if background_music:
        #30% volume loudness
        bgm_clip =AudioFileClip(background_music).with_effects([afx.MultiplyVolume(0.15)])

        num_loops = math.ceil(final_video.duration / bgm_clip.duration)

        # Manually create a new, looped audio clip
        looped_bgm = concatenate_audioclips([bgm_clip] * num_loops)

        # Trim the looped clip to the exact duration of the video
        bgm_clip = looped_bgm.subclipped(0, final_video.duration)
        final_audio = CompositeAudioClip([final_video.audio, bgm_clip])
        final_video = final_video.with_audio(final_audio)

    final_video.write_videofile(output_filename, codec="libx264", fps=30, audio_codec="aac")

    #print(f"\nSuccessfully created '{output_filename}'")
    return output_filename




if __name__ == '__main__':
    import os
    if os.path.exists('output_shorts.mp4'):
        os.remove('output_shorts.mp4')
    combineMedia("世界を動かす巨大企業、知ってる？",[{'phrase':'その影響力、私たちの想像を超えるかも！','audio':'media/audio/au0.mp3','path':'media/refImgs/img0_1.jpg'}])