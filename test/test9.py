import sys
import os

# Use the WSL-resolved Linux path
videoAI_path = "/home/riosshin/code/videoAI"
sys.path.append(videoAI_path)



output = """ ```json
{
  "Script": [
    "World Cup is back everyone gather round",
    "The drama starts now let's dive into some highlights from this tournament",
    "Argentina taking on Croatia in a blockbuster semi final game right Messi could be playing his last one",
    "France they always deliver but Brazil fans are devastated seeing them knocked out early",
    "England beating Germany that was huge talk about an upset the Three Lions deserved it though",
    "Remember the scenes from group stage matches like Morocco's giant killing of Spain or Croatia stunning Serbia",
    "Every game has a story today someone's dream is ending tomorrow another team stepping up",
    "Who will you be cheering for tonight let me know below"
  ]
}
```"""

from llmPrompt import extract_json_between_markers
import os
import glob 


print(extract_json_between_markers(output))