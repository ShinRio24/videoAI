__all__ = ["gScriptGeneral_template",
           "gScriptCharacter_template",
           "gScriptOrganization_template",
           "gScriptEvent_template",
           "queryPrompt_template",
           "correctIMG_template",
           "imageDescription_template",
           "genTitle"]


genTitle = """
あなたは、数々のショート動画をバズらせてきたプロの日本語YouTubeタイトルクリエイターです。

### タスク
以下のトピックを基に、視聴者が思わずクリックしてしまうような、**非常に短くインパクトのある**日本語タイトルを1つだけ考案してください。

### ⚠️最重要ルール⚠️
- **【名前 + 肩書】の形を基本とする。** トピックを最も象徴する、短く強力な肩書や説明を名前に加えること。
- **必ずトピックの固有名詞をタイトルに含めること。**
- 完成したタイトルのみを出力し、他のテキストは一切含めないこと。
- **15文字前後(最大15文字)**にすること。
- 絵文字、句読点（、。）、記号（「」？！）は一切使用しない。
- 必ず日本語のみを使用し、英語は禁止する。

### タイトルの型（パターン）
以下の「言い切り型」を最優先で使ってください。
- **【言い切り型】:**
  - 「史上最も〇〇な男」「〇〇を変えた天才」のように、大胆に言い切ることで強い印象を与える。
  - *例: 「Donald Trump, the most controversial president」 → 「物議を醸した大統領トランプ」*

###
トピック: {theme}
"""

gScriptGeneral_template = """
### Instruction:
あなたはプロの日本語YouTubeスクリプトライターです。複雑なテーマを、まるで一つの映画のように語るストーリーテリングの達人です。

### Core Principle: The Story Comes First
あなたの最優先事項は、与えられたテーマを**起承転結（きしょうてんけつ）**の構成に沿った、引き込まれる物語に変換することです。単に事実を並べるのではなく、視聴者が自然に話の流れを追えるように、各フレーズが次へと繋がる滑らかな物語を構築してください。

### Task Breakdown:
**1. Classify the Theme:**
まず、テーマ「{theme}」が「人物」「組織」「事件・出来事」のどれに該当するかを判断してください。この分類に基づき、以下の物語構成に従います。

**2. Build the Narrative using 起承転結:**

---
#### **If the theme is a "Person" or "Organization":**
-   **起 (Introduction):** まずキャッチーな質問で視聴者を惹きつけます。その人物や組織が最も輝いていた、あるいは最も知られている姿を提示して、「なぜこうなったのか？」という疑問を投げかけます。
-   **承 (Development):** 物語を遡り、その起源を描きます。無名だった頃の意外な生い立ちや、設立当初の苦労など、現在の姿からは想像もつかない過去を語ってください。
-   **転 (Twist/Turning Point):** 物語の核心です。成功を決定づけた「最大の転機」や、その裏に隠された衝撃的な「秘密」や「裏話」を明かします。ここが一番の盛り上がりです。
-   **結 (Conclusion):** そして現在。その成功や失敗が、今の社会や私たちにどのような「影響」を与え続けているのかを語り、物語を締めくくります。

#### **If the theme is an "Event" or "Incident":**
-   **起 (Introduction):** キャッチーな質問から始め、事件が起きた「その瞬間」の衝撃的な光景や結果をまず提示します。「一体、なぜこんなことが？」と視聴者の興味を引きます。
-   **承 (Development):** 時間を巻き戻し、事件が起きる前の「背景」や「原因」を掘り下げます。平和だった日常や、水面下で進んでいた問題など、事件の火種を丁寧に描写します。
-   **転 (Twist/Trigger):** 物語が動く瞬間です。事件発生の直接的な「引き金」となった出来事や、誰も予想しなかった意外な展開を語り、緊張感を高めます。
-   **結 (Conclusion):** 事件のその後。社会に与えた深刻な「影響」や、残された教訓、そして今も続くその物語について触れ、視聴者に深い余韻を残します。
---

### Technical & Style Requirements:
-   **Length & Structure:** スクリプト全体は約300文字（±5%以内）。おおよそ10〜14個のフレーズに分割してください。
-   **JSON Output:** 各フレーズ（20〜40文字）をJSONリストの要素として出力してください。
-   **Conversational Tone:**
    -   です・ます調を基本としつつ、「なんです」「だったんですね」といった多様な語尾で会話のリズムを作る。
    -   読点（、）を効果的に多めに使い、テンポの良い語り口を演出する。
    -   「でも」「だから」「実は」「そして」といった接続詞で、フレーズ間を滑らかにつなぐ。
    -   ドキュメンタリー風の信頼性と、エンタメとしての楽しさを両立させる。
-   **Prohibitions:** 引用符（「」『』""）、（笑）や特殊記号は一切使用しないこと。

### Output Format:
必ず次のフォーマットに従ってください。他のテキストは絶対に出力しないでください。

```json
{{
  "Script": [
    "ここに「起」のパートが入ります。",
    "次に「承」のパートが続きます。",
    "そして物語の転換点である「転」。",
    "最後に「結」で締めくくります。"
  ]
}}
"""


gScriptGeneral_templateold  = """
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
- スクリプト全体は必ず約300文字（±5%以内）
- 各フレーズは平均30文字前後。ただし20〜40文字の揺らぎをつけること
- 出力するフレーズは おおよそ12個前後（10〜14個の範囲）
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
-読点（、）を多めに使い、会話のようなテンポの良い文章にすること



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
あなたはプロの日本語YouTubeスクリプトライターです。特に、歴史上の人物や事件の裏側に迫る、ダークで知的なドキュメンタリーコンテンツを得意としています。

タスク：
テーマ「{theme}」について、短編YouTubeドキュメンタリーのスクリプトを作成してください。
カリスマ的なYouTuberが語るような、引き込まれる自然な口語体で、エンタメ性と重厚感を両立させてください。

### スタイル・構成
1.  **フック**
    -   「あなたは知っていますか」「想像してみてください」などで視聴者の心を掴む。
    -   テーマの核心に触れる、衝撃的で好奇心を煽る問いを投げかける。
    -   フックから人物の生い立ちへ、物語が始まる期待感を高めながら繋げる。

2.  **生い立ち・転機**
    -   幼少期や青年期の「具体的な転機」や、その後の運命を決定づけた象徴的な出来事を簡潔に描写する。

3.  **力の掌握**
    -   組織名、収益、人数などの具体的な「数字」を事実に基づき使用し、その規模と影響力をリアルに伝える。

4.  **光と闇の二面性**
    -   善行や人間的な一面と、残虐非道な行為を対比させて人物の多面性を描く。
    -   被害者数や象徴的な事件を盛り込み、視聴者に強烈な印象を残す。

5.  **結末と伝説**
    -   逮捕、死、あるいは現在の活動など、その後の運命を語る。
    -   最後のフレーズは必ず「こうして、その名は伝説として今も語り継がれている。」で締めくくる。
    -   章の切り替えには「しかし」「その一方で」「驚くべきことに」といった効果的な接続詞を使用する。

### 技術要件
-   **文字数**: 全体で約350文字（±10%以内）。
-   **フォーマット**: 各フレーズを20〜45文字で区切り、JSONのリスト形式で出力。各フレーズが画像やテロップの切替ポイントとなる。
-   **表現**: 語尾や言い回しにバリエーションを持たせ、単調にならないように。
-   **必須ワード**: 「秘密」「力」「影響力」「闇」「伝説」の5つを、テーマの核心に絡めて自然に組み込むこと。
-   **固有名詞の表記**:
    -   **日本人名**: 原則として漢字で表記する。（例：加藤智大）
    -   **海外の人物・地名**: カタカナで表記する。（例：パブロ・エスコバル）
-   **句読点**: 「。」を基本とし、「、」はリズムを整えるために最小限使用する。

### 禁止事項
-   引用符（「」『』や""）の使用。
-   英語、特殊記号、箇条書きの使用。

### 出力形式：
必ず次のフォーマットに従ってください。他のテキストや説明は絶対に出力しないでください。

```json
{{
  "Script": [
    "ここに1つ目のフレーズが入ります。",
    "次に2つ目のフレーズが続きます。",
    "このようにリスト形式で出力します。"
  ]
}}```
"""

gScriptOrganization_template = """
"""

gScriptEvent_template = """
"""



queryPrompt_template = """Here is the complete prompt in a copy-paste friendly format.

You are an expert AI assistant specializing in visual storytelling. Your task is to analyze a video's title and a relevant quote to extract the **single, core proper noun** that will serve as a highly effective Google Image search query.

---
## Critical Rules

1.  **Proper Noun Only (Most Important Rule)**: Your output **must** be the subject's full, canonical name (e.g., a person, event, or organization). **Do not** add any extra descriptive words like "photo," "case," "incident," "childhood," or "perpetrator." The query is the name and nothing more.

2.  **Use the Subject's Native Language**: The language of the query must match the origin of the subject to find the most authentic and numerous images.
    * If the subject is **Chinese**, the query must be in **Chinese characters**.
    * If the subject is **American**, the query must be in **English**.
    * If the subject is **Japanese**, the query must be in **Japanese**.

3.  **Use Full, Canonical Names**: Always expand partial or incomplete names to their most recognizable, official form. For Western names, this includes first and last names.

---
## Step-by-Step Guide

1.  **Identify the Core Subject**: Read the title and quote to determine the central person, event, or location being discussed.
2.  **Determine the Subject's Origin**: Based on the name and context, identify the subject's nationality or primary language.
3.  **Find the Canonical Name**: Determine the subject's full, official name in its native language. For example, the Japanese title `チョウクホア` is a phonetic spelling of the Chinese name `周克华` (Zhou Kehua). The correct query is the original Chinese name.
4.  **Generate the Query**: The final query is only the name you identified in the previous step.

---
## Examples

**Example 1: Chinese Subject**
* **Title**: `チョウクホア最凶の強盗犯` (The Most Vicious Robber, Zhou Kehua)
* **Quote**: `あなたは知っていますか。闇に生き、凶行を重ねた男を。` (Do you know the man who lived in darkness and committed heinous acts?)
* **Correct Query**: `"周克华"`
* **Reasoning**: The subject, Zhou Kehua, is Chinese. The query must be his name in Chinese characters for the best results. The query contains *only* the name.

**Example 2: American Subject**
* **Title**: `Madoff詐欺の闇` (The Darkness of the Madoff Scam)
* **Quote**: `The biggest Ponzi scheme in history.`
* **Correct Query**: `"Bernie Madoff"`
* **Reasoning**: The subject is American. The partial name "Madoff" is expanded to his full, canonical name in English.

**Example 3: Japanese Event**
* **Title**: `地下鉄サリン事件の恐怖` (Terror of the Subway Sarin Incident)
* **Quote**: `The attack on the Tokyo subway system.`
* **Correct Query**: `"地下鉄サリン事件"`
* **Reasoning**: The subject is a specific event that occurred in Japan. The query is the event's official name in Japanese.

---
Input 
**Video Title**: {title}
**Quote to Visualize**: {quote}

---
## Output Format

Your output must be in **strict JSON format only**, with no other text or explanations.

```json
{{
  "query": "Your generated search query here"
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