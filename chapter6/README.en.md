# Chapter 6 · Agent Evaluation

> Turns Agent performance into comparable signals. Covers evaluation environments, dataset design, metric systems, statistical significance, observability, evaluation-driven selection, and production-grade internal evaluation and simulation environments.

← [Back to main README](../README.en.md) · 📖 [Read chapter text](../book-en/chapter6.md)

## Companion Projects

| Project | Type | Description |
| --- | :--: | --- |
| [terminal-bench](terminal-bench/) | 📖 | Terminal-Bench is a benchmark for testing AI Agent performance in real terminal environments. From compiling code to training models and setting up servers, it evaluates how Agents handle real end-to-end tasks. Includes a dataset of ~100 tasks and an execution framework, supporting various Agent implementations. |
| [SWE-bench](SWE-bench/) | 📖 | SWE-bench is a benchmark for evaluating the ability of large language models to solve real GitHub issues. Given a codebase and an issue description, the model must generate a patch that resolves the problem. Includes multiple versions: SWE-bench, SWE-bench Lite, SWE-bench Verified, and SWE-bench Multimodal. |
| [GAIA](GAIA/) | 📖 | GAIA aims to evaluate next-generation LLMs (those with tool augmentation, efficient prompting, search access, etc.). It contains 450+ non-trivial questions requiring varying degrees of tool use and autonomy, with unambiguous answers. Divided into 3 difficulty levels. |
| [OSWorld](OSWorld/) | 📖 | Evaluates the ability of agents to perform complex tasks within a complete operating system environment, including file management, application operation, and system configuration. |
| [android_world](android_world/) | 📖 | Evaluates agent performance in an Android mobile environment, including app navigation, UI interaction, and task completion capabilities. |
| [tau2-bench](tau2-bench/) | 📖 | Focuses on evaluating an agent's ability to use tools for complex reasoning, including scenarios such as computation, search, and data processing. |
| [elo-leaderboard](elo-leaderboard/) | ✅ | Implements an agent performance leaderboard based on the ELO rating system, evaluating the relative abilities of different agents through pairwise comparisons. |
| [model-benchmark](model-benchmark/) | ✅ | Conducts a horizontal benchmark of multiple OpenAI-compatible LLM API providers. It uses a streaming interface to precisely measure Time to First Token (TTFT), calculates end-to-end latency percentiles (p50/p95), throughput, and success rate under concurrency. A single command produces a multi-dimensional comparison table, illustrating that model selection is a multi-faceted trade-off rather than just looking at a leaderboard. |
| [agent-cost-analysis](agent-cost-analysis/) | ✅ | Performs a full-chain cost breakdown for a typical multi-turn agent task (customer service refund): uses a custom lightweight tracing system to record input/output/cache tokens, latency, and cost for each LLM call, aggregates to identify "which step is the most expensive," and then uses A/B testing to quantify the real savings from KV-cache-friendly design and context compression. |
| [tts-quality-eval](tts-quality-eval/) | ✅ | Synthesizes the same set of challenging texts using various TTS configurations (different model/voice/speed), then uses a multimodal LLM-as-a-Judge to score each dimension (clarity, naturalness, etc.) according to a Rubric, aggregating the results into a reproducible configuration comparison table. |

> `chapter6/android-world/` (hyphenated naming) is not the benchmark code, but rather the book's analysis notes (`t3a*.md`) on T3A Agent failure cases on android_world, which can be used as reference reading material.
## Project Types

| Icon | Type | Meaning |
| :--: | --- | --- |
| ✅ | **Standalone** | Full code in this repo, runs after configuring API Key |
| 📖 | **Reproduction Guide** | Detailed doc depending on **external repos** to `git clone` |
| 🚧 | **Design Doc** | Architecture/implementation plan only, runnable code still WIP |
