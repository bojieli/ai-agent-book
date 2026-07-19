# 实验 5-5：论文讲解视频的自动生成 ★★

在“论文 → PPT”的基础上，Agent 为每一页幻灯片生成**口语化讲解词**（引导性叙述，
而非逐条复述要点），调用 **TTS** 合成语音，再用 **ffmpeg** 把 PPT 截图与音频
**逐页同步合成**为一段带旁白的讲解视频。

## 流程

```
论文要点(内置示例)
   │  PIL 渲染
   ▼
每页 PNG 幻灯片 ──► gpt-5.6-luna 生成口语化讲解词 ──► OpenAI tts-1 合成 mp3
   │                                                        │
   └──────────────── ffmpeg：每页 PNG + 该页音频 ───────────┘
                              │  (每页时长 = 该页音频时长)
                              ▼
                     ffmpeg concat 拼接
                              ▼
                     output/lecture.mp4
```

- 本项目**自包含**，不依赖实验 5-4：内置一份《Attention Is All You Need》的论文要点，
  用 PIL 直接渲染出 5 页幻灯片 PNG（也可替换为 5-4 的 Slidev 截图）。
- 讲解词由 `gpt-5.6-luna` 生成；语音由 OpenAI `tts-1`（`voice=alloy`）合成。
- 视频由 `ffmpeg` 合成：每页做一段 mp4，段时长等于该页音频时长，最后 concat 拼接，
  因此**每页展示时间与语音时长精确匹配**。

## 运行命令

```bash
pip install -r requirements.txt      # 安装 Python 依赖
cp env.example .env                  # 填入 OPENAI_API_KEY（未配置时设 OPENROUTER_API_KEY 兜底讲解词，TTS 降级为离线占位）
python demo.py                       # 生成全部 5 页的完整讲解视频
```

常用参数（`python demo.py --help` 查看全部）：

```bash
python demo.py --check     # 环境自检：检查 ffmpeg/ffprobe/字体/配置，不调用任何 API
python demo.py --quick     # 快速冒烟：只跑第 1 页（等价 --limit 1），省时省钱
python demo.py --limit 2   # 只处理前 2 页
python demo.py --offline   # 无需 API：占位静音音轨，验证整条 ffmpeg 合成流水线
```

完整参数：

| 参数 | 说明 |
| --- | --- |
| `--slides FILE` | 幻灯片内容 JSON（`[{title, subtitle, bullets}, ...]`），替换内置示例 |
| `--script FILE` | 现成讲解词 JSON（字符串列表，每页一段），提供后**跳过 LLM 生成** |
| `-o, --output FILE` | 最终视频输出路径（默认 `output/lecture.mp4`） |
| `--tts-provider {openai,offline}` | TTS 供应商；`offline` 用 ffmpeg 生成占位静音音轨（无需 API） |
| `--offline` | 完全离线：等价 `--tts-provider offline`，并用要点占位讲解词（零 API 调用） |
| `--text-model / --tts-model / --tts-voice` | 覆盖模型/音色（默认取同名环境变量） |
| `--limit N / --quick / --check` | 只跑前 N 页 / 只跑第 1 页 / 仅自检 |

> **离线验证**：`--offline` 不需要任何 API Key 或网络，用 `ffmpeg anullsrc` 按讲解词字数
> 估算时长合成静音占位音轨，跑通「渲染 → 估时 → 逐页合成 → concat 拼接」全链路，
> 专门用于验证 ffmpeg 的**逐页时长对齐**是否正确（音轨为静音占位，非真实配音）。

产物：
- `output/slides/slide_*.png`   每页幻灯片
- `output/audio/audio_*.mp3`    每页讲解音频
- `output/segments/seg_*.mp4`   每页分段视频
- `output/narration.json`       每页讲解词与音频时长清单
- `output/lecture.mp4`          最终讲解视频

查看视频元信息：

```bash
ffprobe -v error -show_format -show_streams output/lecture.mp4
```

## 预期输出示例

以内置的 5 页《Attention Is All You Need》为例，一次完整运行的真实产物：

- `output/lecture.mp4`：约 **2.8 MB**，时长 **166.97s**（≈2 分 47 秒），
  分辨率 **1280×720**，视频 **H.264** + 音频 **AAC**。
- `output/audio/audio_01.mp3 … audio_05.mp3`：每页一段旁白，
  单页时长约 **28.6s / 33.3s / 37.2s / 37.9s / 29.9s**（总计 ≈166.9s，与视频时长一致）。
- `output/narration.json`：每页的口语化讲解词与音频时长清单，例如第 1 页：

  > 今天，我们将一起探讨一个改变了自然语言处理领域的重要研究——"Attention Is All You Need"……
  > 它完全依赖于注意力机制，摒弃了传统的循环和卷积结构。

运行日志会逐页打印「幻灯片 → 讲解词 → 音频时长」，末尾汇总各页音频总时长与最终视频时长
（二者应基本一致，说明每页展示时间与语音精确对齐）。

## 依赖

- **ffmpeg / ffprobe**：命令行工具（本项目用 8.x 验证）。macOS 可 `brew install ffmpeg`。
- **Python 包**：`openai`、`Pillow`、`python-dotenv`（见 `requirements.txt`）。
- **中文字体**：渲染幻灯片需系统中文字体，脚本已按 macOS 常见字体
  （PingFang / STHeiti / Hiragino / Arial Unicode）自动回退。
- **环境变量**：需 `OPENAI_API_KEY`（走官方 OpenAI）；未配置时可用 `OPENROUTER_API_KEY` 兜底讲解词生成（此时 TTS 因不在 OpenRouter 上而降级为离线静音占位）。可选项见 `env.example`。

## 如何适配 / 扩展

- **换模型 / 换供应商**：环境变量或命令行均可，无需改代码：
  - `TEXT_MODEL` / `--text-model`：讲解词生成模型（默认 `gpt-5.6-luna`，可换其它）。
  - `TTS_MODEL` / `TTS_VOICE`（或 `--tts-model` / `--tts-voice`）：语音模型与音色
    （默认 `tts-1` / `alloy`，音色可选 `nova` / `shimmer` / `echo` 等）。
  - `--tts-provider offline`：切到离线占位音轨（不产生任何 API 调用），用于本地验证。
  - `OPENAI_BASE_URL`：指向任何**兼容 OpenAI 协议**的自定义端点（自建网关、代理或
    第三方供应商）；配合对应的 `OPENAI_API_KEY` 即可切换后端。
- **换输入（换论文 / PDF）**：用 `--slides my.json` 传入外部幻灯片内容，或直接编辑
  `demo.py` 中的 `SLIDES` 列表（标题 / 副标题 / 要点）；若已有真实 PDF，可先用 5-4 的
  「论文 → PPT」流程产出要点或 Slidev 截图，再喂给本脚本，其余流程不变。
- **自带讲解词**：用 `--script narr.json`（每页一段的字符串列表）跳过 LLM 生成，
  直接进入「TTS → 合成」，便于人工润色脚本后重跑。
- **更长视频**：增加 `SLIDES` 页数或加长每页讲解词即可（单次 5~15 分钟）。
- **快速调参**：先用 `--quick` / `--limit N` 只渲染少量页，确认音色/风格满意后再跑全量。

## 局限

- 讲解词与 TTS 都会产生真实的 OpenAI API 调用（`TEXT_MODEL` 与 `TTS_MODEL`），会**计费**；
  全量 5 页约生成 2~3 分钟视频。建议先 `--check` 自检、再 `--quick` 冒烟。
- 幻灯片为 PIL 纯静态渲染（无动画/转场），中文字体依赖系统字体，非 macOS 需自行调整
  `FONT_CANDIDATES`。
- 每页时长严格等于该页音频时长，不做静音停顿或背景音乐；如需更精细的排版与转场，
  建议改用 5-4 的 Slidev 截图作为输入。
