"""MkDocs hook: set the page title for chapter prose pages so browser tabs
and OG cards show "第1章 Agent基础知识" instead of the nav label "正文".

The nav in mkdocs.yml nests each chapter as:
    - 第1章 Agent基础知识:
        - 正文: book/chapter1.md           ← nav label leaks into <title>
        - 配套实验: chapter1/README.md

Material uses the nav label as the page title when no frontmatter title
is set, so the browser tab says "正文 - AI Agents in Depth". We can't
edit the source markdown files (they're also consumed by the LaTeX PDF
build), so this hook sets the title in-memory at the on_page_context
stage, just before rendering. It only fires for chapter prose pages,
and respects any title already declared in frontmatter.
"""

# Map chapter number → title per language. Keep in sync with mkdocs.yml nav.
CHAPTER_TITLES = {
    "1": {
        "zh":   "第1章 Agent基础知识",
        "zhtw": "第 1 章 · Agent 基礎知識",
        "en":   "Chapter 1 · Agent Basics",
        "ta":   "அதி. 1 · AI ஏஜெண்ட் அடிப்படைகள்",
        "vi":   "Chương 1 · Nền tảng AI Agent",
        "ru":   "Глава 1 · Основы AI Agent",
    },
    "2": {
        "zh":   "第2章 上下文工程",
        "zhtw": "第 2 章 · 上下文工程",
        "en":   "Chapter 2 · Context Engineering",
        "ta":   "அதி. 2 · சூழல் பொறியியல்",
        "vi":   "Chương 2 · Kỹ thuật ngữ cảnh",
        "ru":   "Глава 2 · Контекстная инженерия",
    },
    "3": {
        "zh":   "第3章 用户记忆和知识库",
        "zhtw": "第 3 章 · 使用者記憶和知識庫",
        "en":   "Chapter 3 · User Memory & Knowledge Base",
        "ta":   "அதி. 3 · பயனர் நினைவகம் & அறிவுத்தளம்",
        "vi":   "Chương 3 · Bộ nhớ & Cơ sở kiến thức",
        "ru":   "Глава 3 · Память пользователя и база знаний",
    },
    "4": {
        "zh":   "第4章 工具",
        "zhtw": "第 4 章 · 工具",
        "en":   "Chapter 4 · Tools",
        "ta":   "அதி. 4 · கருவிகள்",
        "vi":   "Chương 4 · Công cụ",
        "ru":   "Глава 4 · Инструменты",
    },
    "5": {
        "zh":   "第5章 CodingAgent与代码生成",
        "zhtw": "第 5 章 · Coding Agent 與程式碼生成",
        "en":   "Chapter 5 · Coding Agent & Code Generation",
        "ta":   "அதி. 5 · குறியீட்டு ஏஜெண்ட் & குறியீடு உருவாக்கம்",
        "vi":   "Chương 5 · Coding Agent & Tạo mã",
        "ru":   "Глава 5 · Coding Agent и генерация кода",
    },
    "6": {
        "zh":   "第6章 Agent的评估",
        "zhtw": "第 6 章 · Agent 的評估",
        "en":   "Chapter 6 · Evaluating Agents",
        "ta":   "அதி. 6 · ஏஜெண்ட் மதிப்பீடு",
        "vi":   "Chương 6 · Đánh giá Agent",
        "ru":   "Глава 6 · Оценка агентов",
    },
    "7": {
        "zh":   "第7章 模型后训练",
        "zhtw": "第 7 章 · 模型後訓練",
        "en":   "Chapter 7 · Model Post-Training",
        "ta":   "அதி. 7 · மாதிரி பிந்தைய பயிற்சி",
        "vi":   "Chương 7 · Post-training mô hình",
        "ru":   "Глава 7 · Посттренировка моделей",
    },
    "8": {
        "zh":   "第8章 Agent的自我进化",
        "zhtw": "第 8 章 · Agent 的自我進化",
        "en":   "Chapter 8 · Agent Self-Evolution",
        "ta":   "அதி. 8 · ஏஜெண்ட் சுய-பரிணாமம்",
        "vi":   "Chương 8 · Tự tiến hóa của Agent",
        "ru":   "Глава 8 · Самоэволюция агентов",
    },
    "9": {
        "zh":   "第9章 多模态与实时交互",
        "zhtw": "第 9 章 · 多模態與即時互動",
        "en":   "Chapter 9 · Multimodal & Real-Time",
        "ta":   "அதி. 9 · பல்முக & நிகழ்நேரம்",
        "vi":   "Chương 9 · Đa phương thức & Thời gian thực",
        "ru":   "Глава 9 · Мультимодальность и реальное время",
    },
    "10": {
        "zh":   "第10章 多Agent协作",
        "zhtw": "第 10 章 · 多 Agent 協作",
        "en":   "Chapter 10 · Multi-Agent Collaboration",
        "ta":   "அதி. 10 · பல-ஏஜெண்ட் ஒத்துழைப்பு",
        "vi":   "Chương 10 · Đa Agent cộng tác",
        "ru":   "Глава 10 · Сотрудничество мультиагентов",
    },
}


def _detect_lang_and_chapter(src_path):
    """Return (lang_code, chapter_num) for a chapter prose path, or None."""
    import re
    m = re.search(r"book(?:-([a-zA-Z-]+))?/chapter(\d+)", src_path)
    if not m:
        return None
    lang_raw, num = m.group(1), m.group(2)
    if lang_raw is None:
        lang = "zh"
    elif lang_raw.lower() in ("zhtw", "zh-tw", "zh_tw"):
        lang = "zhtw"
    else:
        lang = lang_raw.lower()
    return (lang, num)


def on_page_context(context, page, config, nav, **kwargs):
    # Only touch chapter prose pages.
    detected = _detect_lang_and_chapter(page.file.src_path)
    if not detected:
        return context
    lang, num = detected
    if num not in CHAPTER_TITLES:
        return context
    title = CHAPTER_TITLES[num].get(lang)
    if not title:
        return context
    # Respect explicit frontmatter title.
    if page.meta and page.meta.get("title"):
        return context
    # Material's <title> and og:title both come from page.title. Override
    # in-memory; the source markdown is untouched.
    page.title = title
    context["title"] = title
    return context
