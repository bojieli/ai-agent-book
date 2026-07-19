# 实验 4-5：带并行执行和打断能力的异步 Agent（★★★）

本目录是《深入理解 AI Agent》实验 4-5 的配套可运行代码，实现了设计文档
[`agent_framework_design.md`](./agent_framework_design.md) 中描述的事件驱动异步 Agent 框架（Flux）的核心部分。

在 4-4 的简单事件队列之上，本实验进入异步 Agent 的深水区，聚焦四件事：
**异步工具执行、事件队列与批量处理、打断机制、并行工具的取消与状态查询**。
Agent 需要同时管理多个并发任务，处理打断与恢复，并根据实时状态动态决策。

本目录提供两条使用路径：

- **离线演示（推荐先跑，零依赖、无需 API key）**：把三项核心异步能力单独拎出来、
  用可测量的方式演示——**并行 vs 串行的墙钟时间对比、打断/取消后恢复、状态检查点持久化与恢复**。
  这条路径不联网、不调用 LLM，甚至不需要安装 `openai`，`python demo.py` 即可直接运行。
- **LLM 场景（还原书中四个验证场景）**：Agent 的决策由真实 LLM（默认 OpenAI `gpt-5.6-luna`，
  function calling）完成，需要配置 API key。

两条路径共用同一套异步运行时；长任务都用**模拟的异步"终端命令"**（带进度输出）实现，绝不真跑危险命令。

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
| `events.py`  | 事件模型 `Event`（含检查点序列化 `to_dict`/`from_dict`）、事件类型、**紧急度判定** `classify_urgency()` |
| `tasks.py`   | 模拟异步"终端命令"与 `TaskManager`（进度推进、按 ID 取消/查询、状态 `snapshot`/`restore`） |
| `runtime.py` | `AgentRuntime`：事件循环、两种处理机制、LLM function calling、工具执行、检查点 `save_checkpoint`/`load_checkpoint` |
| `async_demos.py` | 三个**离线演示**（无需 API key）：并行墙钟对比、打断/恢复、状态检查点 |
| `demo.py`    | 统一命令行入口（argparse 子命令）：离线演示 + 四个 LLM 验证场景 |

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

命令行入口是 `demo.py`，用 `argparse` 子命令组织，`python demo.py --help` 查看全部用法。

### 离线演示（无需 API key，开箱即用）

```bash
cd chapter4/async-agent

python demo.py              # 默认：依次运行下面三个离线演示
python demo.py offline      # 同上：显式地依次运行三个离线演示
python demo.py parallel     # 能力一：并行 vs 串行工具调用的墙钟时间对比（打印加速比）
python demo.py interrupt    # 能力二：长任务运行中被打断/取消，随后系统恢复
python demo.py state        # 能力三：状态检查点持久化 + 跨会话恢复并校验
```

这三个演示不联网、不调用 LLM，连 `openai` 都无需安装——用纯 `asyncio` 直接测量并行加速、
打断后的状态冻结、以及检查点的落盘与还原。

### LLM 验证场景（还原书中四个场景，需要 API key）

```bash
pip install -r requirements.txt
cp env.example .env         # 填入 OPENAI_API_KEY

python demo.py scenarios                # 依次运行全部四个场景
python demo.py scenarios --scenario 1   # 只跑场景 1（异步执行 + 即时提问）
python demo.py scenarios --scenario 3   # 只跑场景 3（打断机制）
```

默认用 OpenAI `gpt-5.6-luna`。也可切换服务商（OpenAI 兼容接口）：

```bash
# Moonshot（默认模型为当前的推理模型 kimi-k3）
LLM_PROVIDER=moonshot python demo.py scenarios --scenario 1
# 火山方舟 ARK（LLM_MODEL 填推理接入点 ID）
LLM_PROVIDER=ark LLM_MODEL=ep-xxxx python demo.py scenarios --scenario 1
```

> **OpenRouter 通用兜底**：未配置 `OPENAI_API_KEY`（且未用 moonshot/ark provider）时，
> 只要设置了 `OPENROUTER_API_KEY`，`demo.py` 会自动改走 OpenRouter，并把模型名映射为
> `provider/model` 形式（`gpt-*` → `openai/…`、`claude-*` → `anthropic/claude-opus-4.8`、
> 含 `/` 的原样透传）。也可显式 `LLM_PROVIDER=openrouter`。例如：
> `OPENROUTER_API_KEY=sk-or-xxx LLM_MODEL=openai/gpt-5.6-luna python demo.py scenarios --scenario 1`

> Moonshot 默认走**推理模型 `kimi-k3`**（旧的 `kimi-k2-*-preview` 与 `moonshot-v1-*` 已过时/停用）。
> 推理模型要求 `temperature=1` 且 `max_tokens>=2048`，`demo.py` 会按模型自动套用这套采样参数，无需手动配置。

> 兼容旧用法：`python demo.py --scenario N` 会自动等价为 `scenarios --scenario N`。

日志中不同来源用颜色区分：`USER`（用户）、`AGENT`（Agent 回复）、`TOOL`（工具调用）、
`TASK`（后台异步任务）、`TRAJ`（轨迹留痕）、`STATE`（状态检查点）、`SYSTEM`（框架事件）。

---

## 三、离线演示的三项能力（真实测量输出）

以下三段均为**真实运行**输出节选（无需 API key），演示异步到底带来了什么。

### 能力一：并行 vs 串行工具调用（`python demo.py parallel`）

四个相互独立的只读感知工具（读文件 / 搜索 / 查库 / 向量检索），串行逐个 `await`
与并行 `asyncio.gather` 的墙钟时间对比：

```
  ── 结果对比 ─────────────────────────────────────────────
  串行总耗时（Σ 各工具）                  4.51s
  并行总耗时（gather）                 1.50s
  并行理论下界（最慢单个）                  1.50s
  加速比 = 串行 / 并行                 3.00x
  ─────────────────────────────────────────────────────────
```

墙钟时间由「各工具求和」降到「取最大单个」——这正是书中「只读感知工具天然适合并行」的量化落点。

### 能力二：打断 / 取消 / 恢复（`python demo.py interrupt`）

三个并行后台任务运行中，用户先即时提问（不阻塞任务），随后发出「取消」打断：

```
[  1.00s] USER   | （即时提问）现在几点了？
[  1.00s] AGENT  | 现在 00:14:26。三个后台任务仍在并行推进，未被这次提问阻塞。
[  2.00s] USER   | （打断）取消
[  2.00s] TASK   | T1 已被取消 🛑（进度停在 39%）
[  2.00s] TASK   | T2 已被取消 🛑（进度停在 26%）
[  2.00s] TASK   | T3 已被取消 🛑（进度停在 13%）

  ── 打断后各任务状态（进度冻结在中途）───────────────────
  task_id 命令                        状态              进度
  T1      python analyze_fast.py    cancelled      39%
  T2      python analyze_mid.py     cancelled      26%
  T3      python analyze_slow.py    cancelled      13%
  ─────────────────────────────────────────────────────────
[  2.05s] SYSTEM | 打断处理完毕，系统恢复空闲，可继续接受新任务……
[  5.52s] TASK   | T4 完成 ✅
[  5.52s] AGENT  | 已从打断中恢复，新任务 T4 正常完成：……
```

打断只冻结被取消任务的进度，运行时本身无损，随后能立即接受并跑完新任务。

### 能力三：状态检查点持久化与恢复（`python demo.py state`）

会话 A 产生一段轨迹 + 两个运行中的后台任务，落盘为 `checkpoints/agent_state.json`；
会话 B 用全新运行时从磁盘恢复并校验：

```
  ── 恢复校验 ─────────────────────────────────────────────
  轨迹事件数     保存前 3  ->  恢复后 3  [一致 ✓]
  可重建 LLM 上下文消息 4 条（system + 轨迹回放）
  task_id 命令                             保存前进度  恢复后状态           进度
  T1      python analyze_fast.py           21%  suspended      21%
  T2      python analyze_slow.py            7%  suspended       7%
  ─────────────────────────────────────────────────────────
```

轨迹与任务进度完整落盘并跨会话还原；运行中的任务恢复后标记为 `suspended`，保留最后已知进度，
供上层决定「重跑」还是「按进度续跑」——这就是异步任务的状态管理。

---

## 四、四个 LLM 验证场景

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

## 五、LLM 场景真实运行输出（关键片段）

> 以下均为真实调用 `gpt-5.6-luna`（OpenAI 兼容接口）的输出节选（时间戳为真实秒，需配置 API key 复现）。

**场景 1（异步执行 + 即时提问）**
```
[ 3.97s] AGENT | 任务已在后台启动（task_id：T1）。完成后我会根据日志分析结果给出结论。
[ 4.96s] TASK  | T1 `python analyze_logs.py` 进度 22%      ← 任务仍在后台跑
[ 5.19s] TOOL  | get_current_time -> 2026-07-18 13:43:30  ← 即时提问先回应
[ 6.91s] AGENT | 现在是 2026 年 7 月 18 日 13:43:30。
[12.19s] TRAJ  | + async.result  异步完成 T1               ← 真实结果作为新事件注入
[16.67s] AGENT | 日志分析已完成，结论如下：共扫描 12,840 条记录…  ← 再呈现分析
```

**场景 2（批量处理）**
```
[ 1.50s] SYSTEM | 事件进入排队缓冲（当前积压 1 条）
[ 1.90s] SYSTEM | 事件进入排队缓冲（当前积压 2 条）
[12.05s] TASK   | T1 完成 ✅
[12.05s] SYSTEM | 异步结果到达，批量处理 2 条积压的非紧急事件
[12.06s] TRAJ   | + async.result   异步完成 T1
[12.06s] TRAJ   | + user.input     记得最后用日语回复
[12.06s] TRAJ   | + user.input     把结果整理成一个网页(HTML)
...
[22.38s] AGENT  | <!DOCTYPE html>…<h2>分析結論</h2>… （批量指令一次性满足：日语 + HTML）
```

**场景 3（打断）**
```
[ 2.40s] TASK   | 启动异步任务 T1: `python analyze_logs.py` (速度 4%/模拟秒)
[ 4.00s] USER   | (interrupt) 取消
[ 4.00s] TASK   | T1 已被取消 🛑（进度停在 14%）
[ 4.00s] TRAJ   | + user.interrupt  用户打断：取消
[ 4.00s] TRAJ   | + system.note     打断回执，取消任务 ['T1']
[ 5.04s] AGENT  | 已停止后台任务 T1。
```

**场景 4（并行 + 状态查询 + 按 50% 阈值取消 + 整合报告）**
```
[ 2.82s] TASK | 启动异步任务 T1: `python analyze_fast.py` (速度 3%/模拟秒)
[ 2.82s] TASK | 启动异步任务 T2: `python analyze_mid.py`  (速度 2%/模拟秒)
[ 2.82s] TASK | 启动异步任务 T3: `python analyze_slow.py` (速度 1%/模拟秒)
[16.47s] TASK | T1 完成 ✅                               ← 最快脚本先完成
[19.84s] TOOL | query_task(T2) -> running 84%           ← 查询其余两个进度
[19.84s] TOOL | query_task(T3) -> running 42%
[21.93s] TOOL | cancel_task(T3) -> 已取消 (进度 47%)     ← 未过 50%，取消
[22.89s] TASK | T2 完成 ✅
[26.50s] AGENT | ## 分析汇总报告 … analyze_slow.py：已取消（未超 50%）…
```

---

## 六、注意事项

- **离线演示（`parallel`/`interrupt`/`state`）无需任何 API key、也无需安装 `openai`**，开箱即跑。
- **只有 `scenarios` 子命令需要联网并配置有效的 API key**（`OPENAI_API_KEY`，或切换到
  `MOONSHOT_API_KEY` / `ARK_API_KEY`）。
- LLM 决策由真实模型产生，输出措辞每次可能略有不同；四个场景的**行为逻辑**是稳定可复现的。
  若遇到 OpenAI 偶发的高延迟，重跑即可。
- 时间轴已加速；把 `FLUX_TICK_REAL` 调大可让演示更接近书中"几十秒"的真实节奏，
  调小则更快（过小可能让场景 4 的"未过 50% 就取消"来不及判定）。
- 所有"终端命令"均为模拟，不会在你的机器上真实执行任何命令。
