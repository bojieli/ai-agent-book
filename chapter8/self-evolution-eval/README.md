## English

# Experiment 8-6: Designing an Evaluation Dataset for Self-Evolving Agents (★★★)

Evaluating an agent's "self-evolution" capability—i.e., **discovering, creating, and reusing tools on its own** when no ready-made tool is available—
requires a specialized evaluation dataset and validation methodology. The challenge lies in: tasks must not hint at tool names (otherwise it degenerates into "memorizing fixed tool patterns"),
and "whether the result is correct" is only the most superficial signal; we also need to see **how it discovers, how well it creates, and whether it will reuse next time**.

This directory provides a runnable, complete implementation: **a dataset of 20 cross-domain tasks + a four-layer hierarchical validation harness + a controllable reference agent + a one-click demo**.

## Directory Structure

| File | Description |
| --- | --- |
| `dataset.json` | 20 tool-requiring tasks across different domains. Each entry contains a goal description (without hinting at tool names), a reference solution (recommended libraries + API examples), known pitfalls (deprecated libraries / paid or registration-required APIs), and correctness criteria. |
| `harness.py` | Four-layer validation harness: `FourLayerEvaluator.evaluate(task, trajectory, variant_trajectory)`. |
| `agent.py` | Reference agent under test (controllable mock version of a self-evolving agent) + `ToolRegistry`. |
| `demo.py` | One-click demo: `python demo.py`. |
| `config.py` | Reads API Key, constructs an OpenAI-compatible client. |
| `requirements.txt` / `env.example` | Dependencies and environment variable example. |

## Dataset Design Principles

1. **State only the goal, do not hint at tool names.** For example, "Get the subtitles of a YouTube video" instead of "Use `youtube-transcript-api`";
   "Query real-time cryptocurrency price trends" instead of "Use the CoinGecko API". This truly tests the agent's **discovery/creation** ability,
   rather than its memory of a specific library name.
2. **20 different domains**: Multimedia, Finance/Cryptocurrency, Scientific Computing, Geocoding, Social Media, IoT, Weather, NLP, Image,
   PDF, Astronomy, Chemistry, Bioinformatics, Audio, Exchange Rates, Stocks, Geospatial, RSS, QR Codes, Time Zones. The more diverse the domains, the better
   to prevent the model from applying fixed patterns.
3. Each task includes a **reference solution** (`reference_solution`: list of recommended open-source libraries + typical API examples) and
   **known pitfalls** (`known_pitfalls`: `deprecated_libraries`, `paid_or_registration_apis`),
   used as judgment criteria for layers 2 and 3.
4. `correctness_criteria` provides verifiable criteria for layer 1 (regex or keywords); `discovery_keywords` provides keywords for layer 2
   to determine if the search is relevant; `tool_name` + `variant_goal` support layer 4's "whether the second similar task reuses the tool".
5. `mock_answer` is only used to drive the **controllable reference agent** in this repository through the harness; the real agent under test does not depend on it.

## Four-Layer Hierarchical Validation

The harness takes the **execution trajectory** of an agent under test (`trajectory`: sequence of tool calls + created tool code + final answer;
schema is in the comments at the top of `agent.py`) and outputs scores for each of the four layers and an overall evaluation:

| Layer | Name | Method | Criteria Source |
| --- | --- | --- | --- |
| **L1** | Task Correctness | Rule/criteria check of the final answer | `correctness_criteria` |
| **L2** | Tool Discovery Effectiveness | Heuristic analysis of search keywords / whether web pages were accessed / which library was chosen | `discovery_keywords` + `reference_solution` + `known_pitfalls` |
| **L3** | Tool Creation Quality | **LLM-as-a-Judge scoring based on a Rubric** (Error Handling / Parameter Validation / Documentation / Robustness, each 0-3) | Tool code created by the agent under test |
| **L4** | Tool Reuse Capability | Analyze the trajectory of the "second similar task": whether it directly retrieves a registered tool instead of repeating the search and creation | Action sequence of `variant_trajectory` |

- **L2** is purely heuristic (no LLM needed): Selected recommended library (0.40) + Search is relevant (0.25) + Avoided pitfalls (0.25) + Accessed web page (0.10).
  Choosing a deprecated library or paid API results in a "failed to avoid pitfalls" judgment.
- **L3** is the only layer that must call an LLM: the tool function code is given to the judge, which returns JSON scores and a Chinese comment based on the 4-dimensional Rubric.
- **L4** distinguishes between `retrieve_tool` (reuse) and `search`+`create_tool` (redundant work) based on the action sequence of the second similar task (`variant_goal`).
- If a layer is not applicable (e.g., the reuse trajectory does not generate a new tool, so L2/L3 are marked N/A), the overall score is re-normalized by weight among the available layers.

## How to Evaluate Your Own Agent with the Harness

Have your agent under test produce a trajectory conforming to the schema in `agent.py` (`steps` / `created_tools` / `final_answer`),
and reuse the same `ToolRegistry` for the second similar task. Then:

```python
from harness import FourLayerEvaluator
evaluator = FourLayerEvaluator(judge_model="gpt-5.6-luna")          # Default: run all four layers
# Run only deterministic layers (no internet needed): evaluator = FourLayerEvaluator(layers=("L1","L2","L4"))
report = evaluator.evaluate(task, first_trajectory, variant_trajectory)
print(report["layers"], report["summary"]["overall"])
```

`layers=` is used to select which layers to actually run—only **L3** requires an internet connection to call the LLM; removing L3 allows for fully offline evaluation.
Unselected layers are recorded as `score=None` (N/A), and the overall score is re-normalized by weight among the available layers.

## Running

```bash
pip install -r requirements.txt
cp env.example .env      # Fill in OPENAI_API_KEY (default provider=openai, model gpt-5.6-luna)
python demo.py                       # Default: strong runs 3 tasks + weak runs 1 as control (online, includes L3)
python demo.py --quick               # Quick demo: strong / weak each run only 1 task, saves time and money
python demo.py --tasks task-01,task-07   # Specify which task IDs to evaluate
python demo.py --help                # View all parameters (Chinese description)
```

**Full Parameters** (`python demo.py --help`):

| Parameter | Effect |
| --- | --- |
| `--all` | Evaluate all 20 tasks (default: automatically switches to result table output, no per-task scrolling) |
| `--tasks IDS` | Comma-separated task IDs, specify which ones to evaluate |
| `--quick` | strong / weak each run only 1 task |
| `--layers L1,L2,L4` | Select which validation layers to run (only **L3** needs internet; remove it for offline) |
| `--profile {strong,weak,both}` | Select the reference profile under test; default retains the default (strong all + weak first) |
| `--offline` | Offline mode: does not call any LLM (strong uses offline tool templates), automatically skips L3 |
| `--provider {openai,moonshot,ark}` | Override the provider |
| `--agent-model` / `--judge-model` | Override the tool-creation model / L3 judge model |
| `--table` | Only print the "per task × per layer" result table, do not print per-task detailed reports |
| `--output PATH` | Write the complete scoring results (including per-layer details) to a JSON file |

`demo.py` will: print a dataset overview and a few task examples without hinting at tool names → run the four-layer validation with the **strong** reference agent → run the **weak** reference agent as a control → finally print a **per task × per layer result table**, comparing scores across tasks on the four layers horizontally.

### Offline Run Output (No API Key Needed, `python demo.py --all --offline --profile both`)

Runs only the three deterministic layers (L1/L2/L4, L3 is marked N/A), fully reproducible, used to demonstrate the "per task × per layer" result table and the strong/weak differentiation:

```text
Per Task × Per Layer Result Table (N/A = Layer not applicable or not selected)
------------------------------------------------------------------------------
Task     Domain               Profile  L1     L2     L3   L4     Overall
task-01  Multimedia           strong   1.000  1.000  N/A  1.000  1.000
task-02  Financial Data / Crypto strong 1.000  1.000  N/A  1.000  1.000
...
task-10  Document Processing  strong   1.000  0.750  N/A  1.000  0.917
task-19  Encoding / QR Code   strong   1.000  0.750  N/A  1.000  0.917
...
task-01  Multimedia           weak     1.000  0.000  N/A  0.000  0.467
task-03  Scientific Computing weak     1.000  0.250  N/A  0.000  0.550
task-10  Document Processing  weak     1.000  0.400  N/A  0.000  0.600
...
```

Strong scores are generally perfect on L2 (Discovery)/L4 (Reuse); weak scores are significantly lower due to choosing deprecated/paid libraries and never reusing; both can have L1 = 1 (getting the answer right by chance)—which precisely demonstrates that "correct result" is insufficient for judging self-evolution capability. **L3 (Tool Creation Quality) requires an internet connection to call the LLM judge**; removing `--offline` and configuring an API Key will add it back (see the online output below).

### Online Run Output (Includes L3, Excerpt)

Strong (good discovery + high-quality tool generated by LLM + reuse):

```text
■ Task task-01 (Multimedia) | Profile=strong
  L1 Task Correctness     : 1.000
  L2 Tool Discovery Effectiveness : 1.000  | Selected recommended library=True Avoided pitfalls=True (Selected library: ['youtube-transcript-api'])
  L3 Tool Creation Quality   : 1.000  | Rubric 4-dimension total 12/12
       Rubric: Error Handling=3 Parameter Validation=3 Documentation=3 Robustness=3
       LLM-Judge Comment: The code excels in error handling, parameter validation, documentation completeness, and robustness...
  L4 Tool Reuse Capability   : 1.000  | Directly retrieved and reused a registered tool (no repeated search/creation)
  >> Overall score   : 1.000
    [Reuse Probe] Action sequence for the second similar task: ['retrieve_tool', 'call_tool', 'final_answer']
```

Weak (bad discovery: chose deprecated library pytube + rough stub + never reuses):

```text
■ Task task-01 (Multimedia) | Profile=weak
  L1 Task Correctness     : 1.000
  L2 Tool Discovery Effectiveness : 0.000  | Selected recommended library=False Avoided pitfalls=False (Selected library: ['pytube (subtitle/caption feature has been broken for a long time)'])
  L3 Tool Creation Quality   : 0.000  | Rubric 4-dimension total 0/12
       LLM-Judge Comment: The code lacks error handling, parameter validation, and documentation, and the implementation does not meet the task objective.
  L4 Tool Reuse Capability   : 0.000  | Did not reuse; repeated search and tool creation
  >> Overall score   : 0.350
    [Reuse Probe] Action sequence for the second similar task: ['search', 'select_library', 'create_tool', 'register_tool', 'call_tool', 'final_answer']
```

The two profiles are clearly differentiated on L2/L3/L4; note that weak's L1 can still be 1 (getting the answer right by chance), which precisely demonstrates that "correct result" is insufficient for judging self-evolution capability—discovery/creation/reuse must be examined hierarchically.

## Configuration / How to Adapt

- **Switch Model**: `AGENT_MODEL` (the Agent under test that creates tools), `JUDGE_MODEL` (Layer 3 judge, default `gpt-5.6-luna`).
- **Switch Provider / Gateway**: Default `PROVIDER=openai`, reads `OPENAI_API_KEY`; also supports `PROVIDER=moonshot` (`MOONSHOT_API_KEY`)
  or `PROVIDER=ark` (`ARK_API_KEY`), automatically switches `base_url` and default model (see `config.py`).
- **Switch Task / Input**: Edit `dataset.json` to add new tasks (follow the principle of "state only the goal, do not hint at tool names"), or use `--tasks task-xx,...`
  to specify which tasks to evaluate; feed your own Agent's trajectory (following the schema at the top of `agent.py`) into `FourLayerEvaluator.evaluate` to evaluate a real Agent.
- **Unified Fallback**: If the selected provider's API key is missing but `OPENROUTER_API_KEY` is set, it will automatically switch to OpenRouter,
  and map the model name to `openai/gpt-5.6-luna` / `anthropic/claude-opus-4.8`, etc. (see `config.py`).

## Limitations

- The built-in `SelfEvolutionAgent` is a **controllable reference Agent** (mock version), used to run the four-layer harness and demonstrate the distinction between strong and weak,
  not a real networked strong Agent; L1's "accidental correct answer" is precisely used to illustrate that "correct results alone are insufficient to judge self-evolution capability."
- L3 relies on LLM-as-a-Judge, so scores may fluctuate slightly with the judge model and sampling; L2/L4 are interpretable heuristics with criteria hardcoded in the harness.
- In `--offline` mode, the strong profile uses **offline tool templates** (instead of actually calling an LLM to generate tools) to create tools, so **L3 cannot run offline** (recorded as N/A);
  it is used to deterministically reproduce L1, L2, and L4 along with the result table when no API key is available. To evaluate real tool creation quality, you still need to run L3 online.
- The dataset consists of 20 teaching-scale samples, covering a wide range but with only 1 sample per domain, emphasizing methodological demonstration rather than statistical significance.

---

## 中文

# 实验 8-6：为自我进化 Agent 设计评估数据集（★★★）

评估一个 Agent 的"自我进化"能力——即在没有现成工具时，**自己去发现、创造并复用工具**——
需要一套专门的评估数据集与验证方法。难点在于：任务不能暗示工具名（否则退化成"记忆固定工具模式"），
而且"结果对不对"只是最表层的信号，还要看它**怎么发现、造得好不好、下次会不会复用**。

本目录给出一套可运行的配套实现：**20 个跨领域任务的数据集 + 四层分层验证 harness + 一个可控参考 Agent + 一键演示**。

## 目录结构

| 文件 | 说明 |
| --- | --- |
| `dataset.json` | 20 个不同领域的工具需求任务。每条含 目标描述（不暗示工具名）、参考方案（推荐库 + API 示例）、已知陷阱（废弃库 / 需付费注册的 API）、正确性判据。 |
| `harness.py` | 四层验证 harness：`FourLayerEvaluator.evaluate(task, trajectory, variant_trajectory)`。 |
| `agent.py` | 参考被测 Agent（可控 mock 版自我进化 Agent）+ `ToolRegistry` 工具注册表。 |
| `demo.py` | 一键演示：`python demo.py`。 |
| `config.py` | 读取 API Key、构造 OpenAI 兼容客户端。 |
| `requirements.txt` / `env.example` | 依赖与环境变量示例。 |

## 数据集设计原则

1. **只说目标、不暗示工具名**。例如"获取某 YouTube 视频字幕"而非"用 `youtube-transcript-api`"；
   "查询加密货币实时价格趋势"而非"用 CoinGecko API"。这样才能真正考察 Agent 的**发现/创造**能力，
   而不是它对某个库名的记忆。
2. **20 个不同领域**：多媒体、金融/加密货币、科学计算、地理编码、社交媒体、IoT、天气、NLP、图像、
   PDF、天文、化学、生物信息、音频、汇率、股票、地理空间、RSS、二维码、时区。领域越分散，越能避免
   模型套用固定模式。
3. 每条任务都附 **参考方案**（`reference_solution`：推荐开源库列表 + 典型 API 示例）与
   **已知陷阱**（`known_pitfalls`：`deprecated_libraries` 废弃库、`paid_or_registration_apis` 需付费/注册的 API），
   供第 2、3 层做判定依据。
4. `correctness_criteria` 给出第 1 层的可核对判据（正则或关键词）；`discovery_keywords` 给出第 2 层
   判断"搜索是否切题"的关键词；`tool_name` + `variant_goal` 支撑第 4 层"第二次相似任务是否复用"。
5. `mock_answer` 仅用于驱动本仓库的**可控参考 Agent** 跑通 harness，真实被测 Agent 不依赖它。

## 四层分层验证

harness 输入一条被测 Agent 的**运行轨迹**（`trajectory`：工具调用序列 + 创造的工具代码 + 最终答案；
schema 见 `agent.py` 顶部注释），输出四层各自分数与总评：

| 层 | 名称 | 方法 | 判据来源 |
| --- | --- | --- | --- |
| **L1** | 任务正确性 | 规则/判据核对最终答案 | `correctness_criteria` |
| **L2** | 工具发现有效性 | 启发式分析搜索关键词 / 是否访问网页 / 选了哪个库 | `discovery_keywords` + `reference_solution` + `known_pitfalls` |
| **L3** | 工具创造质量 | **LLM-as-a-Judge 按 Rubric 打分**（错误处理 / 参数校验 / 文档 / 健壮性，各 0-3） | 被测 Agent 创造的工具代码 |
| **L4** | 工具复用能力 | 分析"第二次相似任务"轨迹：是否直接检索已注册工具而非重复搜索创建 | `variant_trajectory` 的动作序列 |

- **L2** 是纯启发式（无需 LLM）：选中推荐库(0.40) + 搜索切题(0.25) + 避开陷阱(0.25) + 访问网页(0.10)。
  选了废弃库/付费 API 会被判"未避开陷阱"。
- **L3** 是唯一必须调用 LLM 的层：把工具函数代码交给 judge，按 4 维 Rubric 返回 JSON 分数与中文点评。
- **L4** 通过第二次相似任务（`variant_goal`）的动作序列区分：`retrieve_tool`（复用）vs `search`+`create_tool`（重复劳动）。
- 某层不适用（如复用轨迹不产生新工具，则 L2/L3 记 N/A）时，总评在可用层间按权重重新归一。

## 如何用 harness 评估你自己的 Agent

让你的被测 Agent 产出符合 `agent.py` 中 schema 的轨迹（`steps` / `created_tools` / `final_answer`），
第二次相似任务复用同一个 `ToolRegistry`，然后：

```python
from harness import FourLayerEvaluator
evaluator = FourLayerEvaluator(judge_model="gpt-5.6-luna")          # 默认四层全跑
# 只跑确定性层（不需要联网）：evaluator = FourLayerEvaluator(layers=("L1","L2","L4"))
report = evaluator.evaluate(task, first_trajectory, variant_trajectory)
print(report["layers"], report["summary"]["overall"])
```

`layers=` 用于选择实际运行哪些层——只有 **L3** 需要联网调用 LLM，去掉 L3 即可完全离线评估。
未选中的层记 `score=None`（N/A），总评在可用层间按权重重新归一。

## 运行

```bash
pip install -r requirements.txt
cp env.example .env      # 填入 OPENAI_API_KEY（默认 provider=openai, 模型 gpt-5.6-luna）
python demo.py                       # 默认：strong 跑 3 个任务 + weak 对照 1 个（联网，含 L3）
python demo.py --quick               # 快速演示：strong / weak 各只跑 1 个任务，省时省钱
python demo.py --tasks task-01,task-07   # 指定要评估的任务 id
python demo.py --help                # 查看全部参数（中文说明）
```

**完整参数**（`python demo.py --help`）：

| 参数 | 作用 |
| --- | --- |
| `--all` | 评估全部 20 个任务（默认自动切到结果表输出，不逐条刷屏） |
| `--tasks IDS` | 逗号分隔的任务 id，指定评估哪几条 |
| `--quick` | strong / weak 各只跑 1 个任务 |
| `--layers L1,L2,L4` | 选择运行哪些验证层（仅 **L3** 需联网，去掉即可离线） |
| `--profile {strong,weak,both}` | 选择被测参考画像；缺省保留默认（strong 全部 + weak 第一个） |
| `--offline` | 离线模式：不调用任何 LLM（strong 用离线工具模板），自动跳过 L3 |
| `--provider {openai,moonshot,ark}` | 覆盖供应商 |
| `--agent-model` / `--judge-model` | 覆盖造工具模型 / L3 裁判模型 |
| `--table` | 只打印"每任务 × 每层"结果表，不打印逐任务详报 |
| `--output PATH` | 把完整评分结果（含各层明细）写出为 JSON |

`demo.py` 会：打印数据集概览与几条不暗示工具名的任务示例 → 用 **strong** 参考 Agent 跑完
四层验证 → 用 **weak** 参考 Agent 做对照 → 最后打印一张 **每任务 × 每层结果表**，横向对比各任务在四层上的得分。

### 离线运行输出（无需 API Key，`python demo.py --all --offline --profile both`）

只跑三个确定性层（L1/L2/L4，L3 记 N/A），可完整复现，用来展示"每任务 × 每层"结果表与 strong/weak 区分度：

```text
每任务 × 每层 结果表（N/A = 该层不适用或未选择）
------------------------------------------------------------------------------
任务     领域                 画像    L1     L2     L3   L4     总评
task-01  多媒体               strong  1.000  1.000  N/A  1.000  1.000
task-02  金融数据 / 加密货币  strong  1.000  1.000  N/A  1.000  1.000
...
task-10  文档处理             strong  1.000  0.750  N/A  1.000  0.917
task-19  编码 / 二维码        strong  1.000  0.750  N/A  1.000  0.917
...
task-01  多媒体               weak    1.000  0.000  N/A  0.000  0.467
task-03  科学计算             weak    1.000  0.250  N/A  0.000  0.550
task-10  文档处理             weak    1.000  0.400  N/A  0.000  0.600
...
```

strong 在 L2（发现）/L4（复用）上普遍满分，weak 因选了废弃/付费库且从不复用而显著更低；两者 L1 都可能为 1
（碰巧答对）——正说明"结果正确"不足以评判自我进化能力。**L3（工具创造质量）需联网调用 LLM 裁判**，
去掉 `--offline` 并配置 API Key 后即可补上（见下方联网输出）。

### 联网运行输出（含 L3，节选）

strong（好发现 + LLM 生成的高质量工具 + 复用）：

```text
■ 任务 task-01 (多媒体) | 画像=strong
  L1 任务正确性     : 1.000
  L2 工具发现有效性 : 1.000  | 选中推荐库=True 避开陷阱=True（选库：['youtube-transcript-api']）
  L3 工具创造质量   : 1.000  | Rubric 4 维合计 12/12
       Rubric: 错误处理=3 参数校验=3 文档=3 健壮性=3
       LLM-Judge 点评: 代码在错误处理、参数校验、文档完整性和健壮性方面表现优秀……
  L4 工具复用能力   : 1.000  | 直接检索并复用已注册工具（未重复搜索/创建）
  >> 总评 overall   : 1.000
    [复用探针] 第二次相似任务的动作序列: ['retrieve_tool', 'call_tool', 'final_answer']
```

weak（坏发现：选了废弃库 pytube + 粗糙 stub + 从不复用）：

```text
■ 任务 task-01 (多媒体) | 画像=weak
  L1 任务正确性     : 1.000
  L2 工具发现有效性 : 0.000  | 选中推荐库=False 避开陷阱=False（选库：['pytube（字幕/caption 功能长期失效）']）
  L3 工具创造质量   : 0.000  | Rubric 4 维合计 0/12
       LLM-Judge 点评: 代码缺乏错误处理、参数校验和文档说明，且实现不符合任务目标。
  L4 工具复用能力   : 0.000  | 未复用，重复了搜索与工具创建
  >> 总评 overall   : 0.350
    [复用探针] 第二次相似任务的动作序列: ['search', 'select_library', 'create_tool', 'register_tool', 'call_tool', 'final_answer']
```

两个画像在 L2/L3/L4 上被清晰区分；注意 weak 的 L1 仍可能为 1（碰巧答对），正说明"结果正确"不足以
评判自我进化能力，必须分层看发现 / 创造 / 复用。

## 配置说明 / 如何适配

- **换模型**：`AGENT_MODEL`（被测 Agent 造工具）、`JUDGE_MODEL`（第 3 层裁判，默认 `gpt-5.6-luna`）。
- **换供应商 / 网关**：默认 `PROVIDER=openai`，读 `OPENAI_API_KEY`；也支持 `PROVIDER=moonshot`（`MOONSHOT_API_KEY`）
  或 `PROVIDER=ark`（`ARK_API_KEY`），会自动切换 base_url 与默认模型（见 `config.py`）。
- **换任务 / 输入**：编辑 `dataset.json` 新增任务（保持"只说目标、不暗示工具名"原则），或用 `--tasks task-xx,...`
  指定评估哪几条；把你自己 Agent 的轨迹按 `agent.py` 顶部 schema 喂给 `FourLayerEvaluator.evaluate` 即可评估真实 Agent。
- **统一兜底**：若所选 provider 的 Key 缺失，但设置了 `OPENROUTER_API_KEY`，会自动改走 OpenRouter，
  并把模型名映射到 `openai/gpt-5.6-luna` / `anthropic/claude-opus-4.8` 等（见 `config.py`）。

## 局限

- 内置的 `SelfEvolutionAgent` 是**可控参考 Agent**（mock 版），用于把四层 harness 跑通并展示 strong/weak 的区分度，
  并非真实联网的强 Agent；L1 的"碰巧答对"正是用来说明"结果正确不足以评判自我进化能力"。
- L3 依赖 LLM-as-a-Judge，分数会随裁判模型与采样有小幅波动；L2/L4 为可解释的启发式，判据写死在 harness 中。
- `--offline` 模式下 strong 画像用**离线工具模板**（而非真调 LLM 生成）造工具，因此 **L3 无法离线运行**（记 N/A）；
  它用来在无 API Key 时确定性地复现 L1/L2/L4 三层与结果表。要评估真实的工具创造质量仍需联网跑 L3。
- 数据集为 20 条教学规模样本，覆盖面广但每领域仅 1 条，重在方法论演示而非统计显著性。
