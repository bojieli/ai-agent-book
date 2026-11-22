# 实验 9-2：从 τ²-bench 失败轨迹提炼转人工与工具使用规则

客服 Agent 可能太早转人工，也可能在需要帮助时反复尝试。本实验从失败轨迹提炼转接和工具使用规则，学习怎样把经验变成可复用指令。

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

假设用户的手机无法上网。客服能查账户、查流量，却不能伸手操作用户的手机。如果失败记录里只写着“调用工具报错”，下一次该换一个工具，还是请用户在手机上操作？提炼规则时，知道谁能操作哪台设备，可能会改变答案。

本实验对应第九章「将经验写成指令」。它检验一个具体问题：**当策略里关于
「何时转人工」只有两句原则性描述时，能否从 Agent 自己的失败轨迹中提炼出
可操作的规则，并让同一个模型在未见过的任务上表现更好。**

### 为什么用 τ²-bench

第七章已经完整解剖过 τ²-bench 的 telecom 领域，读者对它的任务结构、双控
环境和分层判分已经熟悉。本实验直接复用同一套环境，把第七章的「怎么评」
接到第九章的「评完之后怎么改」。

### 模型

| 角色 | 模型 | 说明 |
|---|---|---|
| 被测 Agent | `doubao-seed-1-6-flash-250615` | 故意选弱模型，留出改进空间 |
| 用户模拟器 | `doubao-seed-1-6-250615` | 三臂固定不变，避免混淆 |
| 规则提炼 | `doubao-seed-1-6-250615` | 由模型提炼，不由人手写 |

均通过火山方舟（ARK）的 OpenAI 兼容端点调用。

### 目录

- `derive_rules.py` — 从失败轨迹提炼规则，保存完整请求与回复回执
- `run_arms.sh` — 三臂运行，切换 `main_policy.md` 并记录 sha256，结束后恢复
- `analyze.py` — 通过率、转人工率、误调用用户侧工具次数、空参调用次数
- `policies/baseline_main_policy.md` — 原始策略副本
- `validation/runs/*/` — 提炼回执、生成的规则、进化后的完整策略

<a id="learning-1"></a>

## 准备环境与输入

先按任务 ID 分清哪批案例用来提炼转接规则，哪批留给后续对照。检查一次转接时，同时读客服当时得到的信息和最终处理结果，免得把任何一次转人工都当成失误。

### 数据划分

`telecom_small`（20 条）与 `telecom`（114 条）在上游仓库中**互不相交**，
因此天然构成提炼集与迁移集，划分不是本实验事后挑的。

- **提炼集**：`telecom_small`，20 条。只用来收集失败轨迹、提炼规则。
- **迁移集**：`telecom`，114 条。三个策略臂在这里对照，规则提炼过程从未见过这些任务。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读一条转接失败轨迹，写出触发条件、错误动作和更合适的处理方式。按下文准备 τ²-bench 后，在提炼集生成规则，再在未见任务上比较原策略与修改策略。

### 三个对照臂

| 臂 | 策略 | 说明 |
|---|---|---|
| A | 原始 `main_policy.md` | 转人工只有两句原则描述 |
| B | 原始 + v1 规则 | 提炼器只看到失败摘要与报错文本 |
| C | 原始 + v2 规则 | 提炼器额外看到 Agent 与用户各自的工具清单 |

两次提炼用的是同一个模型和同一批失败摘要。第二次请求在第一份提示的末尾追加了工具清单，还请模型想一想：客服调用了只有用户才能用的工具，该怎样取得所需的信息？第一版规则要求客服遇到“找不到工具”的错误后停止重试；第二版写得更具体，遇到手机端的检查，就引导用户在设备上完成。由于清单和提示一同加入，这次对照只能观察两者合用的效果。[第一版规则](validation/runs/exp9-2-tau2-escalation-v1/derived_rules.md) · [第二版规则](validation/runs/exp9-2-tau2-escalation-v2/derived_rules.md)

### 先用随书轨迹复算

从全书仓库根目录运行下面的命令。只需 Python 3，脚本会逐条读取三种策略留下的客服对话，按任务编号配对比较。

```bash
python3 chapter9/tau2-escalation-experience/analyze.py --archived
```

可以先挑一道从失败变为通过的题。到三份轨迹中搜索同一个任务编号 `[mobile_data_issue]airplane_mode_on|data_mode_off[PERSONA:None]`。这部手机开着飞行模式，同时关闭了移动数据。A 组的客服多次尝试调用用户端的 `check_network_status`，最后转了人工。C 组的客服也误调过手机工具，但接下来用户实际执行了 `toggle_airplane_mode` 和 `toggle_data`，随后在手机上测速，这次通过了评估。在消息的 `role` 字段里找出各次调用的发起者，就能理解为什么同一条通过的轨迹里也会记有误调。[A 组轨迹](validation/runs/armA-baseline.trajectories.json) · [C 组轨迹](validation/runs/armC-evolved-v2.trajectories.json)

### 从头运行实验

```bash
# 1. 安装 τ²-bench（不随本仓库分发）
git clone https://github.com/sierra-research/tau2-bench.git chapter7/tau2-bench
cd chapter7/tau2-bench
# 使用归档轨迹记录的上游版本
git checkout 8d005b0e5b9e4af0bc055886fa7f95fc86d1710e
uv venv --python 3.12 && uv pip install -e .

# 2. 跑提炼集基线，收集失败轨迹
export VOLCENGINE_API_KEY=$ARK_API_KEY
.venv/bin/tau2 run --domain telecom --task-set-name telecom_small \
  --agent-llm volcengine/doubao-seed-1-6-flash-250615 \
  --user-llm volcengine/doubao-seed-1-6-250615 \
  --num-trials 1 --max-concurrency 10 --save-to base-train-v1

# 3. 提炼规则（两个版本）
cd ../../chapter9/tau2-escalation-experience
python3 derive_rules.py --run ../../chapter7/tau2-bench/data/simulations/base-train-v1.json \
  --out-dir validation/runs/exp9-2-tau2-escalation-v1
python3 derive_rules.py --run ../../chapter7/tau2-bench/data/simulations/base-train-v1.json \
  --tool-inventory tool_inventory.txt \
  --out-dir validation/runs/exp9-2-tau2-escalation-v2

# 4. 三臂对照（自动切换策略文件，结束后恢复）
./run_arms.sh

# 5. 汇总
python3 analyze.py
```

<a id="learning-3"></a>

## 分析结果与形成判断

先看同一批 114 道迁移题。原策略 A 通过 14 道，用失败摘要提炼规则的 B 通过 20 道，额外给提炼器看工具清单的 C 通过 22 道。逐题比较 A 和 C，原来通过的 14 道仍然通过，另外 8 道从失败变为通过。这是每种策略每题运行一次的结果，多次运行能否保持这个差距，还要另做验证。[逐题记录](validation/arm_stats.json)

为什么要同时读工具调用记录？原策略下，客服误调用户侧工具 1049 次，C 组降到 163 次。这里数的是调用，同一道题可以出错多次。再看转人工，A 组有 104 道题发生过转接，C 组却有 111 道。可见这次增加的通过数不能简单归功于“少转人工”。要判定某一次转接是否合理，得回到那道题，查客服已经试过哪些操作、剩下的操作该由谁来做。[工具分工](tool_inventory.txt) · [运行记录](validation/runs/)

可以只看第二版新通过的八道题。在本实验目录运行下面的代码，把任务得分与同一条轨迹中的转接调用对上：

```python
import json
from pathlib import Path

def trajectories(name):
    path = Path("validation/runs") / f"{name}.trajectories.json"
    return json.loads(path.read_text(encoding="utf-8"))["simulations"]

baseline = {s["task_id"]: s["reward_info"]["reward"] for s in trajectories("armA-baseline")}
for s in trajectories("armC-evolved-v2"):
    if baseline[s["task_id"]] == 1 or s["reward_info"]["reward"] != 1:
        continue
    transferred = any(
        call["name"] == "transfer_to_human_agents"
        for message in s["messages"]
        for call in message.get("tool_calls") or []
    )
    print("转过人工" if transferred else "未转人工", s["task_id"])
```

八题中，两题没有转人工，六题转过人工。先找任务名含 `airplane_mode_on|unseat_sim_card` 的那题，看用户在哪一步操作了手机。再挑一道转过人工的题，读转接之前的对话。这两类题都拿到了满分；评价客服是否尽到了职责，还得结合任务要求读它的处理过程。

### 检查自己的解释

一条经验在旧环境中成立，但工具能力后来增强了，怎样决定它是否还应继续使用？
