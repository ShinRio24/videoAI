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

⚠️重要ルール⚠️  
- 出力はタイトルのみ  
- 他の説明・装飾・文章は禁止  
- 20文字以内  

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
テーマ「{theme}」について短編YouTubeスクリプトを日本語で作成してください。  
カリスマ的なYouTuberが話すような自然な口語で、面白く楽しく語ってください。  

### スタイル・トーン
- カリスマ的なYouTuberのような自然な口語
- ドキュメンタリー風＋エンタメ性あり
- 驚きとワクワクを混ぜ、分かりやすく整理された流れ
- できるだけ句読点の「、」は控えめにし文章を自然につなぐ


### 構成
1. フック
   - 「あなたは知っていますか」「実は」「想像できますか」で始める
   - 誇張した表現でインパクトを作る（例：世界最大の麻薬王）
   - 驚きや好奇心を一気に刺激
2. 生い立ち・歩み
   - 幼少期や出自から闇社会に入るまで
3. 権力拡大
   - 秘密や闇の力を築き、国家や社会への影響力を強調
4. 二面性・エピソード
   - 善行と残虐さのギャップ
   - 意外な人間性や逸話
5. 結末・影響
   - 最期と、その後も残る伝説や影響力

### 技術要件
- 全体は約300文字（±5%以内）
- 各フレーズ20〜40文字、平均30文字前後
- JSONリストで分割（画像切替ポイント）
- 同じ画像が9秒以上続かないように調整
- フレーズは文として完結しなくても、全体の流れで意味が通ること
- 語尾や表現は変化をつけ、単調にならないようにする
- 必須ワード：「秘密」「力」「影響力」「闇」「伝説」
- 可能な限り「、」を控え文を自然につなぐ


### 禁止事項
- 「」や""などの引用符
- 「笑」や特殊記号
- 箇条書き的な事実の羅列
- 句読点は「。」を基本とする



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
### Instruction:
あなたはプロの日本語YouTubeスクリプトライターです。

タスク：
テーマ「{theme}」について短編YouTubeスクリプトを日本語で作成してください。カリスマ的なYouTuberが話すような自然な口語で、面白く楽しく語ってください。
-まず、与えられたテーマが「人物」「組織」「事件・出来事」のどれに該当するかを判断すること。
-判断に迷った場合は、最も一般的に知られている分類を優先すること。
例：歴史上の人物 → 人物、企業や団体 → 組織、災害や犯罪などの事象 → 事件・出来事。
-分類を誤らないこと。誤りそうな場合は「組織として扱う」「事件として扱う」と明示して扱うこと。
-分類した上で、以下の指示に従って内容を展開すること。

組織の場合：
その組織の誕生や設立のきっかけ、どんな理念や背景があったのか、どうやって勢力や影響力を広げたのか、そして今どんな影響を与えているのかを中心に語ること。

要件
-スクリプト全体は必ず約600文字（±5%以内）
-各フレーズは平均30文字前後。ただし20〜40文字の揺らぎをつけること
-各フレーズをJSONリストに分割してください（画像表示用のブレイクポイント）
-同じ画像が9秒以上表示されないように調整してください
-各フレーズは文として完結していなくても良いが、全体の流れで意味が通ること
-必ず最初にフックを置き、その後に本題を明かす
-箇条書きのように事実を並べず、会話の流れで自然につなげること
-前後のフレーズをつなぐ「でも」「だから」「実は」「一方で」などを適度に入れること
-背景・経緯・原因・影響・裏話・意外なポイントを盛り込み、深く掘り下げてください
-トーンはドキュメンタリー風だが楽しく魅力的に

禁止事項
-「」や""などの引用符を一切使わないこと
-「笑」や特殊記号を使わないこと
-句読点は「、」と「。」のみ使用可

口調ルール
-スクリプトの冒頭は必ずキャッチーな質問形式で始めること
（例：知っていますか、実はこんな事実があるんです、など）
-です・ます調は基本だが、すべての文を終わらせない
-語尾に「なんです」「だったんですね」など変化をつける
-「でも」「だから」「実は」などでつなぎ、会話っぽくする
-驚きや感情を少し混ぜて自然に話す


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

gScriptEvent_template = """
### Instruction:
あなたはプロの日本語YouTubeスクリプトライターです。

タスク：

テーマ「{theme}」について短編YouTubeスクリプトを日本語で作成してください。カリスマ的なYouTuberが話すような自然な口語で、面白く楽しく語ってください。
- テーマは必ず「事件・出来事」として扱うこと（戦争、災害、犯罪、歴史的事件など）
- 事件がどのように起こったのか、その背景や原因、なぜ起きたのか、社会や人々にどんな影響を及ぼしたのかを掘り下げて語ること。  

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
You are an AI assistant whose role is to generate **one Google search query** to find the most suitable images for quotes in a video.  

Input:  
- Video title (context): {title}  
- Quote to visualize: {quote}  

Instructions:  
- Create **only one search query**.  
- The query must focus on a **specific, concrete subject** such as a **person’s name, location, organization, event, or other clear noun** that makes sense in context.  
- Do **not** use vague or abstract terms like “influence”, “hidden network”, or “power”.  
- If both the title and quote provide multiple subjects, pick only **one subject** for the query (never combine them).  
  - Example: If the quote mentions a killer and drug use, search **either the killer’s name** or **drugs**, not both together.  
- If the quote is **niche, minor, or not important** in the broader context and has little correlation to the title, generate a query **only from the main subject or term in the title**.  
- Use **English**, unless the topic is specifically Japanese or Japanese results would be better.  

Output must be in strict JSON format only, using the following template:

```json
{{
  "query": "Enter the generated search query here"
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