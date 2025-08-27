import json
import re

def extract_json_between_markers(llm_output):
    # Regular expression pattern to find JSON content between ```json and ```
    s=llm_output
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    # Remove backslashes
    s = s.replace("\\", "")
    # Remove stray punctuation like ."
    s = re.sub(r'\.\s*"', '.', s)
    # Remove control characters
    s = re.sub(r'[\x00-\x1F\x7F]', '', s)
    llm_output=s

    json_pattern = r"```json(.*?)```"
    matches = re.findall(json_pattern, llm_output, re.DOTALL)

    if not matches:
        # Fallback: Try to find any JSON-like content in the output
        json_pattern = r"\{.*?\}"
        matches = re.findall(json_pattern, llm_output, re.DOTALL)

    for json_string in matches:
        json_string = json_string.strip()
        try:
            parsed_json = json.loads(json_string)
            return parsed_json
        except json.JSONDecodeError:
            # Attempt to fix common JSON issues
            try:
                # Remove invalid control characters
                json_string_clean = re.sub(r"[\x00-\x1F\x7F]", "", json_string)
                parsed_json = json.loads(json_string_clean)
                return parsed_json
            except json.JSONDecodeError:
                continue  # Try next match

    return None 


llm_output = """
```json
{
  "Script": [
    "チャールズ・マンソン…想像できますか？　闇に潜むカリスマ。",
    "彼は、アメリカを震撼させた男。秘密裏に組織を拡大した。",
    "『ヘイワースグループ』…なんと100人以上の信者を集めたのです。",
    "ところが、彼はただの狂信者ではなかった。”,
    "彼は、大富豪たちから多額の資金を集め、ビジネスを手助けする。",
    "しかし、彼の秘密裏の活動は、時に残虐に転落していく。",
    "数々の暗殺事件…被害者は10人以上。”,
    "彼は、富と権力のための道具として、人命を軽視した。",
    "彼は、捕らえられ、終身刑を受けた。しかし、その伝説は終わらなかった。",
    "彼の思想は、今日でも一部に受け継がれている。",
    "チャールズ・マンソン…闇に潜むカリスマ。彼の影響力は、今も語り継がれている。"
  ]
}
```
"""
print(extract_json_between_markers(llm_output))