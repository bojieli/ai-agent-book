## English

# Experiment 8-3: Automatic Optimization of System Prompts (★★)

> Companion code for "Deep Understanding of AI Agents" · Chapter 8
>
> **Automated system prompt learning based on human feedback**: Have a Coding Agent read the system prompt file, identify problematic rules, generate precise modifications, and **actually rewrite the prompt file** to fix the Agent's "excessive transfer" behavior. The scenario is a tau-bench style airline customer service.

## 1. Purpose and Problem

In the initial airline customer service Agent, the manual transfer rules were written vaguely — "transfer only when the request cannot be handled within your scope of action," with emphasis on "customer satisfaction first; transfer to human agent when encountering dissatisfaction; do not argue policies with passengers."

Evaluation revealed that the Agent **over-transfers** — whenever encountering policy disputes (requesting refunds beyond policy, demanding free services, requesting fee waivers), it immediately transfers to a human agent instead of attempting to explain the policy to passengers.

Human expert feedback: Such disputes should be **handled by patiently explaining the policy**, rather than simply transferring. The only two situations that truly require human transfer are: **passenger explicitly requests human agent** and **emergency safety/health risk**.

This experiment demonstrates an automated closed loop: **Human feedback → Coding Agent rewrites system prompt → Re-evaluation and verification**.

## 2. Method and Flow

```text
Initial prompt ──Evaluation──► Exposes "excessive transfer" problem
                                  │
               Human feedback ───┤
                                  ▼
                   Coding Agent (reads file → locates rules → generates precise search/replace edits → rewrites file)
                                  │  Displays actual diff
                                  ▼
             Automatically optimized prompt ──Evaluation──► Boundary set accuracy ↑ and holdout set does not degrade
                                  │
               Control: manually tuned prompt ──Evaluation──►
```

Two groups of evaluation cases (5 each, cost-controlled with reproducible conclusions):

- **Holdout task set**: Normal requests. 3 should be handled by the Agent itself (rebooking / baggage allowance / seat selection), 2 should be transferred (passenger explicitly requests human / emergency safety). Used to verify that optimization **does not break existing correct behavior**.
- **Boundary case set**: 5 policy disputes (non-refundable ticket refund request / request to waive change fee / small delay compensation claim / request for free upgrade / excess free baggage). Correct behavior is **explain policy, do not transfer**. Used to verify that excessive transfer is fixed.

Criteria (`evaluate.py`): Combination of deterministic rules + LLM-as-judge —
- Cases that should transfer: correct ⇔ `transfer_to_human` was actually called;
- Cases that should not transfer: correct ⇔ no transfer, and LLM judge confirms it properly explained the policy / handled the business according to the rubric.

The Coding Agent (`coding_agent.py`) does not rewrite the entire document, but produces a set of precise `(old_str → new_str)` edits like a real programming Agent, which are applied one by one via exact string replacement; if a match fails, the error is fed back to the model for retry, ensuring modifications are auditable and can produce a diff.

## 3. File Structure

| File | Description |
| --- | --- |
| `demo.py` | Single command to run the complete flow (evaluation → rewrite → re-evaluation → comparison → comparison table) |
| `airline_env.py` | Simplified airline customer service simulation environment: tools (including `transfer_to_human`), Agent loop, 10 test cases |
| `coding_agent.py` | Coding Agent: reads and **rewrites** the system prompt file, outputs diff |
| `evaluate.py` | Evaluator: rules + LLM-as-judge to determine if each case was handled correctly |
| `config.py` | LLM client configuration (default OpenAI `gpt-5.6-luna`, switchable to Moonshot / Volcengine Ark; falls back to OpenRouter when key is missing) |
| `prompts/system_prompt.txt` | Initial system prompt (contains rules that induce excessive transfer) |
| `prompts/system_prompt_manual.txt` | Control group: manually tuned system prompt |
| `runtime/system_prompt_working.txt` | Runtime working copy rewritten by the Coding Agent (reset on each run) |

## 4. Running

```bash
pip install -r requirements.txt
cp env.example .env      # Fill in OPENAI_API_KEY (or just set OPENROUTER_API_KEY for fallback)
python demo.py           # Full run: 10 cases × 3 prompts
python demo.py --quick   # Quick demo: only 2 cases per group, saves time and cost (recommended to run this first)
python demo.py --help    # View all command-line arguments (Chinese descriptions)
python demo.py --dry-run # Offline self-check: only print configuration and selected cases, no API calls
```

Command-line arguments (full Chinese descriptions visible with `python demo.py --help`):

| Argument | Effect | Default |
| --- | --- | --- |
| `--quick` | Only 2 cases per group, saves time and cost | Off |
| `--limit N` | Maximum N cases per group to evaluate (overrides `--quick`) | Unlimited |
| `--group {holdout,boundary,both}` | Select task set for evaluation | `both` |
| `--rounds N` | Maximum retry rounds for Coding Agent's automatic prompt rewriting | `3` |
| `--model NAME` | Override LLM model name (equivalent to `LLM_MODEL`) | See `config.py` |
| `--provider {openai,moonshot,ark}` | Override LLM provider (equivalent to `LLM_PROVIDER`) | `openai` |
| `--output PATH` | Write comparison results (before/after optimization + manual control) as JSON | Not written |
| `--dry-run` | Offline: only print parsed configuration and case count, no API calls | Off |

Default model `gpt-5.6-luna` (reads `OPENAI_API_KEY`; if missing but `OPENROUTER_API_KEY` is present, automatically switches to OpenRouter and maps to `openai/gpt-5.6-luna`), temperature 0 (reproducible results). Full run processes 10 cases × 3 prompts, approximately dozens of API calls, taking several minutes; `--quick` (or `--limit N` specifying cases per group) significantly reduces time for rapid closed-loop verification. Command-line arguments take precedence over environment variables: `--model` / `--provider` override `LLM_MODEL` / `LLM_PROVIDER` in `.env`. Adding `--output output/run.json` writes the comparison table as JSON (`output/` is already ignored by `.gitignore`), facilitating reproduction and secondary analysis. If the corresponding API Key is not set, the program prints a clear Chinese error message and exits, rather than throwing a stack trace.

The optimized working copy is written to `runtime/system_prompt_working.txt` (automatically reset on each run, a generated artifact ignored by `.gitignore`).

## 5. Real Run Results

The table below shows results from one real run (`gpt-5.6-luna`, full 10 cases):

```text
Accuracy Comparison (Holdout set = existing correct behavior must not degrade; Boundary set = excessive transfer should improve)
==========================================================================
System Prompt Version               Holdout Set             Boundary Set
--------------------------------------------------------------------------
Initial prompt (before optimization)   5/5 (100%)            0/5 (0%)
Automatically optimized prompt         5/5 (100%)            1/5 (20%)
Manually tuned version (control)       5/5 (100%)            2/5 (40%)
==========================================================================

【Conclusion】
  · Boundary set accuracy: 0/5 → 1/5 (improvement ✓)
  · Holdout set accuracy: 5 → 5 (no degradation ✓)
```

- **Boundary set**: Before optimization, all 5 cases were "transferred away" (excessive transfer 5/5); after optimization, **transfers completely disappeared (boundary set transfer count 5 → 0)**, fixing the excessive transfer problem; accuracy increased from 0/5 to 1/5 — B5 (excess free baggage) was judged acceptable for proactively explaining weight-based pricing policy; B1/B2/B3/B4 no longer transferred, but the model tended to first ask passengers for order numbers without fully explaining the policy, which was judged as "improper handling" by the strict evaluator — a genuine boundary performance.
- **Holdout set**: 5/5 both before and after optimization, existing correct behavior (including H4/H5 "cases that should transfer still transfer") **did not degrade**.
- The automatically optimized result is close to the **manually tuned control group** (automatic boundary 1/5, manual 2/5, holdout both 5/5); the manual version explained one more case correctly on B2 (request to waive change fee), with the difference within the evaluator's ±1 case fluctuation range.

> Note: Specific numbers may fluctuate by ±1 case depending on model version and sampling, but the conclusion that "boundary set excessive transfer is fixed, holdout set does not degrade, and automatic optimization approaches manual tuning" is stable and reproducible. The table above is from one real run of `gpt-5.6-luna` (since this model only supports default temperature, this run used `LLM_TEMPERATURE=1`).

The Coding Agent's actual rewrite of `system_prompt.txt` (diff excerpt) is printed in [Step 2] of `python demo.py`, with the core change being tightening rules 3 and 4 for transfer to "only transfer when passenger explicitly requests human / emergency safety," and adding a negative rule "never transfer due to policy disputes or passenger dissatisfaction; first explain the policy then offer alternatives."

### Supplement: Model ↔ Scaffolding Trade-off (Two Real Runs with Strong vs Weak Models)

A natural question: **If the model is stronger, is this "automatic prompt rewriting" scaffolding less necessary?** To explore this, we ran the identical closed loop (10 cases × 3 prompts × max 3 rewrite rounds) on a weaker model `gpt-4o-mini` (OpenAI direct connection, `LLM_TEMPERATURE=0`) and compared it with the `gpt-5.6-luna` run above. The boundary set (excessive transfer should improve) **before optimization → after automatic optimization** changes:

| Model | Holdout Set | Boundary Set Before → After Auto Optimization | Auto Optimization Gain | Manually Tuned (Control) |
| --- | --- | --- | --- | --- |
| `gpt-4o-mini` (weaker) | 5/5 → 5/5 (no degradation) | **1/5 → 3/5** | **+2 cases** | 3/5 |
| `gpt-5.6-luna` (stronger) | 5/5 → 5/5 (no degradation) | **0/5 → 1/5** | **+1 case** | 2/5 |

- **Directionally**, the weaker `gpt-4o-mini` gained more from this automatic optimization scaffolding (boundary set +2 cases, 1/5→3/5), outperforming `gpt-5.6-luna`'s +1 (0/5→1/5); after optimization, `gpt-4o-mini` matched its manually tuned version (both 3/5). This aligns with the intuition that "weaker models rely more on scaffolding, while stronger models have higher tolerance for the same baseline prompt."
- **However, two honest caveats are needed to avoid over-interpretation**: (1) The gain difference between the two is only 1 case, falling within the ±1 case evaluator fluctuation band repeatedly stated in this experiment; (2) The sampling conditions differ between the two runs — the weaker model used `temperature=0` (deterministic), while the stronger model used `temperature=1` (with sampling noise) due to only supporting default temperature. Therefore, this is a **directional, non-conclusive** comparison: one can say "the weaker model benefits no less than the stronger model from the scaffolding," but it would be inappropriate to assert based on this 1-case difference that the stronger model "does not need" automatic optimization. The truly robust conclusion remains the one shared by both models — **boundary set excessive transfer is fixed, holdout set does not degrade, and automatic optimization approaches manual tuning**.

## 6. How to Adapt / Extend and Limitations

- **Change model / provider**: `LLM_PROVIDER` can switch between `openai` / `moonshot` / `ark` (all compatible with OpenAI interface), `LLM_MODEL` overrides the model name, `LLM_TEMPERATURE` adjusts sampling temperature (default 0, see `config.py` / `env.example`).
- **Change task / input**: The evaluation case set is in `airline_env.py`'s `CASES` (divided into `holdout` / `boundary` groups); the human feedback driving optimization is `HUMAN_FEEDBACK` at the top of `demo.py`; the initial and manual control prompts are under `prompts/` — modify these to apply the closed loop to your own scenario.
- **Limitation**: The environment is a simplified simulation for educational purposes, with tools returning fixed mock data; the focus is on the closed loop of "human-feedback-driven automatic prompt optimization" rather than a full reproduction of tau-bench. The specific accuracy may vary by ±1 test case depending on the model version and sampling.

---

## 中文

# 实验 8-3：系统提示词的自动优化（★★）

> 《深入理解 AI Agent》配套代码 · 第 8 章
>
> 基于人类反馈的 **自动化系统提示学习**：让一个 Coding Agent 读取系统提示词文件、
> 定位有问题的规则、生成精确修改并 **真的改写 prompt 文件**，从而修复 Agent 的
> "过度转接" 行为。场景为 tau-bench 风格的航空客服。

## 1. 目的与问题

初始的航空客服 Agent 里，人工转接规则写得很含糊——"仅当请求无法在你的行动范围内
处理时才转接"，并且强调"客户满意度第一，遇到不满就转人工，不要与乘客争辩政策"。

评测发现：Agent **过度转接**——一遇到政策争议（要求超政策退款、要求免费、要求豁免
费用）就直接甩给人工，而不尝试向乘客解释政策。

人类专家反馈：这类争议应当 **通过耐心解释政策来处理**，而不是一转了之。真正需要转
人工的只有两种情况：**乘客明确要求人工客服**、**紧急安全/人身健康风险**。

本实验演示一条自动化闭环：**人类反馈 → Coding Agent 改写系统提示词 → 重新评测验证**。

## 2. 方法与流程

```text
初始 prompt ──评测──► 暴露"过度转接"问题
                          │
              人类反馈 ───┤
                          ▼
                   Coding Agent（读文件→定位规则→生成精确 search/replace 编辑→改写文件）
                          │  展示真实 diff
                          ▼
             自动优化后 prompt ──评测──► 边界集正确率↑ 且 保留集不退化
                          │
              对照：人工调优版 prompt ──评测──►
```

两组评测用例（各 5 个，控制成本、结论可复现）：

- **保留任务集 (holdout)**：正常请求。3 个应由 Agent 自行处理（改签 / 行李额 / 选座），
  2 个本就该转接（乘客明确要人工 / 紧急安全）。用来检验优化 **不会破坏既有正确行为**。
- **边界案例集 (boundary)**：5 个政策争议（不可退票要退款 / 要求免改签费 / 小延误索赔 /
  索要免费升舱 / 超额免费行李）。正确行为是 **解释政策、不转接**。用来检验过度转接被修复。

判据（`evaluate.py`）：结合确定性规则 + LLM-as-judge——
- 该转的用例：正确 ⇔ 确实调用了 `transfer_to_human`；
- 不该转的用例：正确 ⇔ 没转接，且 LLM 裁判确认它按 rubric 妥善解释了政策 / 办理了业务。

Coding Agent（`coding_agent.py`）不整篇重写，而是像真实编程 Agent 一样产出一组
`(old_str → new_str)` 精确编辑，由代码逐条做精确字符串替换落盘；匹配不上就把错误反馈
给模型重试，保证修改可审计、可出 diff。

## 3. 文件结构

| 文件 | 说明 |
| --- | --- |
| `demo.py` | 一条命令跑通完整流程（评测→改写→复评→对照→对比表） |
| `airline_env.py` | 精简航空客服模拟环境：工具（含 `transfer_to_human`）、Agent 循环、10 个用例 |
| `coding_agent.py` | Coding Agent：读取并 **改写** 系统提示词文件，输出 diff |
| `evaluate.py` | 评测器：规则 + LLM-as-judge 判定每个用例是否被正确处理 |
| `config.py` | LLM 客户端配置（默认 OpenAI `gpt-5.6-luna`，可切 Moonshot / 火山方舟；缺 Key 时 OpenRouter 兜底） |
| `prompts/system_prompt.txt` | 初始系统提示词（含会诱发过度转接的规则） |
| `prompts/system_prompt_manual.txt` | 对照组：人工调优版系统提示词 |
| `runtime/system_prompt_working.txt` | 运行时由 Coding Agent 改写的工作副本（每次运行重置） |

## 4. 运行

```bash
pip install -r requirements.txt
cp env.example .env      # 填入 OPENAI_API_KEY（或仅设 OPENROUTER_API_KEY 走兜底）
python demo.py           # 完整运行：10 个用例 × 3 份 prompt
python demo.py --quick   # 快速演示：每组只取 2 个用例，省时省钱（推荐先跑这个）
python demo.py --help    # 查看全部命令行参数（中文说明）
python demo.py --dry-run # 离线自检：只打印配置与选中用例，不调用任何 API
```

命令行参数（`python demo.py --help` 可见完整中文说明）：

| 参数 | 作用 | 默认 |
| --- | --- | --- |
| `--quick` | 每组只取 2 个用例，省时省钱 | 关闭 |
| `--limit N` | 每组最多评测 N 个用例（覆盖 `--quick`） | 不限 |
| `--group {holdout,boundary,both}` | 选择评测的任务集 | `both` |
| `--rounds N` | Coding Agent 自动改写提示词的最大重试轮数 | `3` |
| `--model NAME` | 覆盖 LLM 模型名（等价于 `LLM_MODEL`） | 见 `config.py` |
| `--provider {openai,moonshot,ark}` | 覆盖 LLM 提供商（等价于 `LLM_PROVIDER`） | `openai` |
| `--output PATH` | 把优化前后 + 人工对照的对比结果写成 JSON | 不写 |
| `--dry-run` | 离线：只打印解析后的配置与用例数，不调用 API | 关闭 |

默认模型 `gpt-5.6-luna`（读取 `OPENAI_API_KEY`；缺失时若有 `OPENROUTER_API_KEY` 则自动改走 OpenRouter 并映射到 `openai/gpt-5.6-luna`），温度 0（结果可复现）。完整运行跑
10 个用例 × 3 份 prompt，约几十次 API 调用、数分钟；`--quick`（或 `--limit N` 指定每组
用例数）会显著缩短耗时，用于快速验证闭环。命令行参数优先级高于环境变量：`--model` /
`--provider` 会覆盖 `.env` 中的 `LLM_MODEL` / `LLM_PROVIDER`。加 `--output output/run.json`
可把对比表落盘为 JSON（`output/` 已被 `.gitignore` 忽略），便于复现与二次分析。若未设置
对应 API Key，程序会打印清晰的中文错误提示并退出，而不是抛出堆栈。

优化后的工作副本会写入 `runtime/system_prompt_working.txt`（每次运行自动重置，属生成
工件，已被 `.gitignore` 忽略）。

## 5. 真实运行结论

下表为一次真实运行（`gpt-5.6-luna`，完整 10 用例）的结果：

```text
正确率对比（保留任务集 = 既有正确行为不能退化；边界案例集 = 过度转接应改善）
==========================================================================
系统提示词版本                   保留任务集(holdout)      边界案例集(boundary)
--------------------------------------------------------------------------
初始 prompt(优化前)          5/5 (100%)            0/5 (0%)
自动优化后 prompt            5/5 (100%)            1/5 (20%)
人工调优版(对照)               5/5 (100%)            2/5 (40%)
==========================================================================

【结论】
  · 边界案例集正确率：0/5 → 1/5 （提升 ✓）
  · 保留任务集正确率：5 → 5 （未退化 ✓）
```

- **边界案例集**：优化前 5 个用例全部"一转了之"（过度转接 5/5），优化后 **转接彻底消失
  （边界集转接数 5 → 0）**，过度转接问题被修复；正确率从 0/5 升到 1/5——B5（超额免费行李）
  由主动解释重量计费政策而被判合格，B1/B2/B3/B4 虽不再转接，但模型倾向先向乘客索要订单号、
  未充分把政策解释到位，被严格的裁判判为"处理不当"，属于真实的边界表现。
- **保留任务集**：优化前后均 5/5，既有正确行为（含 H4/H5"该转的仍会转"）**未退化**。
- 自动优化后的效果接近 **人工调优版对照组**（自动边界 1/5、人工 2/5，保留均 5/5）；人工版在
  B2（要求免改签费）上多解释到位一例，差距在裁判的 ±1 个用例波动范围内。

> 注：具体数字可能随模型版本与采样有 ±1 个用例的波动，但"边界集过度转接被修复、保留集不退化、
> 且与人工调优接近"的结论稳定可复现。上表为 `gpt-5.6-luna` 的一次真实运行（因该模型仅支持默认
> 温度，本次以 `LLM_TEMPERATURE=1` 运行）。

Coding Agent 对 `system_prompt.txt` 的真实改写（diff 节选）会在 `python demo.py` 的
【步骤 2】中打印，核心是把第 3、4 条转接规则收紧为"仅乘客明确要求人工 / 紧急安全才转"，
并新增负面规则"绝不因政策争议或乘客不满而转接，应先解释政策再给替代方案"。

### 补充：模型 ↔ 脚手架此消彼长（强模型 vs 弱模型的两次真实运行）

一个自然的问题：**模型更强，这套"自动改 prompt"的脚手架是不是就不那么必要了？**
为此我们把完全相同的闭环（10 用例 × 3 份 prompt × 最多 3 轮改写）在一个较弱模型
`gpt-4o-mini`（OpenAI 直连，`LLM_TEMPERATURE=0`）上又真实跑了一次，与上文
`gpt-5.6-luna` 的运行对照。边界案例集（过度转接应改善）的**优化前 → 自动优化后**变化：

| 模型 | 保留集(holdout) | 边界集 优化前 → 自动优化后 | 自动优化增益 | 人工调优版(对照) |
| --- | --- | --- | --- | --- |
| `gpt-4o-mini`（较弱） | 5/5 → 5/5（未退化） | **1/5 → 3/5** | **+2 个用例** | 3/5 |
| `gpt-5.6-luna`（较强） | 5/5 → 5/5（未退化） | **0/5 → 1/5** | **+1 个用例** | 2/5 |

- **方向上**，较弱的 `gpt-4o-mini` 从这套自动优化脚手架里拿到的增益更大（边界集 +2 个用例，
  1/5→3/5），强于 `gpt-5.6-luna` 的 +1（0/5→1/5）；且优化后 `gpt-4o-mini` 已追平其人工调优版
  （均 3/5）。这与"弱模型更依赖脚手架、强模型对同一条基线 prompt 的容错更高"的直觉一致。
- **但需诚实标注两点，避免过度解读**：(1) 两者增益之差仅 1 个用例，正落在本实验反复申明的
  ±1 个用例裁判波动带内；(2) 两次运行采样条件不同——弱模型 `temperature=0`（确定性），
  强模型因仅支持默认温度而 `temperature=1`（有采样噪声）。因此这是一次**方向性、非结论性**的
  对照：可以说"弱模型从脚手架获益不少于强模型"，但不宜据这 1 个用例的差断言强模型"就不需要"
  自动优化。真正稳健的结论仍是两模型共有的那条——**边界集过度转接被修复、保留集不退化、
  且自动优化逼近人工调优**。

## 6. 如何适配 / 扩展与局限

- **换模型 / 供应商**：`LLM_PROVIDER` 可切换 `openai` / `moonshot` / `ark`（均兼容 OpenAI 接口），
  `LLM_MODEL` 覆盖模型名，`LLM_TEMPERATURE` 调采样温度（默认 0，见 `config.py` / `env.example`）。
- **换任务 / 输入**：评测用例集在 `airline_env.py` 的 `CASES`（分 `holdout` / `boundary` 两组）；
  驱动优化的人类反馈是 `demo.py` 顶部的 `HUMAN_FEEDBACK`；初始与人工对照 prompt 在 `prompts/` 下——
  改这几处即可把闭环套到你自己的场景。
- **局限**：环境为教学用途的精简模拟，工具返回固定 mock 数据；重点在"人类反馈驱动提示词自动优化"
  这一闭环，而非完整复刻 tau-bench。具体正确率会随模型版本与采样有 ±1 个用例的波动。
