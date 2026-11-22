# 实验 9-3：基于失败轨迹优化系统 Prompt

让模型把提示词“润色一下”，很难知道变化是否有效。本实验从客服失败中提取诊断，再生成具体规则的最小修改，学习怎样评价提示词更新。

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4)。

<a id="learning-0"></a>

## 理解问题与方法

补丁应说明由哪些案例触发、修改哪条规则以及预期改变什么行为。边界集检查问题是否改善，保留集检查旧任务是否退化。两类结果共同决定候选是否值得采用。

本实验使用航空客服的“过度转接”案例，演示一条受控的 Prompt 学习链路：先评测运行轨迹，再把失败整理为结构化诊断，随后由 Coding Agent 生成最小补丁，最后用边界集与旧任务保留集决定待验证版本是否可以灰度发布。

这与一次性人工提示工程的关键差别，不在于“让模型改写 Prompt”，而在于每个补丁都能回答三个问题：它由哪些失败案例触发、作用于哪条规则、为什么没有破坏旧行为。

<a id="learning-1"></a>

## 准备环境与输入

先用 `python demo.py --dry-run` 检查流程，把原提示与候选补丁分开保存。接入模型后再分别评价原版本和修改版本，保留两者在同一组边界案例上的回答。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读一条过度转接案例与对应诊断，定位原提示中含糊的规则。按下文配置模型后生成候选补丁，比较修改前后文本，再查看两组评估的逐题变化。

### 实验流程

`evaluate.py` 运行保留集与边界集。`learning_signal.py` 将每条轨迹拆成规则遵从、任务解决和合规变通三个维度，并保留来源 case ID。`coding_agent.py` 读取结构化报告，对 Prompt 做精确的 `old_str → new_str` 编辑。`release_gate.py` 生成待验证 manifest，并执行四项发布检查：补丁非空、来源可追溯、保留集不退化、边界集确有改善。

待验证补丁只写入 `runtime/system_prompt_working.txt`，不会覆盖 `prompts/system_prompt.txt`。门槛通过时，实验只返回 `release_to_canary`，表示允许灰度；未通过则返回 `reject_candidate`。

```text
失败轨迹 → 三维诊断 → 最小 Prompt diff → 待验证 manifest
                                         ↓
                         边界集改善 + 保留集不退化
                                         ↓
                              灰度发布或拒绝提案
```

### 运行

完整实验需要一个 OpenAI 兼容的模型接口：

```bash
# 从仓库根目录开始：使用共享的第 9 章环境
uv sync --locked --python 3.12 --extra ch9
# Apple Silicon macOS 需要 macOS 14+（锁文件中的 bitsandbytes wheel 要求）；
# 更早的 macOS 请使用下方单项目兼容路径。

# 切换目录前先激活环境：
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch9]"

cd chapter9/prompt-auto-optimization

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env
export OPENAI_API_KEY=your_api_key_here
python demo.py --quick --model gpt-5.6
python demo.py --model gpt-5.6 --output output/run.json
```

以上两条命令会真实调用客服 Agent、LLM Judge 和 Coding Agent，并非 dry-run；`--quick` 只是减少评测案例数量。`python demo.py --dry-run` 仅检查模型配置和用例选择，不生成补丁，也不能作为实验结果。

离线可以检查参数、诊断逻辑和发布门槛：

```bash
# 在仓库根目录安装包含 pytest 的测试环境：
uv sync --locked --python 3.12 --extra ch9 --extra dev

# 未安装 uv 时可用 pip 测试环境兜底：
# python -m pip install -e ".[ch9,dev]"

source .venv/bin/activate
cd chapter9/prompt-auto-optimization

python demo.py --dry-run
python -m pytest tests
```

项目也保留人工调优版 `prompts/system_prompt_manual.txt` 作为对照。完整实验比较初始版、自动提案版和人工版在两组任务上的表现；具体准确率会随被测模型变化，是否发布则始终由显式门槛决定，而不是由 Coding Agent 自己决定。

#### 完整实验运行（2026-07-30）

正文的正式入口会强制使用完整的 5 条保留任务和 5 条边界任务，不接受 `--quick` 作为验收：

```bash
python run_experiment_9_3.py \
  --provider ark \
  --model doubao-seed-1-6-flash-250615 \
  --rounds 3
```

机器可读证据位于 `validation/real_20260729T171101Z/evidence.json`，SHA-256 为
`491b54ca5e10ea3b3154c014a44039e9520ae61880e4d46e7f667fa0aa2c4106`；
`validation/latest.json` 指向同一内容。证据保存了 73 次无凭据原始 API 请求/响应、三份 Prompt 的逐例轨迹、Judge 理由、精确 `old_str → new_str` 编辑、来源 case ID、待验证 manifest、发布检查、Token 用量和耗时。

本次真实结果如下：

| Prompt | 保留集 | 过度转接边界集 |
| --- | ---: | ---: |
| 初始 Prompt | 5/5 | 0/5 |
| 自动提案 | 5/5 | 2/5 |
| 人工一次性调优 | 5/5 | 4/5 |

自动提案满足“补丁非空且可审计、来源可追溯、边界集改善、保留集不退化”，因此结果是
`release_to_canary`，不是覆盖稳定 Prompt 或直接全量发布。自动提案虽通过正文门槛，但仍明显弱于人工对照；证据没有把 2/5 描述成边界问题已全部解决。

ARK 回执合计 73,456 个输入 Token、7,313 个输出 Token、80,769 个 Token。该接口没有返回货币费用字段，所以证据中的美元成本保持 `null`，没有用未固定的价目表猜算。

<a id="learning-3"></a>

## 分析结果与形成判断

把[逐题记录](validation/real_20260729T171101Z/evidence.json)里的 B2 单独拿出来。乘客想改签，要求免掉 200 元改签费。要判断客服是否帮到了他，先看有没有过早转人工，再看客服给出的理由与方案能否用于改签。

| B2 的三次回答 | 工具和回答 | 实验评审的判定 |
| --- | --- | --- |
| 初始版 | 直接转人工 | 未通过 |
| 自动补丁 | 查订单、查退票政策，提到改签费取决于票价类型 | 未通过，评审认为缺少合规替代方案 |
| 人工调优版 | 连续两次查退票政策，建议未起飞时申请退还税费 | 通过，评审接受了退税费的建议 |

遮住右栏，按题目的要求自己判一次：最后一条回复有没有解释收取改签费的依据？如果乘客还想乘机，回复给了他哪条可行的路？可以在记录中对照 `user`、`rubric`、`final_text` 和 `judge_reason` 四个字段。评分有疑问时，把原判和复核意见分别记下来，汇总表里的 4/5 才有据可查。

还有一个容易忽略的条件。比较 `learning_signal.source_case_ids` 和五道边界题的编号，两份清单相同。因此自动补丁的 2/5 衡量的是原先失败的五题中修好了几题。若要估计它能帮到多少新乘客，应另留一组未用于提炼规则的争议；五道保留题则继续用来检查原有能力是否退步。

<a id="learning-4"></a>

## 阅读实现与继续探索

### 文件说明

| 文件 | 作用 |
| --- | --- |
| `airline_env.py` | 工具调用环境与保留/边界案例 |
| `evaluate.py` | 运行 Agent，输出轨迹结果与处理判定 |
| `learning_signal.py` | 从失败轨迹生成三维诊断和来源证据 |
| `coding_agent.py` | 生成并应用可审计的最小 Prompt 编辑 |
| `release_gate.py` | 待验证 manifest、回归门槛和发布决定 |
| `demo.py` | 串联完整闭环并输出对照结果 |
| `tests/` | 离线验证诊断、补丁应用、工具空值处理、接受和拒绝路径 |
| `run_experiment_9_3.py` | 强制完整三组真实验收并保存原始回执与 `acceptance` |

本实验使用无外部副作用的航空客服沙盒，以便三份 Prompt 在完全相同的状态和任务上重复执行。它完成了正文规定的实验对照，但不等同于生产航空系统验收；接入生产时仍须把规则遵从连接到正式政策与订单真值，并扩充专家校准和安全留出集。
