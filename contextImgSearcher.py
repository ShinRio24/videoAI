from llmPrompt import prompt
from imageGetter import download
from imageDescription import descriptions

import os
import glob
import difflib
from prompts import *

def imgMatch(input_str,options,files):
    return files[options.index(difflib.get_close_matches(input_str, options, n=1, cutoff=0.0)[0])]

def imgSearch(title, quote, usedImages):

    queryPrompt = queryPrompt_template.format(title=title, quote=quote)

    response = prompt(queryPrompt)
    outputQuery = response['query']

    
    files =download([outputQuery])

    description, files = descriptions(files)

    
    correctIMG = correctIMG_template.format(quote=quote, description=chr(10).join(description), usedImages=chr(10).join(usedImages))
    matchedImage = prompt(correctIMG)
    matchedImage = matchedImage['image_description']
    
    return imgMatch(matchedImage, description,files),matchedImage



if __name__ == '__main__':
    #test
    #format is title, quote
    result = imgSearch("Jeff Bezos", "jeff bezos and donald trump have met in the past, although it is not often.")
    print(result)