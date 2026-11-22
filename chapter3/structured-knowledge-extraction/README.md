# Experiment 3-12: Extracting Latent Knowledge from Structured Data / 实验 3-12：从结构化数据中提取隐性知识

## 一段案件事实怎样变成可比较的字段？

打开下方运行记录，在 `extractions` 里找到留出样本 `cail2018-0317ae92dc821b04`。先只读 `fact`：这份材料写到被告人主动投案、赔偿被害人并取得谅解。假如要把它和同类材料放进一张表，可以把“是否自首”和“是否取得谅解”分成两列。再看 `extracted`：`surrender` 和 `victim_forgiveness` 都是 `true`，而记录中的 `criminal_record` 是 `null`。最后这一格只说明抽取结果没有给出是否有前科，不能把它读成“无前科”。在看聚类之前先做一次这样的逐格核对，才知道后面拿来比较的是哪些信息。

`campaign.py` 使用官方 CAIL2018 材料，抽取盗窃、故意伤害、诈骗各 120 条用于建模，另各保留 20 条，共 360 条建模与 60 条留出样本。运行得到 16 个通用字段及 12/12/11 个扩展字段，按罪名聚类形成 5/4/2 个原型，共 11 个，并对 12 条留出样本生成解释与独立评审。特征权重来自标准化簇中心差异，表示对原型的区分作用。下文 66 条合成数据的旧版 demo 保留为快速教学入口；交互追问属于该 demo / 应用扩展，正式运行评估固定留出样本的解释。

**为什么三类样本分别分成 5、4、2 组？** 打开[本次运行的聚类记录](validation/runs/20260730T044309Z-3_12-3ab8ec7b/evidence.json)，在 `prototype_model.diagnostics` 里任选一个罪名。程序把同一罪名的 120 条建模样本分别分成 2、3、4、5 组，再算各方案的轮廓系数。这个系数比较样本与本组及最近邻组的距离；在相同数据和特征上，系数越高，说明这样的分组越能把相近的样本放在一起。

拿盗窃罪这组数据手算选择过程：四个系数依次约为 0.055、0.040、0.058、0.061，所以程序选了 5 组。但 5 组只比 4 组高约 0.003。读者可以据此追问，换一个样本划分或随机种子，还会选出 5 组吗？故意伤害罪的最高值约为 0.217，对应 4 组；诈骗罪的最高值约为 0.143，对应 2 组。合起来的 11 个原型描述这批材料在当前编码方式下的分组。接下来再到 `heldout_advice` 查看留出样本怎样与原型匹配，以及哪些字段支持这次匹配。

运行索引：[validation/latest.json](validation/latest.json)；结果与请求记录：[20260730T044309Z-3_12-3ab8ec7b](validation/runs/20260730T044309Z-3_12-3ab8ec7b/)。


一批案例可能反复出现相同的影响因素，但这些因素未必已经被整理成表格。本实验以案例文本为材料，学习从发现字段到结构化抽取，再到归纳典型模式的过程。

[English](#english)

[从案件字段到样本原型](#learning-0) · [选择公开材料或合成样本](#learning-1) · [依次运行抽取与聚类](#learning-2) · [用留出样本检验解释](#learning-3) · [实现与接口](#learning-4) · [排错与参考](#learning-5)

<a id="learning-0"></a>

## 从案件字段到样本原型

流程先提出候选因素，再把每份材料转成结构化记录，最后聚类并总结原型。每一步都可能引入误差：遗漏因素、抽取错误或不合适的聚类，都可能被后续摘要掩盖。

### 这个旧版 demo 是什么

演示如何让 Agent 不把知识库当成“只能检索的静态仓库”，而是**先把数据读懂、从数据本身归纳出结构化的决策逻辑，再基于这套逻辑回答问题**。

以三类罪名（盗窃罪 / 故意伤害罪 / 诈骗罪）的判例为例，完整走通四段流水线：

```
判例文本 ──①自下而上因子发现──▶ 模块化 schema（核心+各罪名扩展）
                                        │
                            ②结构化抽取（用发现的 schema 抽因子）
                                        │
                            ③各罪名内聚类 ──▶ 案件原型 + 层次因子重要性
                                        │
        新案情 ──④对话 Agent（匹配最近原型、按重要性追问、给出建议）◀──┘
```

与“预定义僵化 schema + 回归黑箱”的做法相反，本实验的两个关键创新是：
**因子不预设、由 LLM 从数据里自由归纳**；**判决经验不靠回归拟合刑期、而靠聚类出可解释的案件原型**。

### 四段流水线

**① 自下而上因子发现（`discovery.py`）**  
不预先定义任何字段。把判例文本分批喂给 LLM，让它**自由列出**每一批案例中所有可能影响判决的因素；再用一次 LLM 调用把各批发现的原始因子**归并、去重、规范化**成一个模块化 schema：`core`（适用所有罪名的通用因子：自首、赔偿、认罪认罚、前科累犯……）+ `extensions`（各罪名特有扩展因子：盗窃→涉案金额/入户/团伙，故意伤害→伤害等级/持械/预谋，诈骗→金额/受害人数）。产出 `data/schema.json`（带缓存）。

**② 结构化抽取（`extractor.py`）**  
用发现出来的 schema，从每条判例抽取「核心 + 该罪名扩展」因子（LLM 结构化输出，`response_format=json_object`）。文本未提及的因子返回 `null`。抽取结果缓存到 `data/extracted.jsonl`，一次性抽取后重跑几乎免费。

**③ 聚类成案件原型 + 层次因子重要性（`archetypes.py`）**  
把因子翻译成数值向量：罪名 / 分类因子（如伤害等级）用 one-hot 开关位（不用 1/2/3，避免暗示大小关系）；金额 / 人数取 `ln` 压缩量纲；是非情节取 0/1。**在每个罪名内部**用 KMeans 聚类（k 由轮廓系数自动挑选），得到若干「案件原型」——例如故意伤害罪会自动聚出“轻微伤”、“轻伤”、“持械预谋致重伤”等典型模式。再算两级重要性：

- **全局因子重要性**：每个因子在所有原型之间的区分度（簇间方差占比）→ 全局排序；
- **原型内定义性因子**：每个原型相对全局最突出的因子 + 该原型典型刑期分布（中位 / 区间）。

产出可读、自洽的 `data/archetypes.json`（含标准化参数与簇心）。

**④ 对话式量刑建议 Agent（`advisor_agent.py`）**  
把「案件原型 + 层次因子重要性」当决策逻辑：从用户口语描述抽取已知因子 → 对照**全局因子重要性**追问仍缺失的关键因子 → 把案件**匹配到最近的案件原型**（先按罪名圈定候选，再只在已知维度上比距离）→ 让 LLM 基于该原型的统计数据（典型刑期区间、定义性因子）给出一段有判例支持、可解释的建议（附法律免责声明）。所有刑期数字均来自原型统计，LLM 只负责讲清楚。

<a id="learning-1"></a>

## 选择公开材料或合成样本

想观察字段如何变成聚类输入，可以从随附的 66 条合成样本开始。要复核本章的 11 个原型，应看 `campaign.py` 对公开材料的建模与留出划分。

### 数据说明

`data/cases.jsonl` 是**自带的小样本合成数据**（66 条，覆盖 3 类罪名），由 `generate_data.py` 用已知量刑公式加噪声生成：每条含自然语言 `fact`、结构化真值 `gold`、刑期 `label_months`。关键点是**因子在生成时被“写进”案情文本，发现阶段再从文本里把它们“读”回来**——因子发现完全不依赖生成时的字段列表，因此学到的模式来自数据本身。

**真实目标数据集是 CAIL2018**（中文刑事判决，数百万条）。因体量太大不便随仓库分发才用合成小样本；换成真实数据只需把 `generate_data.py` 换成读取 CAIL 的 `data_*.json`（每行含 `fact`、`meta.accusation`、`meta.term_of_imprisonment`），产出同结构的 `cases.jsonl` 即可，发现 / 抽取 / 聚类 / 对话四段代码无需改动。

<a id="learning-2"></a>

## 依次运行抽取与聚类

先阅读仓库自带的教学样例，人工标注几条你认为重要的因素，再配置模型运行 `demo.py`。比较模型发现的字段与人工标注，并检查几条记录如何归入同一原型。真实数据路径与教学数据路径的准备方式见下文的详细步骤。

### 运行

```bash
# 在仓库根目录使用统一的第 3 章环境
uv sync --locked --python 3.12 --extra ch3

# 切换目录前先激活环境：
# macOS/Linux：
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
# Windows cmd：.venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch3]"

cd chapter3/structured-knowledge-extraction

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env        # 填入 OPENAI_API_KEY（默认模型 gpt-5.6-luna）
python generate_data.py    # 可选：重新生成合成判例数据集（已自带 data/cases.jsonl）
python demo.py             # 跑通 因子发现 → 抽取 → 聚类 → 对话建议 全流程
```

首次运行会调用 LLM 做因子发现（约 7 次）与逐条抽取（约 66 次），结果分别写入 `data/schema.json`、`data/extracted.jsonl`；再次运行直接命中缓存，几乎免费。

### 真实运行输出（节选）

```
阶段 1 自下而上发现的 schema：
  核心通用因子: prior_record 前科 / self_surrender 自首 / compensation 赔偿 /
               guilty_plea 认罪认罚 / victim_reconciliation 谅解 ...
  扩展·盗窃罪:  amount_stolen 盗窃金额 / gang_involvement 团伙 / use_of_weapon 持械
  扩展·故意伤害罪: injury_level 伤害等级[轻微伤/轻伤二级/重伤二级] / premeditation 预谋 ...
  扩展·诈骗罪:  amount_defrauded 诈骗金额 / victim_count 受害人数 / group_crime 团伙

阶段 3 各罪名内聚类（k 由轮廓系数自动选）→ 共 12 个案件原型；全局因子重要性排序：
  1. 罪名  2. 伤害等级=重伤  3. 诈骗金额  4. 盗窃金额  5. 团伙作案  6. 是否预谋 ...
  ▸ 原型#0 [故意伤害罪] 中位 2 月：伤害等级=轻微伤(z=+2.5)
  ▸ 原型#1 [故意伤害罪] 中位 42 月：伤害等级=重伤二级(z=+3.9)、预谋(z=+1.8) —— "持械预谋重伤"型
  ▸ 原型#5 [盗窃罪]     中位 51 月：盗窃金额高、前科/累犯 100% ...

阶段 4 对话：识别到盗窃案缺金额 → 按重要性追问金额/认罪/谅解 → 补全后匹配到 原型#6
         （典型刑期中位 40 月、区间 24~50 月），并引用该原型的关键因子给出建议。
```

<a id="learning-3"></a>

## 用留出样本检验解释

打开[留出样本的解释记录](validation/runs/20260730T044309Z-3_12-3ab8ec7b/evidence.json)，找到编号以 `ae51` 结尾的样本。生成器看到的是抽取字段与匹配原型，评审还会看到该样本的实际标签。可以在实验目录里用 Python 标准库读出两者各自依据的数字：

```python
import json
from pathlib import Path

path = Path("validation/runs/20260730T044309Z-3_12-3ab8ec7b/evidence.json")
cases = json.loads(path.read_text())["heldout_advice"]
case = next(c for c in cases if c["id"] == "cail2018-08f56c05f4baae51")
prototype = case["prototype"]
print(prototype["prototype_size"], prototype["sentence_months"])
print(case["actual_label_months"], case["judge"]["numeric_fidelity"])
```

原型只有一条建模记录，五项刑期统计量都是 4 个月。生成器报告了这个数，并提醒读者样本少、部分特征也不吻合。最后一行依次打印 8 和 4：前者是留出样本的实际刑期（月），后者是独立模型给数字忠实度打的分（满分 4 分）。如果另设一道预测题，让程序直接用原型中位数作答，这一题的绝对误差就是 4 个月。用同一份材料评两种任务，计分依据也要跟着换。

### 先用合成数据理解流程

以下文件早于本页开头的正式 CAIL2018 campaign，仅保留用于快速本地教学。
合成案例与小规模运行只能说明机制，不能验收实验 3-12；正文验收只认
`campaign.py` 及 `validation/latest.json`。

### 检查自己的解释

一个因素在训练样例里经常出现，却在新样例中无帮助，怎样判断它是规律还是数据偏差？

<a id="learning-4"></a>

## 实现与接口

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — judicial case analysis pipeline: bottom-up factor discovery → structured extraction → archetype clustering → conversational advisory Agent.  
> 配套《深入理解 AI Agent》第 3 章——以司法判例分析为例：因子发现 → 结构化抽取 → 案件原型聚类 → 对话式建议 Agent。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

### 文件

| 文件 | 作用 |
|------|------|
| `generate_data.py` | 合成多罪名小样本判例数据集 |
| `discovery.py` | 阶段 ①：自下而上因子发现 → 模块化 schema |
| `extractor.py` | 阶段 ②：用发现的 schema 做结构化抽取（带缓存） |
| `archetypes.py` | 阶段 ③：各罪名内聚类成案件原型 + 层次因子重要性 |
| `advisor_agent.py` | 阶段 ④：对话式量刑建议 Agent（匹配最近原型） |
| `demo.py` | 全流程演示入口 |
| `config.py` | OpenAI 客户端与模型配置 |

<a id="learning-5"></a>

## 排错与参考

### 局限与免责声明

- 本项目**仅用于教学**，演示“从结构化数据中提取隐性知识”这一技术范式。
- 数据为合成、因子集经简化，聚类也无法刻画真实司法量刑的复杂性与非线性。
- **本项目的任何输出都不构成法律意见。** 真实案件量刑受法律条文、司法解释、地域政策与大量具体情节影响，请务必咨询专业律师，切勿据此做任何法律决策。

---

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

This experiment supports a **universal OpenRouter fallback** for its chat LLM.

- If the primary provider key (e.g. `MOONSHOT_API_KEY` / `KIMI_API_KEY` / `OPENAI_API_KEY` / `DOUBAO_API_KEY` …) is present, behavior is unchanged.
- Else if `OPENROUTER_API_KEY` is set, the chat LLM is automatically routed through OpenRouter (`https://openrouter.ai/api/v1`). Model names are mapped automatically: `gpt-*`/`o1-*` → `openai/…`, `claude-*` → `anthropic/claude-opus-4.8`, `kimi-*` → `moonshotai/kimi-k2.6`, ids already containing `/` are kept as-is, and other provider-native ids (e.g. `doubao-*`) fall back to `openai/gpt-5.6-luna`. Set `OPENROUTER_MODEL` to force a specific OpenRouter model id.
- Else a clear error lists the accepted keys.

Add `OPENROUTER_API_KEY=...` to your `.env` (see `env.example`) to enable it.

## English

### Canonical official-data campaign

`python campaign.py` is the acceptance run. It reads the official CAIL2018
archive (cache-only), deterministically materializes a bounded 420-case sample
(360 train/60 held out across three charges), performs live bottom-up discovery
and live modular extraction, selects per-charge clusters with silhouette
diagnostics, and independently judges prototype-only held-out advice. The
official URL/repository revision/archive SHA-256 and bytes, split, raw receipts,
prototype statistics, leakage checks, and legal disclaimer gate are recorded
under `validation/runs/<run-id>/`; `validation/latest.json` is canonical.

The large `data/official/CAIL2018_ALL_DATA.zip` is intentionally ignored. Only
the deterministic sample and validation evidence are versionable.

### Legacy synthetic teaching path (not acceptance evidence)

The files described below predate the canonical official-data campaign. They
remain useful for a fast local walkthrough, but their synthetic cases and
hand-sized run are mechanism illustrations only; they do not satisfy
Experiment 3-12. Only `campaign.py` and `validation/latest.json` can close the
manuscript experiment.

### What this legacy demo is

This lab shows how an Agent can treat a knowledge base not as a “static warehouse you only retrieve from,” but as data to **read, understand, and turn into structured decision logic**—then answer questions using that logic.

Using three charge types (theft / intentional injury / fraud) as examples, it walks a four-stage pipeline:

```
Case texts ──① bottom-up factor discovery──▶ modular schema (core + per-charge extensions)
                                                    │
                                        ② structured extraction (factors via discovered schema)
                                                    │
                                        ③ per-charge clustering ──▶ case archetypes + hierarchical factor importance
                                                    │
        New facts ──④ conversational Agent (match nearest archetype, ask by importance, advise) ◀──┘
```

Unlike “rigid predefined schema + black-box regression,” the two key ideas here are: **factors are not preset—the LLM induces them freely from data**; **sentencing experience is not fit by regression, but by clustering into interpretable case archetypes**.

### Four-stage pipeline

**① Bottom-up factor discovery (`discovery.py`)**  
No fields are predefined. Case texts are batched to the LLM so it can **freely list** factors that may affect the judgment; a second LLM pass **merges, deduplicates, and normalizes** raw factors into a modular schema: `core` (cross-charge factors: surrender, compensation, guilty plea, prior record, …) + `extensions` (charge-specific: theft → amount/home invasion/gang; intentional injury → injury level/weapon/premeditation; fraud → amount/victim count). Output: `data/schema.json` (cached).

**② Structured extraction (`extractor.py`)**  
Using the discovered schema, extract “core + that charge’s extensions” per case (LLM structured output, `response_format=json_object`). Factors not mentioned in the text return `null`. Results cache to `data/extracted.jsonl`; after one full pass, re-runs are nearly free.

**③ Clustering into case archetypes + hierarchical factor importance (`archetypes.py`)**  
Factors become numeric vectors: charge / categorical factors (e.g. injury level) as one-hot (not 1/2/3, to avoid implying order); amounts / counts use `ln` scaling; binary facts as 0/1. **Within each charge**, KMeans clusters (k chosen by silhouette score) produce “case archetypes”—e.g. intentional injury may cluster into “minor injury,” “light injury,” “premeditated armed serious injury,” etc. Two levels of importance:

- **Global factor importance**: how well each factor separates all archetypes (between-cluster variance share) → global ranking  
- **Within-archetype defining factors**: factors most distinctive for each archetype vs global, plus typical sentence distribution (median / range)

Readable output: `data/archetypes.json` (with normalization params and centroids).

**④ Conversational sentencing-advice Agent (`advisor_agent.py`)**  
Uses “archetypes + hierarchical factor importance” as decision logic: extract known factors from the user’s free-form description → ask for still-missing **globally important** factors → **match the nearest case archetype** (filter by charge, then distance on known dims only) → LLM writes an interpretable suggestion grounded in that archetype’s stats (typical sentence range, defining factors), with a legal disclaimer. All sentence numbers come from archetype statistics; the LLM only explains them.

### Run

```bash
# From the repository root: use the shared Chapter 3 environment
uv sync --locked --python 3.12 --extra ch3

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch3]"

cd chapter3/structured-knowledge-extraction

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env        # set the selected provider key (OpenAI or DashScope/Bailian)
python generate_data.py    # optional: regenerate synthetic cases (repo ships data/cases.jsonl)
python demo.py             # full pipeline: discovery → extract → cluster → conversational advice
```

First run calls the LLM for factor discovery (~7 calls) and per-case extraction (~66 calls), writing `data/schema.json` and `data/extracted.jsonl`; later runs hit cache and are nearly free.

### Real run output (excerpt)

```
阶段 1 自下而上发现的 schema：
  核心通用因子: prior_record 前科 / self_surrender 自首 / compensation 赔偿 /
               guilty_plea 认罪认罚 / victim_reconciliation 谅解 ...
  扩展·盗窃罪:  amount_stolen 盗窃金额 / gang_involvement 团伙 / use_of_weapon 持械
  扩展·故意伤害罪: injury_level 伤害等级[轻微伤/轻伤二级/重伤二级] / premeditation 预谋 ...
  扩展·诈骗罪:  amount_defrauded 诈骗金额 / victim_count 受害人数 / group_crime 团伙

阶段 3 各罪名内聚类（k 由轮廓系数自动选）→ 共 12 个案件原型；全局因子重要性排序：
  1. 罪名  2. 伤害等级=重伤  3. 诈骗金额  4. 盗窃金额  5. 团伙作案  6. 是否预谋 ...
  ▸ 原型#0 [故意伤害罪] 中位 2 月：伤害等级=轻微伤(z=+2.5)
  ▸ 原型#1 [故意伤害罪] 中位 42 月：伤害等级=重伤二级(z=+3.9)、预谋(z=+1.8) —— "持械预谋重伤"型
  ▸ 原型#5 [盗窃罪]     中位 51 月：盗窃金额高、前科/累犯 100% ...

阶段 4 对话：识别到盗窃案缺金额 → 按重要性追问金额/认罪/谅解 → 补全后匹配到 原型#6
         （典型刑期中位 40 月、区间 24~50 月），并引用该原型的关键因子给出建议。
```

### Data notes

`data/cases.jsonl` is a **bundled small synthetic sample** (66 cases, 3 charges), produced by `generate_data.py` with a known sentencing formula plus noise: each line has natural-language `fact`, structured ground truth `gold`, and sentence `label_months`. The point is that **factors are written into the narrative at generation time, then “read back” from text at discovery**—discovery does not depend on the generation field list, so patterns come from the data itself.

The **intended real dataset is CAIL2018** (Chinese criminal judgments, millions of rows). Volume makes shipping it impractical; to switch, replace `generate_data.py` with a reader for CAIL `data_*.json` (lines with `fact`, `meta.accusation`, `meta.term_of_imprisonment`) into the same `cases.jsonl` shape—discovery / extract / cluster / dialogue code need not change.

### Files

| File | Role |
|------|------|
| `generate_data.py` | Synthetic multi-charge small case set |
| `discovery.py` | Stage ①: bottom-up factor discovery → modular schema |
| `extractor.py` | Stage ②: structured extraction with discovered schema (cached) |
| `archetypes.py` | Stage ③: per-charge clustering + hierarchical factor importance |
| `advisor_agent.py` | Stage ④: conversational advice Agent (nearest archetype) |
| `demo.py` | End-to-end demo entry |
| `config.py` | OpenAI client and model config |

### Limitations and disclaimer

- **Teaching only**—demonstrates the paradigm “extract latent knowledge from structured data.”
- Data is synthetic, factor set simplified; clustering cannot capture full complexity of real sentencing.
- **No output constitutes legal advice.** Real sentencing depends on statutes, judicial interpretations, local policy, and many case-specific facts—consult a qualified lawyer; do not rely on this project for legal decisions.

---
