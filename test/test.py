import sys
sys.path.append("/home/riosshin/code/videoAI")

import src.prompts as prompts_module

# Use dir() to get a list of all names (variables, functions, etc.) inside the module
# We then filter out the special Python "__" variables.
varList = [
    item for item in dir(prompts_module) if not item.startswith('__')
]
print(varList)