# 实验 6-7：用 Fish Audio S1 调节客服语音的表达

“太好了！您的订单已确认。让我查一下发货时间。预计明天下午送达。”同一位客服说这三句时，哪一句适合说快一点？在哪儿停一下，听众会觉得客服正在查订单？先听一遍[直接合成的版本](output/A_no_control_markers.mp3)，再听[逐段调节的版本](output/C_24_reference_library.mp3)，记下最容易听出区别的那几个字。

[English](#english)

<a id="learning-0"></a>

## 理解问题与方法

主模型在回答里标出要用的情绪、语速和风格，执行程序读这些标记，为不同片段挑选参考音频，把文字和参考音一起送给 Fish Audio S1。它使用 S1 的零样本参考音接口 `ReferenceAudio`。例如，“太好了”用的是高兴、快速、随意的组合，最后报送达时间时换回中性、正常语速和正式风格。可以先看程序选了哪条参考音，再听成片有没有传达出相应的变化。

同一说话人的参考音覆盖三种可以分别调节的属性，每种组合对应一条录音：

- 情绪：neutral / happy / frustrated / thinking；
- 语速：normal / fast / slow；
- 风格：formal / casual；
- 总计：4 × 3 × 2 = 24 条。

`[THINKING]` 产生 1.2s 思考停顿和 S1 `(uncertain)嗯……`；`[SIGH]`、`[LAUGH:small]`、`[BREATH]` 分别发送 S1 原生 `(sighing)`、`(chuckling)`、`(gasping)`，不再用“唉/哈哈”等文字冒充非语言音。所有 Fish 请求显式指定 `backend="s1"`。

<a id="learning-1"></a>

## 准备环境与输入

听已生成的录音只需打开文件。如果要自己做一遍合成，在仓库根目录准备第六章的 Python 环境，系统中还需安装 ffmpeg 和 ffprobe。

```bash
uv sync --locked --python 3.12 --extra ch6 --extra dev
source .venv/bin/activate
# Windows PowerShell 用 .\.venv\Scripts\Activate.ps1，cmd 用 .\.venv\Scripts\activate.bat
# 使用 pip 时，可在虚拟环境中执行 python -m pip install -e ".[ch6]"
cd chapter6/controllable-tts
python -m pip install -r requirements.txt
cp env.example .env
```

配置 `FISH_API_KEY` 与一个你拥有或获准克隆的 `FISH_BASE_REFERENCE_ID`。建库程序使用同一 基础音色 和 Fish S1 原生情感标记，合成 24 条约 5 秒的参考音；`reference_audio/manifest.json` 保存每条音频的情绪、语速、风格、转写、时长和 SHA-256。运行时会验证数量与 hash，缺任何一条都拒绝合成。

```bash
run=$(mktemp -d validation/my-run.XXXXXX)
python build_reference_library.py --output-dir "$run/reference_audio"
python demo.py --manifest "$run/reference_audio/manifest.json" \
  --output-dir "$run/output" --evidence "$run/evidence.json"
```

<a id="learning-2"></a>

## 按照步骤完成实验

2026 年 7 月 29 日的三份成片使用相同的订单答复。先比较 A 和 B，两者都把标记删掉，整段文字一次合成；再比较 B 和 C，听“让我查一下”前后有什么变化。

| 录音 | 合成时给 S1 的条件 | 成片时长 |
|---|---|---:|
| [A 无标记](output/A_no_control_markers.mp3) | 直接指定原声音色的 `reference_id` | 5.355 秒 |
| [B 单一参考音](output/B_single_reference.mp3) | 整段用一条中性、正常语速、正式风格的参考音 | 5.904 秒 |
| [C 按片段选参考音](output/C_24_reference_library.mp3) | 从 24 条参考音中选取相应组合，按标记加入停顿和填充音 | 8.305 秒 |

沿着[解析记录](validation/latest.json)找 `[THINKING]`。它既切换了参考音，也插入了 1.2 秒静音和填充音。因此 C 比 B 长约 2.4 秒，不能把这段差值都算作语速变慢。若想单独检验语速，可以固定情绪、风格和停顿，只换 `SPEED` 标记，再听同一句话。

<a id="learning-3"></a>

## 分析结果与形成判断

先用自己的话描述差别，再看[模型听评记录](validation/audio_quality_study.json)。2026 年 7 月 30 日，Mistral Voxtral（`voxtral-small-latest`）听了三轮相同的录音。每轮隐去配置名，轮换播放顺序，请它从自然度、情绪匹配、思考停顿、音色一致性和真人客服感五方面打分，并给出听觉依据。三个位置都轮到一次，有助于观察顺序的影响；三轮评分都来自同一个模型。

| 五分制均分 | A | B | C |
|---|---:|---:|---:|
| 五项总均分 | 3.93 | 3.20 | 4.60 |
| 其中“真人客服感”一项 | 4.00 | 3.33 | 4.67 |

这段订单答复里，Voxtral 给逐段调节的 C 打分最高；它听 B 的整体感觉却不及 A。读者如果更喜欢 A，可以挑一句说明理由：听清送达时间、感到对方语气自然、察觉客服正在查询，是三个不同的判断。要了解真实来电者的偏好，还需邀请听众试听。

<a id="learning-5"></a>

## 排查问题与查阅资料

- `python -m pytest -q` 可离线检查标记解析、参考音组合和音频拼接等环节。
- `evaluate_audio_quality.py` 可通过 Gemini、OpenRouter 音频路由、DashScope Omni 或 Mistral Voxtral 重新听评，记录实际使用的服务和失败尝试。默认使用 `output/` 中的三份成片。
- `validate_artifacts.py` 离线核对参考音和成片的哈希、时长、标记路由、听评排列与重算均分，结果写入 `validation/acceptance.json`。归档实验估计发出 30 次 Fish 请求（建库 24 次，三组分别为 1、1、4 次），SDK 没有给出逐次美元费用。
- 复核历史文件时会遇到一处编号差异。[旧版听评文件](https://github.com/bojieli/ai-agent-book/blob/efbde98ad6a5367fc949e7608a3b6366439d5426/chapter6/controllable-tts/validation/audio_quality_study.json)的 SHA-256 与[原验收记录](validation/acceptance.json)吻合。逐字段对照，现存听评文件只改了 `experiment`（从 `9-5` 改为 `6-6`）；三轮原始评分、匿名映射和均分均相同。本书现行编号为 6-7。

## English

This is real Fish Audio S1 zero-shot voice cloning. A builder renders a same-speaker 4×3×2 reference library, hashes all 24 clips, and the runtime selects those real clips through inline `ReferenceAudio`. Native S1 `(sighing)`, `(chuckling)`, `(gasping)`, and `(uncertain)` controls replace the former OpenAI/onomatopoeia approximation. `demo.py` produces and records the required no-marker, single-reference, and 24-reference comparison.
