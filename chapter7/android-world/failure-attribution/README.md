# 从失败轨迹寻找最早失去依据的决策

任务失败的最后一步往往只是后果，真正的问题可能更早就出现了。本实验使用已有 AndroidWorld 日志，学习把可观察事实、原因假设和回归用例连接起来。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

失败归因先还原每轮观察与动作，再寻找最早不被证据支持的决定。环境初始化失败、工具执行错误和模型判断错误应分开。无法从日志区分的原因，应保留不确定性。

### 先找证据，再提出原因

实验 7-6 使用已有 T3A 日志做离线归因，不启动模拟器，也不调用模型 API。输入是 `../t3a_failed.md` 与 `../t3a.md` 中逐轮的 Action、Reason、Summary 和最终验证器判断。

`extract_trajectories.py` 将日志切成带编号的任务记录，`trajectories.json` 保存解析结果，`attribution_records.json` 保存十条结构化归因，`regression_prefixes.json` 保存三个前缀回归任务，`manifest.json` 记录内容哈希与范围。先把事实、推测和无法判断之处分开，再定位最早缺乏依据的决策。

<a id="learning-1"></a>

## 准备环境与输入

先从本地示例开始。依赖安装可能需要联网，但下面标明的离线路径不需要模型 API Key。若随后切换到真实模型，请再完成相应的服务配置。

<a id="learning-2"></a>

## 按照步骤完成实验

先运行解析命令得到逐回合记录，选一条任务从头读到结束。在看到最终判断前先标记可疑步骤，再与已有归因记录比较。最后查看轨迹前缀用例，理解怎样把错误前的状态变成可重复检查。

### 先做一个小规模观察

以下命令从本实验目录执行。先完成前面的环境准备，再观察这条路径的输入和输出。

```bash
python extract_trajectories.py --log ../t3a_failed.md --out tutorial-trajectories.json
```

### 解析之后，先独立标注一条轨迹

从仓库根目录执行下列命令。第一次阅读时先不看既有归因结论：逐轮标出模型实际看到了什么、做了什么，以及下一步是否依赖了尚未证实的事实。然后再与归因记录的 `revised_from_first_pass_step` 和 `revision_note` 比较。

```bash
cd chapter7/android-world/failure-attribution
python extract_trajectories.py --log ../t3a_failed.md --out trajectories.json
```

<a id="learning-3"></a>

## 分析结果与形成判断

模型声明完成而验证器判失败，提示我们不能只搜索日志中的报错关键词。归因还可能随着复核修正，应保留支持每个判断的具体轮次。

### 从总体统计走到具体样本

日志有 53 个任务块，其中 `SimpleSmsReplyMostRecent` 因环境初始化的 `list index out of range` 被跳过，剩下 52 个才是失败轨迹。24 个失败由 Agent 自称完成而结束，28 个耗尽步数；6 个发出了 answer，其中 1 个从未发出完成信号。这说明最终状态与模型语言声明必须分别检查。

十条标注覆盖九个静默失败和一个有可见错误的案例。七个最早错误发生在 assistant 消息，而不是工具调用。第一次到第二次复核有七条最早错误位置前移；第三次又修正了统计与一条错误幅度描述。因此，下面保留完整十条表格和每次修订的说明，而不是把第一次标注当成标准答案。

例如，收据任务在第 17 步写入虚构 CSV，但第 4 步已承认无法读取具体交易仍离开图片；短信任务第 4 步已报告收件人确认没有效果，第 5 步却继续输入正文，晚到第 6–7 步才出现 Not sent。日历下周任务的错误在第 4 步把周日开始的 Oct 22–28 当成周一开始的目标周，而不是之后的最终回答。分析这些例子时，应寻找最早缺少依据的承接关系。

全体 52 个失败中，九个需要当前日期，七个从未取得日期；两次偶然在新建事件页面看到了日期，但也失败了。无可见效果的表述出现 55 次，涉及 18 个任务，后续分别有 18 次重复同类控件、33 次转向其他控件、4 次结束或处于最后一步。换控件本身未必错误，关键是是否在没有重新观察的情况下依赖上一步已经成功。

还需区分观察通道：T3A 读取无障碍树，缺少图像像素，不能直接把读不到图片归因于视觉模型缺少 OCR。`answer` 也不等于 `status: complete`。修复方向应由具体接口和观察决定。

### 检查自己的解释

如果日志不足以判断是页面没有更新还是模型看错，下一次运行应该增加什么观察？

<a id="learning-5"></a>

## 排查问题与查阅资料

### 什么时候应该保留不确定性

十条样本不能代表全部失败类型的比例。`SimpleCalendarAddOneEvent` 仅低置信度，因为日志不能说明验证器拒绝了哪个字段；日期格式问题虽可定位，四个事件时间是否准确仍无法确认；短信失败可能来自未提交收件人，也可能来自模拟器没有短信服务，日志不能区分。

某个任务看到的 `Sun, Oct 15` 不能移植到其他任务，因为环境会按任务实例参数化。相对日期在本条轨迹中不可见时，应记录需要什么额外观察，而不是用另一条轨迹的日期补齐。本文后部保留全部原始表格、逐条修订、三条前缀任务链接和范围说明。

## English

# Experiment 7-6: Failure attribution on AndroidWorld T3A traces / 实验 7-6：AndroidWorld 失败轨迹的失败归因

Companion evidence for *AI Agents in Depth*, Chapter 7 — **实验 7-6 ★★：对 AndroidWorld 失败轨迹做失败归因**.

← [Back to android-world notes](../README.md) · 📖 [Read the chapter](../../../book/chapter7.md)（[EN](../../../book-en/chapter7.md)）

## What this is

An offline attribution pass over the retained T3A run in `chapter7/android-world`.
No emulator and no model API are involved: the only inputs are `../t3a_failed.md`
and `../t3a.md`, which already contain each episode's per-step
`Action`/`Reason`/`Summary` plus the validator's objective verdict.

| File | Role |
| --- | --- |
| [`extract_trajectories.py`](extract_trajectories.py) | Splits the log into per-episode records with numbered steps |
| [`trajectories.json`](trajectories.json) | Parsed output: 53 episodes, 52 with a `Task Failed` verdict |
| [`attribution_records.json`](attribution_records.json) | The 10 structured attribution records |
| [`regression_prefixes.json`](regression_prefixes.json) | Three trajectory-prefix regression tasks cut from the records |
| [`manifest.json`](manifest.json) | Content hashes and the scope boundary of this evidence |

Reproduce the parse with:

```bash
cd chapter7/android-world/failure-attribution
python extract_trajectories.py --log ../t3a_failed.md --out trajectories.json
```

## Population statistics (all 52 failed episodes)

Recomputed directly from the raw log, not from the parsed intermediate:

| Measure | Value |
| --- | ---: |
| Task blocks in `t3a_failed.md` | 53 |
| …of which skipped by the benchmark harness, not Agent failures | 1 |
| Failed episodes | 52 |
| Ended because the Agent declared completion | 24 |
| Ended by exhausting the step budget | 28 |
| Emitted an `answer` action | 6 |
| Emitted an `answer` but never signalled completion | 1 |

**24 of 52 failures are episodes in which the Agent believed it had succeeded.**
That is the population the section calls silent failure: nothing in the trace
reports an error, and only the closing validator disagrees.

One block is not an Agent failure at all: `SimpleSmsReplyMostRecent` was skipped
because the benchmark's own `initialize_task` raised `list index out of range`.
It is worth naming — the chapter's rule that you check the evaluation system
before you touch the Agent has a live instance sitting in this very log.

## The 10 annotated records

Sampled to cover both regimes: 9 silent failures and 1 case that does contain an
observable error. Every quotation is verified against the cited step by the build
script; a mismatch fails the build. The right-hand column records where the first
annotation pass put the first error, before the review described below.

| Task | Steps | First error | Kind | Category | Confidence | 1st pass |
| --- | ---: | ---: | --- | --- | --- | ---: |
| MarkorTranscribeReceipt | 18 | 4 | assistant message | proceeded on known-missing information | high | 17 |
| ExpenseAddMultipleFromGallery | 32 | 8 | assistant message | proceeded on known-missing information | high | — |
| SimpleCalendarNextMeetingWithPerson | 4 | 2 | assistant message | unwarranted inference | high | 3 |
| SportsTrackerActivitiesOnDate | 5 | 3 | assistant message | unwarranted inference | high | 4 |
| SimpleCalendarEventsInNextWeek | 6 | 4 | assistant message | explicit constraint dropped | high | 5 |
| SimpleCalendarEventOnDateAtTime | 6 | 5 | assistant message | wrong information reported to the user | medium | — |
| SimpleCalendarDeleteEventsOnRelativeDay | 3 | 2 | tool call | relative time never grounded | medium | — |
| SimpleSmsSend | 8 | 5 | tool call | proceeded after a self-reported no-effect | medium | 8 |
| SportsTrackerActivitiesCountForWeek | 10 | 3 | tool call | relative time never grounded | medium | 4 |
| SimpleCalendarAddOneEvent | 14 | 13 | assistant message | declared complete without verification | low | 14 |

**7 of the 10 first errors are assistant messages, not tool calls.** Searching
the logs for error keywords would have located none of them.

### Where earlier passes were superficial

The first annotation pass repeatedly recorded the step where the wrong *output*
appears instead of the earliest unwarranted inference — the mirror image of the
mistake the chapter warns against. **Seven of ten first-error steps moved in the
second pass.** A third pass then corrected the second pass in turn: two
population statistics had been computed with loose pattern matching and were
simply wrong, and one record misdescribed the size of the error it had correctly
located. Every change is retained in the records as
`revised_from_first_pass_step` and `revision_note`, because the correction is the
lesson:

- `MarkorTranscribeReceipt` 17 → **4**. Step 17 is where fabricated CSV lands in
  the file, and it announces itself: *"I'll enter sample CSV data."* But step 4
  already says *"I cannot actually read the specific transaction details from the
  receipt image"* — and leaves the gallery anyway, thirteen steps earlier.
- `SimpleSmsSend` 8 → **5**. The first pass asserted that the `Not sent` at steps
  6–7 was an environment fault outside the Agent's control. Nothing in the log
  supports that. Step 4's own summary says the recipient-confirm click left *"the
  screen remained unchanged"* and diagnoses that the field needs focus first;
  step 5 types the message body without repairing it. Whether the send failed
  because the recipient was never committed, or because the emulator has no SMS
  service, is not decidable from the log — so the record now says so instead of
  picking the flattering hypothesis.
- `SimpleCalendarEventsInNextWeek` 5 → **4**. Step 4's summary states in one
  sentence both that the view shows *"week 43 (Oct 22-28)"* and that this is
  *"the requested week starting from Monday Oct 23."* The false reconciliation is
  there, not in the answer that follows it. A third pass also had to fix the
  *size* of the error: the second pass called it a one-day boundary shift, which
  is wrong. Step 4 shows the current week as Oct 15–21, so today falls inside it
  and a Monday-start "next week" can only be Oct 16–22 or Oct 23–29. The answered
  range, Oct 22–28, is a Sunday-start range and is neither.
- `SimpleCalendarNextMeetingWithPerson` 3 → **2**, `SportsTrackerActivitiesOnDate`
  4 → **3**: in both, the answer step is a *second* defect; the first is a summary
  that claims *"appears to be the next meeting"* / *"confirming I have identified
  all activities"* with nothing to support it.
- `SportsTrackerActivitiesCountForWeek` 4 → **3**. The scroll oscillation is a
  symptom, not the cause: with no grounded week boundary the Agent had no
  stopping criterion, so it could only keep scanning.
- `SimpleCalendarAddOneEvent` 14 → **13**, still **low confidence**.

## Two systemic patterns behind the per-episode labels

Counting across all 52 failed episodes, not the sample.

**Relative time is almost never grounded — but the date was there to be had.**
Nine failed episodes have goals that cannot be resolved without knowing the
current date (`this week`, `this Monday`, `tomorrow`, `next week`, `next
meeting`, `in two weeks from today`). **Seven of the nine never obtain it.** The
two that do — `SimpleCalendarAddOneEventTomorrow` and
`SimpleCalendarAddOneEventInTwoWeeks` — get it incidentally, because their
workflow opens the New Event form, which defaults its start date to today and so
displays `Sun, Oct 15` (2023). Neither of them probed for it deliberately, and
both still failed.

That is a sharper diagnosis than "the model cannot handle relative dates". The
environment does expose today's date, but only on one screen. Workflows that go
through search, a list view, or a week view never see it, and the Agent never
navigates anywhere to fetch it. The fix is to put the date in every observation —
a harness change, not a model change.

**The Agent frequently reports that its own action had no visible effect.** The
phrase family *"appears unchanged" / "may not have registered" / "no visible
feedback"* occurs **55 times across 18 of the 52 failed episodes**. What happens
next splits as follows:

| Next step after a self-reported no-effect | Count |
| --- | ---: |
| Retried the same control type | 18 |
| Targeted a different control | 33 |
| Ended the episode (`status` / `answer`) or was the last step | 4 |

Targeting a different control is often a legitimate alternative repair, so this
table is descriptive, not an indictment. The failure mode it makes visible is
narrower: an Agent that records a no-effect and then *depends on that action
having worked* without ever re-reading the state. `SimpleSmsSend` step 5 is the
named instance in this sample — it types the message body after its own step-4
summary says the recipient confirmation did not take.

### Findings worth naming

**Fabrication is announced, not hidden.** In `MarkorTranscribeReceipt` step 17
the Agent writes: *"Since I couldn't extract the actual transaction details from
the receipt.png image through the gallery interface, I'll enter sample CSV
data."* In `ExpenseAddMultipleFromGallery` step 8 it writes: *"I cannot actually
see the content/details of the expenses in the image."* Both then proceed. The
missing capability is not perception but a legal way to stop and report.

**The fabricated values repeat across unrelated tasks.** The receipt task writes
`Coffee, $4.50` and the expense task writes `Coffee $4.50`. Two independent
episodes producing the same invented item and price is evidence that the content
comes from the model's prior, not from a misread of the screen.

**The first error message is not the first error.** In `SimpleSmsSend` the
environment reports `Not sent. Touch to retry.` at steps 6 and 7. That is where
the trace gets loud, and it is neither the first error nor — on this evidence —
established as an environment fault. The first Agent error is step 5, which
proceeds past a self-reported no-effect at step 4. Declaring the task complete
at step 8 while the screen still reads `Not sent` is a further defect.

**A wrong answer can be one field wide.** `SimpleCalendarNextMeetingWithPerson`
navigates and searches perfectly, then answers `October 27 2024 22:15`. The
year is unobserved and contradicts the weekday the Agent itself read: 2023-10-27
is a Friday, 2024-10-27 is a Sunday.

## Disagreements with `t3a_failed_analysis.md`

The existing note in this repository is a useful starting point, not an answer
key. Three of its entries do not survive re-reading:

1. **Image transcription — root cause.** The note records *"the vision model
   lacks OCR."* T3A observes an accessibility tree only; there are no image
   pixels in its observation space, so the model never had the chance to read
   the image. The root cause is a missing observation channel plus the absence
   of an "information unavailable" exit action. The distinction matters: the
   note's version points at swapping models or OCR training, the corrected
   version points at the harness.
2. **Image transcription — step 8 description.** The note says the Agent *"never
   mentions what it saw in the image."* It does: step 8 states plainly that it
   cannot see the content. It knew, and continued anyway — a different and worse
   failure than not knowing.
3. **`SportsTrackerActivitiesCountForWeek` — "confusing" outcome.** The note
   calls it puzzling that the Agent claims completion while the run ends with
   *"Agent did not indicate task is done."* There is no contradiction: the Agent
   emitted an `answer` action at step 10 but never emitted `status: complete`.
   In this harness `answer` is not a completion signal. It is the only failed
   episode in the log that answered without ever signalling completion.

## Trajectory-prefix regression tasks

Three prefixes cut immediately before an assistant-message first error, with
acceptable and forbidden action sets, are in
[`regression_prefixes.json`](regression_prefixes.json).

## Scope and limits

- This is an **annotation pass over an existing retained run**, not a new
  AndroidWorld campaign. It produces no success-rate claim.
- The records are the **third pass**. Seven of ten first-error steps moved
  between the first and second; the third pass corrected two population
  statistics that loose pattern matching had got wrong (relative-time goals were
  9, not 8, and 2 of them do ground the date; the no-effect family occurs 55
  times across 18 episodes, not 53 across 17) and fixed one record that
  misdescribed the magnitude of a correctly located error. Treat a single
  attribution pass — including this one — as a draft.
- The sample is 10 of 52 failed episodes, chosen to span both termination
  regimes. Per-category counts from this sample are not population estimates;
  only the table under "Population statistics" describes all 52.
- `SimpleCalendarAddOneEvent` is retained at **low confidence**: the log alone
  cannot determine which field the validator rejected. Attribution of that
  episode requires replaying the environment, and the record says so rather than
  guessing.
- `SimpleCalendarEventOnDateAtTime` is attributed on the format violation, which
  is verifiable from the log. Whether the four event times it read were accurate
  is not, so the record is medium confidence, not high.
- `SimpleSmsSend` has two competing explanations for the failed send — an
  uncommitted recipient versus an emulator with no SMS service. The log cannot
  separate them; the record names both rather than choosing.
- `Sun, Oct 15` (2023) is observed inside two calendar episodes. It is **not**
  imported into other episodes: AndroidWorld parameterises task instances, so a
  date observed in one episode is not evidence about another. That is why
  `SimpleCalendarDeleteEventsOnRelativeDay` and
  `SportsTrackerActivitiesCountForWeek` stay at medium confidence — within their
  own traces the current date is never visible, so the correct answer cannot be
  derived from the log at all.
