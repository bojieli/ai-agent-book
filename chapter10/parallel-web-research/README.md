# 并行收集资料时怎样保持证据一致

查阅多个来源可以并行进行，但最后仍需要判断它们是否描述同一个对象。本实验让多个浏览器工作者各自读取来源，再把有出处的结果交给管理者整理。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

独立浏览器上下文减少工作者互相影响，任务标识与消息总线帮助管理者追踪进度。并行减少等待，但不会自动解决同名对象、冲突资料或来源质量问题。

本实现不再使用“可控字符串 + 模拟延迟”。每个同构子 Agent 都拥有独立 Playwright Chromium context，访问真实大学网站、读取实际渲染内容，再由真实 LLM 做证据约束抽取。Manager 维护状态表、错误隔离、超时、加锁单次结算、级联终止、ack 与资源关闭审计；默认还会在同一批网站上实跑串行基线。

### 让多个检索任务并行，同时维护唯一结果

Manager 为每个真实大学 URL 启动一个同构 worker；每个 worker 拥有独立的 Playwright Chromium context，读取渲染文本，再让真实模型抽取有证据支持的教师信息。状态通过带时间戳的异步消息总线回传。

一个网站超时或结构不同，不应停止其他 worker。第一个 `target_found` 必须在 `asyncio.Lock` 保护下结算，只允许一次 terminate 广播；较晚返回的命中仍要记录。导航和抽取都与停止事件竞争，未胜出的 worker 在安全位置取消、确认并关闭 context。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读站点配置和目标名称，明确每个工作者负责的来源。按下文准备浏览器与模型后，从少量来源开始，跟踪启动、返回、追问与终止消息，再检查汇总是否保留出处。

### 先选少量网站，再比较同一组任务的调度方式

安装共享环境和 Chromium 后，先使用自定义目标与 `sites.example.json`，确认每个 worker 能返回可核对的来源。默认演示访问十个 Stanford 页面，并真实运行串行基线；完整记录入口还包含四 worker 的终止传播检查。

```bash
# From the repository root: use the shared Chapter 10 environment
uv sync --locked --python 3.12 --extra ch10

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch10]"

cd chapter10/parallel-web-research

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

playwright install chromium
cp env.example .env                 # configure one real text-model endpoint
python demo.py                       # 10 Stanford pages + real serial comparison
```

```bash
python run_official_experiment.py --run-id exp10-4-real-receipts-YYYYMMDD-vN
```

```bash
python demo.py --target 'Professor Name' --sites-json sites.example.json --agents 3
```

`cascade-stress.example.json` 使用同一个真实目标页面的不同查询 URL，以便观察几乎同时命中时的竞争。它是并发机制检查材料，不是多学校研究的数据集。

<a id="learning-3"></a>

## 分析结果与形成判断

某个工作者失败时，汇总应说明缺口，而不是让其他结果假装覆盖全部来源。还要比较协调开销与实际节省的时间。

### 将加速、终止与资源关闭一起核对

串行与并行必须访问同一批网站、使用同一抽取函数，才适合比较墙钟耗时。2026-07-29 的记录为并行 18.542 秒、串行 58.264 秒，约 3.142 倍；后续保留完整来源的运行为 1.872 倍。两者条件与记录时间不同，应分别解释，不能只选更高的数字。

完整运行还核对了 20 个正常比较 context 和 4 个级联测试 context 的关闭、一次终止广播、三个未胜出 worker 的确认，以及 24 份浏览器观察、3 份 ARK 响应和 114 个总线事件。阅读这些文件可以判断加速是否伴随任务遗漏或资源泄漏。

### 检查自己的解释

两个来源对同一人的职位给出不同信息，管理者应怎样利用日期和来源解释差异？

## English

# Experiment 10-4 · Parallel research with real browser sessions

This implementation uses no simulated sources, canned content, or artificial source latency. The Manager dynamically launches one homogeneous worker per real university URL. Every worker owns an isolated Playwright Chromium browser context, navigates the live page, reads rendered text, and uses a real configured LLM endpoint for evidence-constrained profile extraction.

Implemented requirements:

- Dynamic N-way launch with target URL, teacher name, and routed task ID.
- Push status updates over a timestamped asynchronous message bus.
- Per-site timeout/error isolation; an inaccessible or structurally different site does not stop peers.
- First `target_found` is settled under an `asyncio.Lock`; exactly one terminate broadcast is allowed and late hits are recorded.
- Navigation and LLM extraction race against the terminate event. Losing workers cancel at a safe point, acknowledge, and close their browser context.
- Context creation/closure counters make leaked browser sessions an explicit failing audit.
- Serial and parallel paths visit the same live sites and use the same extraction function; wall-clock time and speedup are measured, not estimated.

## Code map

- **Run first:** python demo.py --target "Professor Name" --sites-json sites.example.json --agents 3.
- **Start here:** agents.py::search_one and the Manager run path in run_official_experiment.py.
- **Core behavior:** worker navigation/extraction, async message bus, first-target settlement and cancellation.
- **State / protocol:** task IDs, status/result/terminate events, worker registry and manifest.
- **Verifier:** evidence-constrained extraction, acceptance gates, lock-protected single winner, acknowledgement count and browser-context closure.
- **Experiment variable:** site count, serial versus parallel scheduling and cascade timing.
- **Skip on first pass:** provider request serialization, HTML fixtures and report formatting.

## Run

```bash
# From the repository root: use the shared Chapter 10 environment
uv sync --locked --python 3.12 --extra ch10

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch10]"

cd chapter10/parallel-web-research

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

playwright install chromium
cp env.example .env                 # configure one real text-model endpoint
python demo.py                       # 10 Stanford pages + real serial comparison
```

For the provenance-complete acceptance campaign (the default comparison plus
the four-worker live cascade in one run):

```bash
python run_official_experiment.py --run-id exp10-4-real-receipts-YYYYMMDD-vN
```

This runner stores full rendered browser observations, credential-free raw SDK
request/response bodies with provider response IDs and usage, the message-bus
event stream, exact runtime source hashes, artifact hashes, and acceptance gates.

Use your own university school/directory list:

```bash
python demo.py --target 'Professor Name' --sites-json sites.example.json --agents 3
```

`cascade-stress.example.json` repeats a real target-bearing Stanford profile under distinct query URLs solely to make near-simultaneous live hits and cancellation observable. It is a real-browser stress supplement, not the multi-school research dataset.

## Recorded real integration evidence

On 2026-07-29, the default ten-page Stanford run found Andrew Ng on the live Stanford HAI page using ARK extraction. Parallel wall time was 18.542 s; serial time was 58.264 s, a measured 3.142× speedup. All 10 parallel and 10 serial browser contexts closed. The live cascade stress run produced one winner, one terminate broadcast, three losing-worker acknowledgements, and 4/4 closed contexts.

The current provenance-complete campaign is
[`validation/runs/exp10-4-real-receipts-20260730-v2/manifest.json`](validation/runs/exp10-4-real-receipts-20260730-v2/manifest.json).
All 12 acceptance gates passed: the ten-site parallel and serial paths both
found the target and closed all 20 contexts; the measured speedup was 1.872×;
the cascade produced one broadcast, three loser acknowledgements, and 4/4
closed contexts. The run retains 24 full browser observations, three raw ARK
responses with unique response IDs and usage, and 114 bus events. Seven runtime
source/input hashes and all four artifact hashes recompute exactly, and the
credential scan found zero hits.

The earlier sanitized summary-only records remain at
[`validation/real_parallel_serial_2026-07-29.json`](validation/real_parallel_serial_2026-07-29.json)
and [`validation/real_cascade_2026-07-29.json`](validation/real_cascade_2026-07-29.json)
for historical comparison; they are not the current provenance anchor.

---
