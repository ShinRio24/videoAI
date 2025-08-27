__all__ = ["gScriptGeneral_template",
           "gScriptCharacter_template",
           "gScriptOrganization_template",
           "gScriptEvent_template",
           "queryPrompt_template",
           "correctIMG_template",
           "imageDescription_template",
           "genTitle"]


genTitle = """
あなたはプロのYouTube動画タイトルクリエイターです。  
以下のトピックをもとに、日本語で短くてキャッチーなYouTubeショート動画のタイトルを1つだけ出力してください。  
絵文字や句読点は使用せず、テキストのみ  

⚠️重要ルール⚠️  
- 出力はタイトルのみ  
- 他の説明・装飾・文章は禁止  
- 20文字以内  
- 必ず日本語のみを使用し英語は禁止  
- 固有名詞も必ずカタカナ表記にする（例：Donald Trump → ドナルド・トランプ）  

トピック: {theme}
"""

gScriptGeneral_template = """
### Instruction:
あなたはプロの日本語YouTubeスクリプトライターです。

タスク：

テーマ「{theme}」について短編YouTubeスクリプトを日本語で作成してください。カリスマ的なYouTuberが話すような自然な口語で、面白く楽しく語ってください。
- まず、与えられたテーマが「人物」「組織」「事件・出来事」のどれに該当するかを判断すること。
- 判断に迷った場合は、最も一般的に知られている分類を優先すること。
  例：歴史上の人物 → 人物、企業や団体 → 組織、災害や犯罪などの事象 → 事件・出来事。
- 分類を誤らないこと。誤りそうな場合は「組織として扱う」「事件として扱う」と明示して扱うこと。
- 分類した上で、以下の指示に従って内容を展開すること。
- テーマが「人物」や「組織」の場合：  
  その人物や組織の生い立ちや設立の経緯、どのようにして今の地位に至ったのか、そして現在どんな影響を与えているのかを中心に語ること。  

- テーマが「事件」や「出来事」の場合：  
  事件がどのように起こったのか、その背景や原因、なぜ起きたのか、社会や人々にどんな影響を及ぼしたのかを掘り下げて語ること。  


要件：
- スクリプト全体は必ず約600文字（±5%以内）
- 各フレーズは平均30文字前後。ただし20〜40文字の揺らぎをつけること
- 各フレーズをJSONリストに分割してください（画像表示用のブレイクポイント）
- 同じ画像が9秒以上表示されないように調整してください
- 各フレーズは文として完結していなくても良いが、全体の流れで意味が通ること
- 必ず最初にフックを置き、その後に本題を明かす
- 箇条書きのように事実を並べず、会話の流れで自然につなげること
- 前後のフレーズをつなぐ「でも」「だから」「実は」「一方で」などを適度に入れること
- 背景・経緯・原因・影響・裏話・意外なポイントを盛り込み、深く掘り下げてください
- トーンはドキュメンタリー風だが楽しく魅力的に
- 禁止事項：
  - 「」や""などの引用符を一切使わないこと
  - 「笑」や特殊記号を使わないこと
- 句読点は「、」と「。」のみ使用可
- スクリプトの冒頭は必ずキャッチーな質問形式で始めること
  （例：知っていますか、実はこんな事実があるんです、など）
- です・ます調は基本だが、すべての文を終わらせない  
- 語尾に「なんです」「だったんですね」など変化をつける  
- 「でも」「だから」「実は」などでつなぎ、会話っぽくする  
- 驚きや感情を少し混ぜて自然に話す


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

gScriptCharacter_template = """
### Instruction:
あなたはプロの日本語YouTubeスクリプトライターです。

タスク：  
テーマ「{theme}」について短編YouTubeスクリプトを作成してください。  
カリスマ的なYouTuberのように自然な口語で、ドキュメンタリー風かつエンタメ性を持たせてください。  

### スタイル・構成
1. フック  
   - 「あなたは知っていますか」「実は」「想像できますか」などで始める  
   - 驚きや好奇心を刺激しインパクトを作る  
   - フックから生い立ちの説明へ自然に移れるように必ず流れを作る

2. 生い立ち・歩み  
3. 権力拡大（組織名や収益・人数など数字を事実に基づき使用）  
4. 二面性・エピソード（善行と残虐さのギャップ、暗殺件数や被害人数など数字も活用）  
5. 結末・影響（逮捕・死亡・現役活動など）  
   - ナレーションが自然になるように、最後は「こうして彼の名前は今も語り継がれている」で結ぶ。
   - 章の切り替えには「ところが」「一方で」「驚くことに」など自然な接続詞を使用  

### 技術要件
- 全体は約300文字（±5%以内）  
- 各フレーズ20〜40文字でJSONリストに分割（画像切替ポイント）  
- 同じ画像が9秒以上続かないように調整  
- 文として完結しなくても流れが通るように  
- 語尾や表現は変化をつける  
- 必須ワード：「秘密」「力」「影響力」「闇」「伝説」  
- 固有名詞は必ずカタカナ表記、英語表記は禁止  
- 句読点は「。」を基本とし「、」は最小限  

### 禁止事項
- 引用符（「」や""）禁止  
- 英語・特殊記号・箇条書き禁止  


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

gScriptOrganization_template = """
"""

gScriptEvent_template = """
"""



queryPrompt_template = """
You are an AI assistant whose job is to generate **one Google search query** to find the most suitable images for a quote in a video.  

Input:  
- Video title (context): {title}  
- Quote to visualize: {quote}  

Rules / Requirements:  

1. The search query must be **exactly one proper noun** from the title or quote.  
2. Only proper nouns present in the input are valid. Do **not** invent, replace, or guess another person, place, organization, or entity.  
3. **Always use the canonical full name** of the proper noun for search.  
   - If the input contains only a partial name (e.g., surname only), expand it to the full official name.  
   - Example: if the title is "Madoff詐欺の闇", the search query must be `"Bernie Madoff"`, not `"Madoff"`.  
4. Do **not** use vague, abstract, or general terms such as "influence", "hidden network", "largest gang", or "power".  
5. If both the title and quote provide multiple proper nouns, pick **only one**. Do **not combine them**.  
6. If the quote is minor, niche, or unrelated to the main context, generate the query **only from the main subject in the title**.  
7. Use **English**, unless the topic is specifically Japanese or Japanese results would be more accurate.  
8. Output must be **strict JSON format only**, using the template below.  


Example:  
Title: 'Madoff詐欺の闇'  
Quote: '世界最大の麻薬王の存在'  
Correct query: 'Bernie Madoff'  
Incorrect query: 'Pablo Escobar'  

Output template:
```json
{{
  "query": "Enter the proper noun from title or quote here"
}}```
"""



correctIMG_template = """
You are an AI assistant tasked with selecting the most suitable image for a quote in a video.

Input:
Quote: {quote}

AI-generated image descriptions (may be vague or abstract, newline-separated): {description}

Task:
Choose a single description that best matches the quote and enhances entertainment value.
Provide a brief reason why it fits.
DO NOT add any special characters such as backslashes (\\) or other escape sequences.

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