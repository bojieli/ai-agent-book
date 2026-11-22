# 用成对音频比较语音微调效果

一次语音微调改变了什么，最直观的证据是同一文本训练前后的实际声音。本项目将音色一致性与声学事件控制分成两条比较路径。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

固定输入文本和生成条件，可以更清楚地观察适配器的作用。留出损失、实际听感和目标事件检测分别提供不同证据；没有哪一个指标能独自概括全部语音质量。

### 把两个语音目标分别测量

实验 8-6 包含两条训练路线：Orpheus 用于观察跨句音色一致性，Sesame CSM 用于控制 `<laughs>`、`<giggles>` 与 `<sighs>`。已有运行 `validation/exp8-6-20260804-v1/` 为每个 LoRA 执行 60 次优化器更新，使用独立的留出损失集，并生成匹配的基座与适配器 WAV 对照。完整适配器、负向比较与运行报告都属于结果的一部分。

<a id="learning-1"></a>

## 准备环境与输入

阅读训练命令前，先确认基础模型、数据文件、适配器输出位置和显存要求。把数据准备、训练和评估看作三个独立步骤：前一步得到的文件，是后一步需要核对的输入。

### 核对数据来源和训练兼容性

上游笔记本使用的 `MrDragonFox/Elise` 数据集在记录时已禁用，因此这次运行使用公开镜像 `maxbsoft/mrdragonfox-elise` 的固定修订 `2cc657c3f94a83df18fcd968b7531ca1a19c7f88`，包含 1,195 行数据。两份 manifest 都记录了这一替换。

`compatibility_failures.json` 记录了 Unsloth CSM 的 pad-token 拒绝和 Transformers bf16 codec/text 合并类型问题。已有 Sesame 训练因此采用标准 PEFT 与 float32，同时保留原定数据规模、60 次更新和完整比较。复现时先核对这些条件，再判断差异来自训练目标还是实现环境。

<a id="learning-2"></a>

## 按照步骤完成实验

先选择 Orpheus 或 Sesame 路线，阅读其数据与目标。按下文准备环境后，保留基础模型输出，再训练并生成对应音频。比较时交替听正向改善与负面案例，避免只挑最好的一段。

### 分别训练，再汇总对照

下面从仓库根目录创建实验环境，分别运行两条训练路线，最后分析同一个输出目录。命令中的 `--system-site-packages` 会继承系统包，使用前要确认已有 GPU 栈与这里的依赖兼容。

```bash
python3 -m venv --system-site-packages .venv-exp8-6
.venv-exp8-6/bin/pip install -r chapter8/speech-sft-experiment/requirements.txt

.venv-exp8-6/bin/python chapter8/speech-sft-experiment/run_orpheus.py \
  --output chapter8/speech-sft-experiment/validation/my-run

.venv-exp8-6/bin/python chapter8/speech-sft-experiment/run_sesame.py \
  --output chapter8/speech-sft-experiment/validation/my-run

.venv-exp8-6/bin/python chapter8/speech-sft-experiment/analyze_campaign.py \
  --run chapter8/speech-sft-experiment/validation/my-run
```

运行器默认使用 `bojieli/...` 适配器仓库。若要发布自己的结果，应通过 `--hf-repo` 指定有写权限的仓库并配置 `HF_TOKEN`；只做本地练习时，需要先调整运行器，跳过发布步骤。

<a id="learning-3"></a>

## 分析结果与形成判断

少量更新能演示学习过程，却不保证广泛泛化。兼容性失败也要与训练效果分开记录；模型根本没有正确加载时，后续音频不能用于比较。

### 理解自动指标的边界

Orpheus 使用的 MFCC 统计余弦相似度是音色代理指标，Sesame 使用的 AudioSet 检测分数是事件存在性的代理指标。它们便于重复计算，但不能替代盲听、MOS 或注册说话人验证。一次训练和评估流程完整结束，仍可能得到负向代理指标；应保留这种结果，并通过配对音频判断下一步需要检验什么。

### 检查自己的解释

怎样组织盲听，让评价者不知道哪段来自微调后模型，又仍能判断目标特征？

## English

# Experiment 8-6: speech SFT acceptance campaign

This directory contains the reproducible local-GPU campaign and its retained
evidence for both speech-training tracks described in the chapter:

- Orpheus cross-sentence voice/timbre consistency
- Sesame CSM control of `<laughs>`, `<giggles>`, and `<sighs>` events

The retained run is `validation/exp8-6-20260804-v1/`. It performed 60 optimizer
updates for each LoRA, used disjoint held-out loss sets, generated matched
base/adapted WAV comparisons, published the full adapters to Hugging Face, and
kept explicit negative comparisons. See the run's `REPORT.md` for results and
limitations.

The retained `compatibility_failures.json` also records the current Unsloth CSM
pad-token rejection and Transformers bf16 codec/text merge mismatch. Sesame was
therefore trained with standard PEFT in float32, without reducing the dataset,
optimizer-step count, or comparison campaign.

## Reproduce

Use a fresh environment because the two upstream notebooks move quickly:

```bash
python3 -m venv --system-site-packages .venv-exp8-6
.venv-exp8-6/bin/pip install -r chapter8/speech-sft-experiment/requirements.txt

.venv-exp8-6/bin/python chapter8/speech-sft-experiment/run_orpheus.py \
  --output chapter8/speech-sft-experiment/validation/my-run

.venv-exp8-6/bin/python chapter8/speech-sft-experiment/run_sesame.py \
  --output chapter8/speech-sft-experiment/validation/my-run

.venv-exp8-6/bin/python chapter8/speech-sft-experiment/analyze_campaign.py \
  --run chapter8/speech-sft-experiment/validation/my-run
```

The runners default to `bojieli/...` adapter repositories. Pass `--hf-repo`
with a repository you can write, or modify the runners to skip publication for
a private local reproduction. `HF_TOKEN` is required for publication.

## Dataset provenance

The upstream notebooks name `MrDragonFox/Elise`. Hugging Face now marks that
dataset disabled. The campaign therefore uses
`maxbsoft/mrdragonfox-elise` at immutable revision
`2cc657c3f94a83df18fcd968b7531ca1a19c7f88`, a public non-disabled mirror of
the 1,195-row Elise corpus. Both manifests record this substitution.

## Interpretation

Execution acceptance and hypothesis support are separate. A run can be
complete while an automatic quality proxy is negative. The MFCC statistic
cosine used for Orpheus is a transparent timbre proxy. The AudioSet detector
scores used for Sesame are event-presence proxies. Neither replaces a blinded
human listening test, MOS, or enrolled-speaker verification, and the report
does not claim perceptual quality from this bounded campaign.
