__all__ = ["genScript_template", "queryPrompt_template", "correctIMG_template","imageDescription_template"]

genScript_template = """
### Instruction:
あなたはプロの日本語YouTubeスクリプトライターです。

タスク：
テーマ「{theme}」について短編YouTubeスクリプトを日本語で作成してください。カリスマ的なYouTuberが話すような自然な口語で、面白く楽しく語ってください。

要件：
- スクリプト全体は必ず約600文字（±5%以内）
- 各フレーズは30文字前後、長くても50文字以内
- 各フレーズをJSONリストに分割してください（画像表示用のブレイクポイント）
- 同じ画像が9秒以上表示されないように調整してください
- 各フレーズは文として完結していなくても良いが、全体の流れで意味が通ること
- 必ず最初にフックを置き、その後に本題を明かす
- イントロや挨拶は不要、すぐに本題へ
- 背景・経緯・原因・影響・裏話・意外なポイントを盛り込み、深く掘り下げてください
- トーンはドキュメンタリー風だが楽しく魅力的に
- **禁止事項：**
  - 「」や""などの引用符を一切使わないこと
  - 「笑」や特殊記号を使わないこと
  - JSON以外の出力をしないこと
- 句読点は「、」と「。」のみ使用可

出力形式：
必ず次のフォーマットに従ってください。他のテキストは絶対に出力しないでください。

正しい形式の例：
json```
{{
  "Script": [
    "文1",
    "文2",
    "文3"
  ]
}}```
"""

queryPrompt_template = """
You are an AI assistant whose role is to generate Google search queries to find the most suitable images for quotes in a video.

Given information:
Video title (context): {title}
Quote to visualize: {quote}

Instructions:
Create a single search query that is highly relevant to the quote, the video title, and the specific subject.
Always include some reference to the specific subject from the title.
In some cases, if the quote adds important context about the subject, include it as well.
Example: If the title is “Trump” and the quote is referencing “G7 summit,” it makes most sense to find an image of the G7 summit, possibly with all leaders present to clarify context.
The search query should be specific enough to get meaningful images but not so narrow that almost no results appear.
The search query can be in English or Japanese, whichever is likely to yield the best results.

Output must be in strict JSON format only, using the following template:

```json
{{
  "query": "Enter the generated search query here"
}}
```
"""

correctIMG_template = """
あなたはAIアシスタントで、動画内の引用文やセクションに最適な画像を選択する役割を持っています。

与えられる情報：

- 表現したい引用文：{quote}
- 自動生成された画像の説明リスト（不明瞭または抽象的な場合があります）。各フレーズは改行で区切られています：
{description}

指示：

1. 引用文に最も合致し、かつエンタメ価値を高める単一の画像説明を選択してください。
2. 選択理由は **JSON内の "reason" フィールド** に必ず記入してください。
3. JSONオブジェクト以外には何も出力しないでください。コメント、余計な改行、マークダウン、確認文は出さないでください。
4. JSONオブジェクトは必ず以下の3つのフィールドを含めてください：
   - "phrase": 元の引用文
   - "image_description": 選択した画像説明。詳細を維持しつつ、簡潔にまとめ、**おおよそ20文字前後** にしてください。
   - "reason": その画像が引用文に合う理由を簡潔に説明し、**おおよそ20文字前後** にしてください。

出力形式（JSONのみ、他のテキストなし）：

```json
{{
    "phrase": "引用文をここに入れる",
    "image_description": "選択した画像説明をここに入れる",
    "reason": "この画像が引用文に合う理由を短く説明する"
}}
```
"""


correctIMG_template = """
You are an AI assistant tasked with selecting the most suitable image for a quote in a video.

Input:
Quote: {quote}

AI-generated image descriptions (may be vague or abstract, newline-separated): {description}

Task:
Choose a single description that best matches the quote and enhances entertainment value.
Provide a brief reason why it fits.
Output only a JSON object with exactly these two fields:
"image_description": chosen description
"reason": why it fits, concise (~20 characters)
If descriptions lack names, assume the subject relates to the quote. Focus on how it is portrayed and its visual appeal.

Output format:
```json
{{
    "image_description": "your selected description here",
    "reason": "your reason here"
}}
```
"""

imageDescription_template = """
Describe the content of this image in plain text, in a single paragraph.
Be descriptive about what is happening, the style of the image, and any noticeable details.
Do not mention names unless you are completely certain.
"""