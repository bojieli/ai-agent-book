# 实验 9-5：控制标记驱动的可控 TTS

《深入理解 AI Agent》实验 9-5 的可运行配套项目。

核心思路：让主 LLM 的输出不只是文本，还带上**控制标记**（情感 / 语速 / 风格 /
停顿 / 笑声等）；执行层解析这些标记，映射到一个**参考语音库**里对应的音色/风格档案，
再合成语音。这样「在哪里该停顿、该用什么语气」的决策交给了 LLM，同一段文本在不同
控制标记下能合成出不同风格、情感、节奏的语音。

## Provider 适配（重要）

书中实验 9-5 使用 **Fish Audio S1** 的声音克隆：用 3-10 秒参考语音零样本克隆同一
音色，构建覆盖情绪 × 语速 × 风格的参考语音库，靠控制标记选择参考语音，Fish Audio
保证不同参考语音之间**音色一致**、只有韵律和情感变化。

本环境无 Fish Audio 可用 key，因此改用 **OpenAI TTS** 演示**完全相同的思路**：

| 书中（Fish Audio） | 本项目（OpenAI TTS） |
| --- | --- |
| 声音克隆保证音色一致 | 全库固定同一个 `voice`（alloy），音色不变 |
| 每条参考语音的韵律/情感 | 每个档案对应一段 `instructions` 风格提示词 |
| 控制标记选参考语音 | 控制标记解析后 -> 选 `(情绪,语速,风格)` 档案 |

- 首选模型 **`gpt-4o-mini-tts`**：支持 `instructions` 参数，可用一段中文提示词精确
  控制情感/语速/口吻，最贴近「控制标记 → 风格化语音」的语义。
- 若首选模型不可用，代码**自动兜底到 `tts-1`**：不支持 instructions，改用多 voice +
  `speed` 参数 + 文本级停顿近似。

**必须用 OpenAI 直连 Key**：本实验只用 TTS 语音合成端点（`gpt-4o-mini-tts` / `tts-1`），
这类音频端点只有 OpenAI 直连才有——OpenRouter 只做聊天补全、无音频合成端点，故无法回退到
`OPENROUTER_API_KEY`。离线查看语音库/标记映射（`--list-voices` / `--dump-mapping`）则无需任何 Key。

> 局限：OpenAI TTS 无法像 Fish Audio 那样**原生生成**笑声/叹气等非语言音。本项目对
> `<laugh>` / `[SIGH]` 用「匹配情绪的拟声词」（如“哈哈，”“唉——”）近似，`[PAUSE]`/
> `[THINKING]` 等停顿则用 ffmpeg 生成**真实静音**插入，可被 ffprobe 验证时长。

## 控制标记 → TTS 参数 映射

### 状态标记（持续生效，直到被同类标记改变）

| 标记 | 中文写法 | 作用 |
| --- | --- | --- |
| `[EMO:neutral\|happy\|frustrated\|thinking]` | `[情感=中性\|高兴\|沮丧\|思考]` | 切换情绪 |
| `[SPEED:normal\|fast\|slow]` / `[SPEED:0.8x]` | `[语速=正常\|快\|慢]` | 切换语速 |
| `[STYLE:formal\|casual]` | `[风格=正式\|轻松]` | 切换口吻 |

三个维度组合成参考语音库的一个档案（如 `happy_fast_formal`），
再拼成一段 `instructions` 提示词交给 `gpt-4o-mini-tts`。

### 内联标记（一次性事件）

| 标记 | 作用 |
| --- | --- |
| `[THINKING]` | 切到「思考/慢速/正式」参考语音 + 插入 0.5s 停顿 |
| `[SEARCHING]` | 同上，停顿 0.4s（搜索性犹豫） |
| `[PAUSE]` / `<pause>` / `[停顿]` | 插入 0.5s 静音 |
| `[BREATH]` / `<breath>` | 插入 0.4s 换气停顿 |
| `[SIGH]` / `<sigh>` | 叹气拟声词「唉——」+ 0.3s 停顿 |
| `[LAUGH:small]` / `<laugh>` | 轻笑拟声词「哈哈，」（欢快音色） |
| `<emphasis>…</emphasis>` / `[强调]…[/强调]` | 对包裹文本追加「加重强调」提示词 |

### 参考语音库

`voice_library.py` 由 情绪(4) × 语速(3) × 风格(2) 笛卡尔积生成 **24 条**档案，全部固定
`voice=alloy`（音色一致），仅 `instructions` 不同。可单独运行查看：

```bash
python voice_library.py
```

## 安装与运行

```bash
pip install -r requirements.txt          # 需系统已装 ffmpeg/ffprobe
cp env.example .env                       # 填入有效的 OPENAI_API_KEY
python demo.py                            # 生成 output/*.mp3
```

`demo.py` 做两件事：

1. **三种配置对比**（书中要求），同一段带标记文本：
   - `A_no_markers.mp3` 无控制标记（流畅但机械）
   - `B_single_voice.mp3` 单一参考语音（自然但情感单调）
   - `C_voice_library.mp3` 多参考语音库（按标记切换情感/语速/停顿）
2. **同文本 / 不同控制标记** → 多个不同风格音频：`variant_*.mp3`。

运行时会打印每个音频的「控制标记 → 参数」解析过程，以及 ffprobe 时长信息。

常用参数（`python demo.py --help`）：

| 参数 | 作用 |
| --- | --- |
| `--quick` | 只跑三种配置对比（A/B/C），跳过 5 个风格变体，减少 TTS 调用与耗时 |
| `--text 文本` | 只合成这一段自定义文本（可内嵌控制标记，如 `[情感=高兴][THINKING]…`） |
| `--emotion / --speed / --style` | 为 `--text` 指定情绪/语速/口吻（等价于在文本前加对应状态标记） |
| `-o / --output 路径` | `--text` 模式的输出 mp3 路径（默认 `output/custom.mp3`） |
| `--list-voices` | **离线**（无需 API key）：打印完整参考语音库（24 条档案及其 instructions） |
| `--dump-mapping` | **离线**（无需 API key）：打印控制标记 → 动作映射表，并演示对示例文本的解析过程 |

## 预期输出示例（真实节选）

```
首选模型: gpt-4o-mini-tts（不可用时自动兜底 tts-1）

对比实验：同一段带控制标记的文本，三种配置
原始文本: [EMO:happy][SPEED:fast]太好了！您的订单已确认。[THINKING]嗯，让我查一下发货时间...[EMO:neutral][SPEED:normal]预计明天下午送达。

[C] 多参考语音库（解析控制标记 -> 逐段切换参考语音 + 停顿）
    -- 控制标记解析过程 --
  [EMO:happy]            -> 情绪 = happy
  [SPEED:fast]           -> 语速 = fast
  [THINKING]             -> 切换到 思考/慢速/正式 参考语音
  [THINKING] 停顿          -> 插入静音 500ms
    -- 合成片段 --
    · [happy_fast_formal         ] gpt-4o-mini-tts  voice=alloy text='太好了！您的订单已确认。'
    · [静音 500ms]
    · [thinking_slow_formal      ] gpt-4o-mini-tts  voice=alloy text='嗯，让我查一下发货时间...'
    · [neutral_normal_formal     ] gpt-4o-mini-tts  voice=alloy text='预计明天下午送达。'
  => output/C_voice_library.mp3  |  format_name=mp3  duration=11.324000  ...
```

对照三种配置的 ffprobe 时长即可看出差异：C（多参考语音库）因插入真实静音停顿，
比 A/B（8.5s 左右）更长（约 11.3s），且各片段用了不同的 `(情绪,语速,风格)` 档案。
（每次运行会真实调用 OpenAI TTS，时长/字节数会有小幅波动。）

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `voice_library.py` | 参考语音库 + 控制维度 → instructions 映射 |
| `markup.py` | 控制标记解析器：带标记文本 → 片段列表(语音/静音) |
| `tts.py` | OpenAI TTS 合成 + ffmpeg 生成静音/拼接 |
| `demo.py` | 演示入口，三种配置对比 + 风格变体 |
