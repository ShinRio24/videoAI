from llmPrompt import prompt
from llmPrompt import extract_json_between_markers
def genTopics(idea):
    script_prompt = (f"""
    You are a professional Japanese YouTuber.
Please generate a list of 10 topics for a YouTube short, designed to be entertaining, fun to watch, and natural-sounding, as if spoken by a charismatic YouTuber. The theme of the topics should be related to the idea: {idea}

Make sure the topics:
- Are engaging and suitable for a short video format
- Can be easily understood by a wide audience
- Have the potential to go viral or attract viewers
- Are relevant to current trends or interests
- are output in japanese
- Keep the output concise and focused on the main idea, making the topics around 10 characters maximum
-could just add names of people, places, or things related to the main idea, but if so, make sure to add context, such as "the history of" or "the best" or "the top 10", or by formatting it as idea, topic or something to make sure they also see the relation to the idea

Example:
Main idea: "日本食"
Topics:
1. 寿司
2. ラーメンの歴史
3. おにぎりの種類
4. 和菓子の作り方
5. 日本の伝統的な朝食
6. 日本の食文化の変遷
7. 人気の日本のスナック
8. 日本の飲み物の種類
9. 日本の食材の特徴
10. 海外の食事マナー

The output should be in the following JSON format:
{{
  "Topics": [
      "寿司",
    "ラーメンの歴史",
    "おにぎりの種類",
    和菓子の作り方
    "日本の伝統的な朝食",
    "人気の日本のスナック",
    "日本の飲み物の種類",
    "日本の食材の特徴",
    "海外の食事マナー"
    ]}}
    ONLY RETURN THE RAW JSON FILE, DO NOT REUTURN ANYTHING ELSE""")
    
    response = prompt(script_prompt)
    #print(response)


    
    genList= extract_json_between_markers(response)
    print(genList["Topics"])
    return genList["Topics"]

import sys
if __name__ == "__main__":
    title = sys.argv[1]
    topics = genTopics(title)