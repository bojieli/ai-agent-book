# Chapter 4 experiment ledger

This ledger separates execution coverage from the manuscript hypothesis and from external credential availability. `official_complete` is true only when every gate named by the manuscript has substantive real evidence. Mechanism tests and credential probes are retained, but never promoted as successful external executions.

| Experiment | Canonical run | Status | `official_complete` | Manifest SHA-256 |
| --- | --- | --- | --- | --- |
| 4-1 | `active-tool-discovery/validation/experiment_4_1/rerun_20260825` | passed | true | `e5a70588804b8bc1a5ba38c18fe7f4537e8284e62f745d8a6e03401833046dae` |
| 4-2 | `perception-tools/validation/experiment_4_2/real_mcp_dashscope_intl_20260730T070000Z` | blocked | false | `f93ee0ad9bd1121ed9e7c9d730bbaf85847d03e89c9024487cfdf9f62b8557ab` |
| 4-3 | `multimodal-agent/validation/runs/20260729T185433Z-4_2-e028c9db` | passed | true | `1a9cc7bfd48717e73a03ebbde7fd786c7da2811a15267715a3794c0f1220362e` |
| 4-4 | `execution-tools/validation/experiment_4_4/real_mcp_gui_20260802T093657Z` | blocked | false | `fde8976b91b149a61b7d468f4c825c1bdfdc9da3062cbfa66aaa1fd0f3d1966f` |
| 4-5 | `collaboration-tools/validation/experiment_4_5/real_mcp_human_20260803_v2` | blocked | false | `9fae8eadec1f9583ba03e21df5c8bc660cc8bec2ba328cf304bcaa0039bd97a3` |

> **Numbering.** Chapter 4 renumbered its experiments when the “too many tools” section moved ahead of the
> three tool categories: active tool discovery 4-5 → 4-1, perception 4-1 → 4-2, multimodal 4-2 → 4-3,
> execution 4-3 → 4-4, collaboration 4-4 → 4-5. Run directories under `validation/` were renamed to match,
> but the sealed manifests and receipts inside them were left byte-identical, so every hash below still
> verifies against the file it was computed from. Receipts written before the renumber therefore still
> quote the old `experiment_4_N` paths and the old experiment label; that is a record of the run as it
> happened and is deliberately not rewritten.

> **One recorded hash still does not verify, predating this renumber and left as-is rather than
> silently replaced:** the mailbox experiment that became 6-1 has a manifest that now hashes to
> `5b8befd0…` after its `experiment` field was relabelled 4-5 → 6-1 during the chapter-6 split,
> while both `chapter6/EXPERIMENT_LEDGER.md` and `chapter6/.../latest.json` still record the
> pre-relabel `3f689dfe…`. Its Unipile credential still returns 401, so a re-run cannot lift the
> block; only the hash can be corrected, and that is left to a deliberate, documented recomputation.
> The 4-1 hash that previously matched no file has been resolved by the re-run recorded below.

## Experiment 4-1 — active tool discovery

The canonical campaign `rerun_20260825` uses local Ollama `qwen3:4b`,
127 complete schemas from the perception MCP server and an
`all-MiniLM-L6-v2` index. Its manifest SHA-256 matches the table above.
The schema catalog is 50,597 tokens under the experiment's `o200k` tokenizer;
this is a common text-size estimate, not Qwen's native input-token count.
The control system prompt contains 50,829 tokens per task. Treatment starts
with 1,251 system tokens and injects 3,939, 1,853 and 2,632 schema tokens for
the stock, arXiv and contributor tasks respectively.

All twelve recorded gates pass. `grade_plan` measures required capability-slot
coverage: both arms cover all slots for all three tasks. It does not penalize
extra calls or score parameter correctness. `_call_real_tool` supplies task
constants, expands one download selection into three PDF downloads, and
replaces model-supplied code with a deterministic contributor-chart program.
Thus the three passing artifact checks in each arm establish execution with
adapter assistance. `_finalize_execution` checks successful capability calls,
PDF count/signatures/minimum sizes and SVG signature/minimum size; it does not
evaluate paper relevance, causal news analysis or answer/chart correctness.
The manuscript reports capability coverage and schema exposure, rather than
an unqualified accuracy or autonomous-task-completion rate.

Recorded totals are 3,056.294 seconds for control and 783.442 for treatment.
They include model/runtime/API and parser-retry effects and are retained as
run observations. In task order stock/arXiv/contributors, parse-error counts
are 1/1/2 for control and 4/6/1 for treatment. The control contributor trace
also repeats the contributor query and calls `file_stat`. Treatment selects
`yfinance_quote` and `web_search` on the stock task. Earlier descriptions of an
empty stock-task chart and premature finishes belonged to the prior July
campaign and must not be attributed to this August rerun.

The earlier `qwen3_4b_exact_v2_20260730T130600Z` campaign has 126 tools and
separate receipts. Its previously recorded manifest hash `ce9d6eda…` matched
no retained file. The rerun also followed a runner compatibility fix from
`serverInfo` to `server_info`. The recorded runtime workaround was
`OLLAMA_FLASH_ATTENTION=0` after an Ollama 0.20.7 Metal prefill failure with
flash attention enabled. Historical files remain unchanged.

Failed evidence is also preserved. The first exact campaign
`qwen3_4b_exact_20260730T061700Z` completed but had treatment at only 1/3 tasks
(manifest SHA-256
`e3b98be25fca51e3454e442f2e312ff84aad24c89c2d44a7c1e46628cdbebe09`).
The canonical v2 campaign's first terminal attempt hit real arXiv
429/503/disconnect failures; its final search succeeded only on turn 12, too
late to download. Its failed manifest SHA-256 is
`e18bc4465606087c195a2abafbd375048c2921233bae812ef3bc3f522eb9b86b`.
A bounded same-campaign resume archived that failed summary, manifest and task
receipt, reused the other five completed receipts, then made one fresh real
attempt. With the arXiv client page bounded to the requested three results,
the official endpoint succeeded on its first call and all three PDFs were
downloaded, signature-checked and hashed. No cached result or mock substituted
for either failed attempt.

## Experiment 4-2 — perception MCP

Manuscript gates: a real MCP catalog covering search, multimodal understanding, filesystem operations, public data, and authorized private data.

- Passed: real MCP `tools/list`; web and local-knowledge search; HTTPS download and webpage reading; PDF/DOCX/PPTX extraction; OCR; local Whisper transcription; video parsing; DashScope international `qwen-vl-max` image and video analysis with response IDs, token usage, and latency; confined file read/search/list/copy/move/delete; three escape probes; Open-Meteo, Yahoo Finance, exchange-rate, Wikipedia, and arXiv calls.
- Blocked: Google Calendar and Notion. No usable OAuth token or Notion integration credential exists in the environment. The failed calls and credential-free preflight are retained.
- Failed provenance retained: the first DashScope attempt used the mainland endpoint with an international-region key and received 401; the corrected run uses `dashscope-intl.aliyuncs.com`.

Experiment 4-2 integrity review: 45 regular-file entries verify. The remaining
entry `fixtures/mutation_workspace/escape-link` is a `symlink-target` entry
whose retained absolute target differs from its recorded 28-byte target hash.
The link points into the original author's workspace and cannot resolve here.
The historical link and manifest are retained unchanged; the regular-file
receipts preserve the recorded isolation checks. Full 46-entry integrity is
therefore pending reconciliation of this symlink provenance.

## Experiment 4-3 — multimodal processing

Manuscript gates: run the same nontrivial image/PDF and questions through native multimodal, extract-to-text, and tool-on-demand paradigms, retaining real vision calls, tool-use traces, exact-answer quality, latency, usage, and an external judge for free-form output. The canonical run is retained under `multimodal-agent/validation/runs/20260729T185433Z-4_2-e028c9db/`.

Editorial review of Experiment 4-3: the four artifact/question combinations
use one chart as PNG and inside a PDF, with two questions each. Native vision
and tool-on-demand each answer 4/4 completely; text extraction answers 0/4.
All answering stages use `doubao-seed-1-6-250615`; Moonshot judges the answers.
The tool path is prompted to inspect the image when exact values or spatial
associations are missing. It makes decision/vision/final calls for every case.
Reported means are 8.01/10.87/29.79 seconds respectively. Text extraction is
included in text/tool timing, while PDF rendering precedes native timing.
Both retained evidence-file hashes verify. These findings support the specific
information-loss example used in the manuscript.

## Experiment 4-4 — execution MCP

Manuscript gates: verified file write/edit, terminal timeout and dangerous-command review, sandboxed Python, long-output persistence, Excel operations, external system mutations, and browser/desktop/mobile execution.

- Passed: deterministic Python compiler and Node `--check` linter; structured invalid-code responses; workspace escape rejection; timeout; OpenRouter GPT-4.1-mini dangerous-command rejection with raw usage/latency receipts; Docker Python sandbox (`--network none`, read-only root, memory/CPU/PID limits); immutable full long-output retention; XLSX formulas rendered through LibreOffice and PyMuPDF; real HTTPS webhook; real headless Chromium navigation and screenshot; PR #605 created through the GitHub execution tool and then safely reused through query-before-mutation idempotency; headful Chromium on Xvfb driven through OS keyboard events with a hashed framebuffer; and a KVM-backed AndroidWorld API-33 emulator that opened Wi-Fi Settings, verified focus, captured pixels, and returned home through ADB input.
- Blocked: no Google Calendar or real email-provider credentials. Android, Computer Use, and GitHub are no longer blockers. The canonical run passes 13/15 gates while retaining `official_complete: false` for the two absent external mutations.
- Failed provenance retained: `real_mcp_gui_20260802T093348Z` established the GitHub/desktop/mobile gates but failed the spreadsheet gate because LibreOffice and the Chapter 4 PyMuPDF dependency were missing. The corrected canonical run installs/declares both and passes the spreadsheet gate; it reuses the already-open PR instead of creating a duplicate.

## Experiment 4-5 — collaboration MCP

Manuscript gates: sync/async sub-agent lifecycle, messages, cancellation/status, two context-passing strategies, HITL requests with timeout/default behavior, and real multi-channel notification.

- Passed: the canonical v2 run retains six unique Kimi K3 response/usage/latency receipts; real minimal and LLM-generated handoffs; privacy filtering; synchronous and asynchronous completion/status; follow-up messages; cancellation; a conservative timeout; and a live repository-user approval delivered to the same pending MCP request in 1,423.272 seconds within its four-hour response window. The independent validator checks the human/MCP IDs and decision, 55 tool receipts, all 61 manifest hashes, and credential absence.
- Blocked only on delivery: no real SMTP/SendGrid, Telegram, or Slack configuration exists. Credential-free preflights fail explicitly, so `official_complete` remains false even though the human-decision gate is now closed.
- Failed provenance retained: `real_mcp_human_20260803_v1` used a 30-minute live window; the response arrived just after timeout and exposed that an expired request could still be mutated. The failed run preserves the timeout and late-response receipts. The production HITL primitive now rejects late or duplicate responses to terminal requests, with focused regression tests. The earlier `real_mcp_kimi_20260730T063500Z` run also preserves the original too-short async polling failure.
