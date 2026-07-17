# 实验 4-5：带并行执行和打断能力的异步 Agent（★★★）

本目录是《深入理解 AI Agent》实验 4-5 的配套可运行代码，实现了设计文档
[`agent_framework_design.md`](./agent_framework_design.md) 中描述的事件驱动异步 Agent 框架（Flux）的核心部分。

在 4-4 的简单事件队列之上，本实验进入异步 Agent 的深水区，聚焦四件事：
**异步工具执行、事件队列与批量处理、打断机制、并行工具的取消与状态查询**。
Agent 需要同时管理多个并发任务，处理打断与恢复，并根据实时状态动态决策。

Agent 的决策由真实 LLM（默认 OpenAI `gpt-4o-mini`，function calling）完成；
长任务用**模拟的异步"终端命令"**（带进度输出）实现，绝不真跑危险命令。

---

## 一、架构

对应设计文档第 5 节的事件处理循环，全部基于 `asyncio` 单线程实现：

```
                       ┌──────────────┐
   用户消息 / 打断  ──▶ │    inbox     │  所有进来的原始事件
   异步任务完成通知 ──▶ │  (asyncio.Q) │
                       └──────┬───────┘
                              │
                   ┌──────────▼───────────┐   判定紧急度 classify_urgency()
                   │     _dispatcher      │──▶ 打断 / 立即处理 / 排队
                   └──────────┬───────────┘
             ┌────────────────┼───────────────────┐
   INTERRUPT │        IMMEDIATE│           DEFERRED│
   取消当前turn+异步工具    直接入 work        进 pending 缓冲，
   并留痕                                     异步结果到达时批量追加
                   ┌──────────▼───────────┐
                   │        work          │  待处理的事件批次
                   └──────────┬───────────┘
                   ┌──────────▼───────────┐
                   │       _worker        │  逐批：追加到轨迹 -> run_llm_turn()
                   │   turn_task 可被取消  │  （打断时 cancel 掉这个子任务）
                   └──────────────────────┘

  TaskManager：管理模拟异步终端任务（start / query / cancel / cancel_all）
               任务自然完成 -> 以"新事件"(async.result) 注入 inbox
```

代码文件：

| 文件 | 作用 |
|------|------|
| `events.py`  | 事件模型 `Event`、事件类型、以及**紧急度判定** `classify_urgency()` |
| `tasks.py`   | 模拟异步"终端命令"与 `TaskManager`（进度推进、按 ID 取消/查询） |
| `runtime.py` | `AgentRuntime`：事件循环、两种处理机制、LLM function calling、工具执行 |
| `demo.py`    | 四个验证场景的演示脚本 |

### 两种事件处理机制（设计文档 5.1）

- **取消式处理（Cancellation-Based）**：紧急事件（用户"取消/停止"）到达时，
  立即取消正在进行的 LLM turn，并取消所有后台异步工具，把打断事件与取消回执写入轨迹。
- **排队处理（Queued）**：非紧急事件（补充性指令）先进入 `pending` 缓冲，不打断正在进行的工作；
  当某个异步工具完成、产生 `async.result` 事件时，一次性把 `pending` 里的事件批量追加到轨迹，再触发一次 LLM。

紧急度判定规则（简单可解释）：

1. 含打断关键词（取消/停止/stop…）→ `INTERRUPT`（取消式处理）
2. 是一个提问（带问号或疑问词，如"现在几点了？"）→ `IMMEDIATE`（立即回应，但**不**打断后台任务）
3. 其它补充性指令（如"用日语回复"）→ `DEFERRED`（排队，批量处理）

### 异步工具

`run_terminal_command` 是**异步**工具：调用后立刻返回 `task_id` 占位符（不阻塞），
命令在后台按固定速度推进进度；真正完成后，其结果作为一条**新事件**（`async.result`）注入对话。
另有 `query_task` / `cancel_task` 按 ID 查询进度与取消，`get_current_time` 用于即时提问。

**时间轴加速**：为便于复现，1 个"模拟秒"默认映射为 `0.4` 真实秒（`FLUX_TICK_REAL` 可调）。
速度差 **3% / 2% / 1% 每（模拟）秒** 与 **是否过 50%** 的判定逻辑完全保留。

---

## 二、运行

```bash
cd chapter4/async-agent
pip install -r requirements.txt
cp env.example .env        # 填入 OPENAI_API_KEY

python demo.py             # 依次运行全部四个场景
python demo.py --scenario 1   # 只跑场景 1
python demo.py --scenario 2   # 只跑场景 2
python demo.py --scenario 3   # 只跑场景 3
python demo.py --scenario 4   # 只跑场景 4
```

默认用 OpenAI `gpt-4o-mini`。也可切换服务商（OpenAI 兼容接口）：

```bash
# Moonshot
LLM_PROVIDER=moonshot python demo.py --scenario 1
# 火山方舟 ARK（LLM_MODEL 填推理接入点 ID）
LLM_PROVIDER=ark LLM_MODEL=ep-xxxx python demo.py --scenario 1
```

日志中不同来源用颜色区分：`USER`（用户）、`AGENT`（Agent 回复）、`TOOL`（工具调用）、
`TASK`（后台异步任务）、`TRAJ`（轨迹留痕）、`SYSTEM`（框架事件）。

---

## 三、四个验证场景

### 场景 1：异步工具执行
Agent 执行一个长终端命令，期间用户插入提问"现在几点了？"。
因为长命令是异步的、不阻塞，Agent 立即用 `get_current_time` 回应时间，
等后台任务完成后再把分析结论呈现出来。

### 场景 2：事件队列与批量处理
Agent 执行长任务期间，用户连续发"记得用日语回复""整理成网页"。
这两条是非紧急指令，先进入排队缓冲；任务完成时，框架把它们**一次性批量追加**到轨迹，
Agent 再综合所有指令，输出日语的 HTML 结果。

### 场景 3：打断机制
Agent 执行长任务，用户发"取消"。框架立即取消当前执行流并取消后台异步工具，
在轨迹中记录打断事件（`user.interrupt`）和取消回执（`system.note`，含被取消的 task_id）。

### 场景 4：并行工具的取消与状态查询
用户要求"同时运行这三个脚本，哪个先完成就查其余进度，未过 50% 就取消"。
三个脚本速度分别为 3% / 2% / 1% 每秒。Agent 同时启动三个异步任务；
最快的先完成后，Agent 查询另外两个（约 66% 与 33%），取消未过 50% 的那个，
其余完成后整合出报告。

---

## 四、真实运行输出（关键片段）

> 以下均为真实调用 `gpt-4o-mini` 的输出节选（时间戳为真实秒）。

**场景 1（异步执行 + 即时提问）**
```
[ 2.25s] TASK  | 启动异步任务 T1: `python analyze_logs.py` (速度 4%/模拟秒)
[ 3.34s] AGENT | 任务已在后台启动。请稍等，待任务完成后我会给您分析结论。
[ 6.29s] AGENT | 当前时间是 2026-07-17 22:07:14。        ← 任务仍在跑，先即时回应
[ 8.02s] TRAJ  | + async.result  异步完成 T1              ← 真实结果作为新事件注入
[11.03s] AGENT | 日志分析完成，结果如下：...             ← 再呈现分析
```

**场景 2（批量处理）**
```
[7.78s] SYSTEM | 异步结果到达，批量处理 2 条积压的非紧急事件
[7.78s] TRAJ   | + async.result   异步完成 T1
[7.78s] TRAJ   | + user.input     记得最后用日语回复
[7.78s] TRAJ   | + user.input     把结果整理成一个网页(HTML)
...
AGENT | <html>...<h1>日志分析结果</h1>... 結果は成功に生成されました。
```

**场景 3（打断）**
```
[4.00s] USER   | (interrupt) 取消
[4.00s] TASK   | T1 已被取消 🛑（进度停在 32%）
[4.00s] TRAJ   | + user.interrupt  用户打断：取消
[4.00s] TRAJ   | + system.note     打断回执，取消任务 ['T1']
[4.81s] AGENT  | 已取消后台任务。
```

**场景 4（并行 + 状态查询 + 按 50% 阈值取消 + 整合报告）**
```
[ 3.46s] TASK | 启动异步任务 T1: `python analyze_fast.py` (速度 3%/模拟秒)
[ 3.46s] TASK | 启动异步任务 T2: `python analyze_mid.py`  (速度 2%/模拟秒)
[ 3.46s] TASK | 启动异步任务 T3: `python analyze_slow.py` (速度 1%/模拟秒)
[17.09s] TASK | T1 完成 ✅                               ← 最快脚本先完成
[19.81s] TOOL | query_task(T2) -> running 80%           ← 查询其余两个进度
[19.81s] TOOL | query_task(T3) -> running 40%
[20.99s] TOOL | cancel_task(T3) -> 已取消 (进度 43%)     ← 未过 50%，取消
[23.50s] TASK | T2 完成 ✅
AGENT | 现在所有分析脚本的结果已完成，整合报告如下：### 分析报告 ...
```

---

## 五、注意事项

- **需要联网并配置有效的 API key**（`OPENAI_API_KEY`，或切换到 `MOONSHOT_API_KEY` / `ARK_API_KEY`）。
- LLM 决策由真实模型产生，输出措辞每次可能略有不同；四个场景的**行为逻辑**是稳定可复现的。
  若遇到 OpenAI 偶发的高延迟，重跑即可。
- 时间轴已加速；把 `FLUX_TICK_REAL` 调大可让演示更接近书中"几十秒"的真实节奏，
  调小则更快（过小可能让场景 4 的"未过 50% 就取消"来不及判定）。
- 所有"终端命令"均为模拟，不会在你的机器上真实执行任何命令。
