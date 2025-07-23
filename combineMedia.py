import os
import subprocess
import json # Import json to parse ffprobe output

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, AudioFileClip, ColorClip, concatenate_videoclips
from moviepy.video.tools.subtitles import SubtitlesClip

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


def combineMedia(title, imgMatches,output_filename="media/final_video.mp4"):
    n_pairs = len(imgMatches)


    allClips = []
    for i,x in enumerate(imgMatches):
        #basePath = f'media/'
        input_video = x['path']
        input_audio = x['audio']
        text_to_add = x['phrase']


        allClips.append(addTextBlock(
            title = title,
            caption =text_to_add,
            videoPath=input_video,
            audioPath=input_audio,

        ))

    final_video=concatenate_videoclips(allClips)
    final_video.write_videofile(output_filename, codec="libx264", fps=30, audio_codec="aac")

    print(f"\nSuccessfully created '{output_filename}'")





if __name__ == '__main__':
    import os
    if os.path.exists('output_shorts.mp4'):
        os.remove('output_shorts.mp4')
    combineMedia("世界を動かす巨大企業、知ってる？",[{'phrase':'その影響力、私たちの想像を超えるかも！','audio':'media/au0.mp3','path':'media/refImgs/img0_1.jpg'}])