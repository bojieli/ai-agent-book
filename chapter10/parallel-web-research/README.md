# 怎样并行查找教师资料，并在找到后停止搜索

要从十个斯坦福大学页面中找到 Andrew Ng 的资料，一个办法是依次打开页面，找到就停；另一个办法是让十个工作者同时开始。后者可能更快，却多了一个问题：一位工作者找到有出处的资料时，谁来通知另外九位收手，又怎样知道浏览器已经关闭？

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

每位工作者负责一个网址，用独立的 Playwright Chromium 浏览器上下文打开页面。先认清程序什么时候会用到模型：它读取渲染后的文字，忽略大小写查找目标姓名；页面里没有这个名字，就直接报告未找到。只有名字出现时，才把材料交给模型抽取教师信息。因此，即使打开了十个页面，也未必会发出十次模型请求。这个筛选条件也有代价：只写姓名缩写或别名的页面可能被跳过。

### 两位工作者同时报告找到目标，听谁的？

工作者通过带时间戳的消息报告任务进度。Manager 维护各站点的状态，某个站点超时、访问失败，都要单独记录，其余站点可以继续。第一个有效的 `target_found` 到达时，Manager 在 `asyncio.Lock` 保护下登记胜出者，广播一次停止通知。迟到的命中仍会留下记录。接下来还要核对两件事：其余工作者是否确认了通知，各自的浏览器上下文是否已经关闭。正在导航或等待模型返回的工作者也要响应停止事件。

<a id="learning-1"></a>

## 准备环境与输入

把待查的人名和候选网站分开准备，并保留每个网站的原始地址。串行和并行两次都使用同一组来源，否则完成时间的差别也可能来自站点数量或速度。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读站点配置和目标名称，明确每个工作者负责的来源。按下文准备浏览器与模型后，从少量来源开始，跟踪任务分派、命中、停止通知和确认消息，再检查汇总是否保留出处。

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
python demo.py --target 'Andrew Ng' --sites-json sites.example.json --agents 3
```

`cascade-stress.example.json` 使用同一个真实目标页面的不同查询 URL，以便观察几乎同时命中时的竞争。它是并发机制检查材料，不是多学校研究的数据集。

<a id="learning-3"></a>

## 分析结果与形成判断

某个工作者失败时，汇总应说明缺口，而不是让其他结果假装覆盖全部来源。还要比较协调开销与实际节省的时间。

### 将加速、终止与资源关闭一起核对

串行与并行必须访问同一批网站、使用同一抽取函数，才适合比较墙钟耗时。2026-07-29 的记录为并行 18.542 秒、串行 58.264 秒，约 3.142 倍；在[7 月 30 日的完整记录](validation/runs/exp10-4-real-receipts-20260730-v2/evidence.json)中，串行组在第十个页面找到目标，用了 44.971 秒；并行组用了 24.022 秒。两者相除得到 1.872 倍。串行代码每找到一个有效结果就退出。如果把命中页排到第一位，串行组就只访问一页，所以复现时除了保留网址，还要保留它们的顺序。两者条件与记录时间不同，应分别解释，不能只选更高的数字。

完整运行还核对了 20 个正常比较 context 和 4 个级联测试 context 的关闭、一次终止广播、三个未胜出 worker 的确认，以及 24 份浏览器观察、3 份 ARK 响应和 114 个总线事件。阅读这些文件可以判断加速是否伴随任务遗漏或资源泄漏。

### 检查自己的解释

两个来源对同一人的职位给出不同信息，管理者应怎样利用日期和来源解释差异？

## English

# Experiment 10-4 · Parallel research with real browser sessions

This implementation uses no simulated sources, canned content, or artificial source latency. The Manager dynamically launches one homogeneous worker per real university URL. Every worker owns an isolated Playwright Chromium browser context, navigates the live page, reads rendered text, and calls the configured LLM for profile extraction only when the target name occurs in that text (case-insensitive).

Implemented requirements:

- Dynamic N-way launch with target URL, teacher name, and routed task ID.
- Push status updates over a timestamped asynchronous message bus.
- Per-site timeout/error isolation; an inaccessible or structurally different site does not stop peers.
- First `target_found` is settled under an `asyncio.Lock`; exactly one terminate broadcast is allowed and late hits are recorded.
- Navigation and LLM extraction race against the terminate event. Losing workers cancel at a safe point, acknowledge, and close their browser context.
- Context creation/closure counters make leaked browser sessions an explicit failing audit.
- Serial and parallel paths visit the same live sites and use the same extraction function; wall-clock time and speedup are measured, not estimated.

## Code map

- **Run first:** python demo.py --target "Andrew Ng" --sites-json sites.example.json --agents 3.
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
python demo.py --target 'Andrew Ng' --sites-json sites.example.json --agents 3
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
