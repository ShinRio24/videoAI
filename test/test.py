import sys
sys.path.append("/home/riosshin/code/videoAI")

from src.prompts import genScript_template
from src.llmPrompt import prompt


print(prompt(genScript_template.format(theme = "住吉会")))