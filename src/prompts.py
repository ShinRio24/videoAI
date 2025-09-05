
genTitle = """
あなたは、数々のショート動画を100万回再生させてきた、プロの日本語YouTubeプロデューサーです。

### タスク
以下のトピックを基に、視聴者の知的好奇心を強烈に刺激し、思わずクリックしてしまうような**日本語タイトルを1つだけ**考案してください。

### 最高のタイトルを作るための原則

1.  **好奇心を最大化せよ:** 「〇〇の真実」「〇〇に隠された秘密」のように、視聴者が「答えを知りたい！」と思うような、謎や秘密をほのめかすこと。事実を説明するのではなく、好奇心を煽ること。
2. 物語のトーンに合う「パワーワード」を選ぶ (Choose a "Power Word" that Fits the Story's Tone)

タイトルに読者の感情を揺さぶるような強力な単語（パワーワード）を使い、一瞬で興味を引くことが重要です。物語が持つ雰囲気（ポジティブ、ネガティブ、ミステリアスなど）に合わせて、最適な言葉を選びましょう。

* **感動・希望を与える物語 (For inspiring or hopeful stories):**
    * **例:** `伝説 (Legend), 奇跡 (Miracle), 天才 (Genius), 覚醒 (Awakening), 栄光 (Glory), 希望 (Hope), 革命 (Revolution)`

* **衝撃・悲劇性を強調する物語 (For shocking or tragic stories):**
    * **例:** `悲劇 (Tragedy), 衝撃 (Shock), 禁断 (Forbidden), 闇 (Darkness), 崩壊 (Collapse), 絶望 (Despair), 孤独 (Loneliness)`

* **謎・真実を追求する物語 (For mysterious or truth-seeking stories):**
    * **例:** `真実 (Truth), 謎 (Mystery), 秘密 (Secret), 裏側 (The Other Side), 運命 (Destiny), 正体 (True Identity)`
3.  **簡潔に、しかし強力に:** タイトルは**20文字以内**を目安に、不要な言葉を削ぎ落とし、最もインパクトのある部分だけを残すこと。

### 実績のあるタイトルパターン（これらを創造的に組み合わせよ）

* **秘密・暴露型 (The Secret/Revelation):** 最も強力なパターン。視聴者が知らないであろう情報を示唆する。
    * *例:* `【名前】に隠された禁断の真実`
    * *例:* `メディアが報じない【名前】の裏側`

* **言い切り型 (The Bold Declaration):** 対象を大胆な言葉で定義し、強い印象を与える。
    * *例:* `世界を騙した天才詐欺師【名前】`
    * *例:* `歴史を塗り替えた男【名前】`

* **問いかけ型 (The Question):** 視聴者に直接質問を投げかけ、考えさせることでエンゲージメントを高める。
    * *例:* `なぜ【名前】は〇〇したのか？`

### ⚠️絶対的なルール⚠️
-   完成したタイトルのみを出力し、他のテキストは一切含めないこと。
-   必ずトピックの固有名詞（名前）をタイトルに含めること。
-   絵文字、句読点（、。）、記号（「」？！）は一切使用しない。

### 悪い例 vs 良い例
-   **トピック:** Donald Trump
-   **悪いタイトル:** `物議を醸した大統領トランプ` (事実を述べているだけで、好奇心を刺激しない)
-   **良いタイトル:** `トランプ 封印された過去` (「封印された過去」とは何か？と好奇心を煽る)


### Input
トピック: {theme}

### Output Format:
必ず次のフォーマットに従ってください。他のテキストは絶対に出力しないでください。

```json
{{
  "title": "Your generated title here"
}}```
"""

queryPrompt_template = """
You are an expert AI assistant specializing in visual storytelling. Your task is to analyze a video's title and a relevant quote to generate the **most visually effective Google Image search query**. This query should center on the core subject but can be made more specific if the context points to a highly famous, visually documented event associated with that subject.

---
## Critical Rules

1.  **The Specificity Principle (Most Important Rule)**: Your primary goal is to identify the core subject's full, canonical name.
    * **Default Behavior**: In most cases, the query will be **only** the subject's full name (e.g., a person, organization, or base event).
    * **Exception for Famous Events**: If the title or quote *explicitly* references a **highly famous and visually distinct event, trial, scandal, or performance** uniquely associated with the subject, you should append that event to the name. This is only for events that have a rich, well-known visual record of their own (e.g., "O.J. Simpson trial," "Michael Jackson moonwalk").
    * **What to Avoid**: **Never** add generic, descriptive words like "photo," "case," "incident," "childhood," or "perpetrator." The added context must be a proper noun or a widely recognized named event.

2.  **Use the Subject's Native Language**: The language of the query must match the origin of the subject to find the most authentic and numerous images.
    * If the subject is **Chinese**, the query must be in **Chinese characters**.
    * If the subject is **American**, the query must be in **English**.
    * If the subject is **Japanese**, the query must be in **Japanese**.

3.  **Use Full, Canonical Names**: Always expand partial or incomplete names to their most recognizable, official form. For Western names, this includes first and last names.

---
## Step-by-Step Guide

1.  **Identify the Core Subject**: Read the title and quote to determine the central person, event, or location being discussed.
2.  **Analyze the Context**: Determine if the title or quote refers to a *specific, famous, and visually-rich event* directly associated with the core subject.
3.  **Determine the Subject's Origin**: Based on the name and context, identify the subject's nationality or primary language.
4.  **Construct the Query**:
    * First, find the subject's full, canonical name in its native language (e.g., `周克华`, `Bernie Madoff`).
    * If a famous associated event was identified in Step 2, append its common name to the query (e.g., `O.J. Simpson trial`).
    * Otherwise, use only the subject's canonical name.
5.  **Generate the Final Query**: The final query is the result from the previous step.

---
## Examples

**Example 1: Default Behavior (Chinese Subject)**
* **Title**: `チョウクホア最凶の強盗犯` (The Most Vicious Robber, Zhou Kehua)
* **Quote**: `あなたは知っていますか。闇に生き、凶行を重ねた男を。` (Do you know the man who lived in darkness and committed heinous acts?)
* **Correct Query**: `"周克华"`
* **Reasoning**: The subject, Zhou Kehua, is Chinese. While he committed crimes, there isn't one single, named event famous enough to append. The most effective query is his canonical name in Chinese.

**Example 2: Exception - Famous Trial (American Subject)**
* **Title**: `The Trial of the Century: O.J.`
* **Quote**: `The infamous Bronco chase and the glove that didn't fit.`
* **Correct Query**: `"O.J. Simpson trial"`
* **Reasoning**: The subject is O.J. Simpson, but the title and quote are not about his general life; they are specifically about his murder trial, an event with its own massive and distinct visual record. "O.J. Simpson" alone would be too broad.

**Example 3: Exception - Famous Performance (American Subject)**
* **Title**: `キング・オブ・ポップの伝説のムーンウォーク` (The King of Pop's Legendary Moonwalk)
* **Quote**: `The moment he first performed the iconic dance during 'Billie Jean' at Motown 25.`
* **Correct Query**: `"Michael Jackson moonwalk"`
* **Reasoning**: The context is not just Michael Jackson, but his single most iconic performance. Searching for "Michael Jackson moonwalk" will yield far more relevant images for this specific story than just his name.

**Example 4: Default Behavior (Japanese Event)**
* **Title**: `地下鉄サリン事件の恐怖` (Terror of the Subway Sarin Incident)
* **Quote**: `The attack on the Tokyo subway system.`
* **Correct Query**: `"地下鉄サリン事件"`
* **Reasoning**: The subject is the event itself. It's already a specific, proper noun. No further context is needed.

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

genTopics_template ="""You are a professional scriptwriter and researcher for a popular Japanese YouTube channel that creates educational and entertaining content.

Your task is to generate a list of 10 influential figures suitable for a series of YouTube Shorts.
The theme is: {idea}

The primary audience is Japanese, so the list should include a mix of figures who are:
a) Significant in Japanese history and culture.
b) Globally influential figures who are also widely recognized and respected in Japan.

CRITICAL GUIDELINES FOR SELECTION:

Visual Availability: Prioritize figures for whom there is a rich public domain or easily accessible visual record (photographs, famous paintings, statues, etc.). This is crucial for creating visually engaging short videos.

Clear Narrative: Select figures with well-documented and clear life stories. Their key achievements and impact should be easily explainable in a concise, 60-second format. Avoid figures whose histories are overly complex, obscure, or primarily based on disputed legends.

Catchy Framing: The topics should be framed as catchy, short YouTube titles (ideally around 15 characters). Provide context. For example, instead of just 「織田信長」, a better topic would be 「天下統一を目指した男、織田信長」(Oda Nobunaga: The Man Who Aimed to Unify Japan).

The output MUST be a raw JSON file in the following format. Do not include any text, explanations, or markdown formatting before or after the JSON block.

EXAMPLE OUTPUT:
{{
  "Topics": [
    "天下統一を目指した男、織田信長",
    "幕末の風雲児、坂本龍馬",
    "世界を変えた発明王、エジソン",
    "非暴力で世界を導いた、ガンジー",
    "近代看護の母、ナイチンゲール",
    "Appleの伝説、スティーブ・ジョブズ",
    "奇跡の作曲家、ベートーヴェン",
    "人種の壁を壊した王、キング牧師",
    "近代日本の父、福沢諭吉",
    "無償の愛の聖女、マザー・テレサ"
  ]
}}
    """

__all__ = [k for k in globals().keys() if not k.startswith('_')]