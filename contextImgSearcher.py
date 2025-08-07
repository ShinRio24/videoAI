from llmPrompt import prompt
from llmPrompt import extract_json_between_markers
from imageGetter import download
from imageDescription import descriptions

import os
import glob
import difflib


def imgMatch(input_str,options,files):
    return files[options.index(difflib.get_close_matches(input_str, options, n=1, cutoff=0.0)[0])]

def imgSearch(title, quote):

    queryPrompt = f"""
     You are an AI assistant tasked with generating a google prompt to find the best image to go with a quote within a video

You are given:

The title of the video the quote is in (context). As given here: {title}

The actual quote. As given here: {quote}

Make sure the search is broad enough so that the query finds a relevant picutre, but is specific enough to acompany the quote.

Here is the output format
json
{{
  "query": "output query"
}}
"""

    response = prompt(queryPrompt)
    outputQuery = extract_json_between_markers(response)['query']

    print(outputQuery)
    files =download([outputQuery])
    print(files)

    description, files = descriptions(files)

    correctIMG =f"""You are an AI assistant tasked with selecting the best image for a given quote or section of a film.

You are given:

The quote you are trying to find the best image for. As given here: {quote}

A list of image descriptions generated from automatic tools or captions (these may not always be perfectly clear or explicit). Each phrase is separated by a new line. As given here 
{chr(10).join(description)}

Your job is to find the image that best matches the quote, and adds entertainment value to the viewer


Keep in mind the descriptions may:
Doesn't explicitly mention the exact name or subject

Refers to the subject indirectly or abstractly

Describes the scene, person, or activity related to the phrase

Your matches should be based on understanding of context, implied meaning, and background knowledge.

For example:

If a script says “Jeff Bezos started Amazon in his garage,” and an image description says “a man in a small room surrounded by boxes,” you should correctly infer that the image matches, even if it doesn’t name him.

Return the best matching description for the quote
additionally return A short explanation of why this match makes sense (including inferred or indirect context)

Avoid choosing irrelevant or misleading images just because they contain a keyword. Prioritize semantic relevance, narrative flow, and viewer clarity.
Example Format for Output
```json
{{
  
    "phrase": "Jeff Bezos started Amazon in his garage.",
    "image_description": "A man working on a computer in a cluttered garage.",
    "reason": "The image indirectly represents Jeff Bezos’ early Amazon days, matching the garage startup context."
}}   ```"""

    response = prompt(correctIMG)
    matchedImage = extract_json_between_markers(response)
    matchedImage = matchedImage['image_description']
    print(matchedImage)
    
    return imgMatch(matchedImage, description,files)



    #return image path

def notUsed():

    #currently search 50 of each query, find best match
    download(['jeff bezos', 'amazon'])

    folder = "media/refImgs"

    files = glob.glob(os.path.join(folder, "*"))
    description, files = descriptions(files)
    
    correctIMG = f"""
        You are an AI assistant tasked with selecting the best image for each segment of a video script.

You are given:

A list of script phrases or sentences (typically short video narration lines). Each phrase is separated by a new line. As given here: {chr(10).join(data)}

A list of image descriptions generated from automatic tools or captions (these may not always be perfectly clear or explicit). Each phrase is separated by a new line. As given here {chr(10).join(description)}

Your job is to match each script segment with the most relevant image, even if the image description:

Doesn't explicitly mention the exact name or subject

Refers to the subject indirectly or abstractly

Describes the scene, person, or activity related to the phrase

Your matches should be based on understanding of context, implied meaning, and background knowledge.

For example:

If a script says “Jeff Bezos started Amazon in his garage,” and an image description says “a man in a small room surrounded by boxes,” you should correctly infer that the image matches, even if it doesn’t name him.

For each phrase, return:

The best-matching image description

A short explanation of why this match makes sense (including inferred or indirect context)

Avoid choosing irrelevant or misleading images just because they contain a keyword. Prioritize semantic relevance, narrative flow, and viewer clarity.
Example Format for Output
json
[
  {{
    "phrase": "Jeff Bezos started Amazon in his garage.",
    "image_description": "A man working on a computer in a cluttered garage.",
    "reason": "The image indirectly represents Jeff Bezos’ early Amazon days, matching the garage startup context."
  }},
  {{
    "phrase": "Apple changed the way we listen to music.",
    "image_description": "White earbuds plugged into a phone showing a music app.",
    "reason": "The description reflects Apple's impact on music through products like the iPod and iPhone, even if Apple isn't named."
  }}
]
    """

    response = prompt(correctIMG)
    imgMatches = extract_json_between_markers(response)
    print(imgMatches)


    
    for i,x in enumerate(imgMatches):
        x['audio'] ="media/au"+str(i)+".mp3"

        genAUDIO(x['phrase'],"media/au"+str(i))
        x['path']=imgMatch(x['image_description'], description,files)



if __name__ == '__main__':
    #test
    #format is title, quote
    result = imgSearch("Jeff Bezos", "jeff bezos and donald trump have met in the past, although it is not often.")
    print(result)