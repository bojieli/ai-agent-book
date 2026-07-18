# 实验 5-1：用代码生成工具提升数学解题能力

《深入理解 AI Agent》配套实验（★★）。验证一个结论：给 Agent 配上能执行代码的
Python 沙箱后，它在竞赛数学题上的准确率会**显著高于**纯思维链（Chain-of-Thought, CoT）。

## 目的

大模型「心算」大数、枚举、因式分解时极易出错——不是不会方法，而是算错。
本实验让同一个模型（默认 `gpt-5.6-luna`）在同一组题上跑两种模式，直接对比：

- **纯 CoT**：只能用自然语言一步步推理，禁止写代码；
- **代码辅助**：把题目形式化为 Python（sympy 符号计算、numpy 矩阵、scipy 数值求解），
  通过 function calling 调用 `run_python` 工具在**子进程沙箱**里执行，用精确结果替代心算。

## 原理

```
题目 ──► 模型
          │  纯 CoT：直接自然语言推理 ─────────────► 最终答案（易算错）
          │
          └─ 代码辅助：生成 Python 代码
                       │  function calling
                       ▼
                 run_python 工具（子进程沙箱，预装 sympy/numpy/scipy，超时保护）
                       │  返回 stdout
                       ▼
                 模型基于精确结果继续推理 ──────────► 最终答案（更准）
```

- 工具用 OpenAI **function calling** 暴露：模型自主决定何时写代码、写什么代码。
- 沙箱是 `sandbox.py` 里的 `run_python()`：把代码写入临时文件，用子进程执行，
  带 20 秒超时，崩溃/死循环不影响主进程。预导入了 `sympy / numpy / scipy`。
- 题目在 `problems.json`：11 道 AIME 风格竞赛题，**答案均为整数、已用暴力枚举离线校验**，
  覆盖数论、模运算、丢番图方程、生成函数、素因子分解、格点计数等。每题还附带一段
  `solution` 参考解代码，用于离线自检（见下）。

## 离线自检（无需 API key）

想验证「沙箱 + 题库真值」这条链路是否可用、但手头没有 API key？跑：

```bash
pip install -r requirements.txt
python demo.py --selfcheck        # 在沙箱中执行每题的参考解，按真值判分
```

它会对每道题执行 `problems.json` 里附带的参考解，在子进程沙箱中运行，抽取整数输出
与真值比对——这既演示了「写代码 → 沙箱执行 → 按真值判分」的核心机制，也自检了题库
真值本身。全部命中时退出码为 0。真实输出（11/11 全部通过）：

```
题号   考点                             真值      沙箱输出
--------------------------------------------------------
1    number theory (inclusion-exclusion)    925       925   ✓
2    modular exponentiation        216       216   ✓
...
11   lattice points               1245      1245   ✓
--------------------------------------------------------
参考解命中真值：11/11
```

## 运行对照实验（需要 API key）

```bash
cp env.example .env   # 或直接 export OPENAI_API_KEY=...
export OPENAI_API_KEY=sk-...      # 也支持 MOONSHOT_API_KEY / ARK_API_KEY

python demo.py                    # 跑完整对照实验（code 与 cot 两种模式）
python demo.py --verbose          # 额外打印模型生成的代码与执行结果
python demo.py --limit 3          # 只跑前 3 题（省钱调试）
python demo.py --mode code        # 只跑代码辅助模式
python demo.py --mode cot         # 只跑纯思维链模式
python demo.py --model gpt-4o     # 覆盖模型名（等价于设 MODEL 环境变量）
python demo.py --output result.json   # 把逐题结果与汇总写入 JSON
python demo.py --problems mine.json   # 换用自定义题库
```

完整参数见 `python demo.py --help`。常用开关：

| 参数 | 说明 |
| --- | --- |
| `--mode {both,code,cot}` | 求解模式，默认 `both`（两种都跑并对照） |
| `--selfcheck` | 离线自检，只跑沙箱参考解，无需 API key |
| `--model 名称` | 覆盖模型名（优先级高于 `MODEL` 环境变量） |
| `--problems 路径` | 题库 JSON 路径，默认 `problems.json` |
| `--limit N` | 只跑前 N 题 |
| `--output 路径` | 把逐题结果写入 JSON 文件 |
| `--verbose` | 打印生成的代码与沙箱执行结果 |

可用环境变量：`OPENAI_API_KEY`（或 `MOONSHOT_API_KEY` / `ARK_API_KEY`）、
`OPENAI_BASE_URL`（切换兼容端点）、`MODEL`（默认 `gpt-5.6-luna`）。

**通用 OpenRouter 兜底**：未配置任何直连 key 时，只要设置了 `OPENROUTER_API_KEY`
即可自动改走 OpenRouter（模型名自动映射：`gpt-*` → `openai/*`，其它 → `openai/gpt-5.6-luna`）。
另外默认模型 `gpt-5.6-luna` 属于 gpt-5.x，直连 OpenAI 调用它需要组织实名认证，
因此只要设置了 `OPENROUTER_API_KEY` 就会优先走 OpenRouter（route `openai/gpt-5.6-luna`）。

## 预期输出示例 / 结论

真实跑 `gpt-4o-mini`（11 题，`temperature=0`）的一次逐题结果节选：

```
题号   考点                             真值     CoT预测          代码预测
------------------------------------------------------------------------------
2    modular exponentiation        216       216   ✓       216   ✓
4    perfect squares              1464      1495   ✗      1464   ✓
7    prime factorization           661       661   ✓       661   ✓
10   factorials and modular arithmetic    313       113   ✗       313   ✓
11   lattice points               1245      1211   ✗      1245   ✓
------------------------------------------------------------------------------
准确率                                   6/11 =   55%      8/11 =   73%
```

| 模式 | 准确率（典型区间） |
| --- | --- |
| 纯 CoT | 约 5~6 / 11（≈ 45%~55%） |
| 代码辅助 | 约 8~9 / 11（≈ 73%~82%） |

**代码辅助模式准确率稳定地显著高于纯 CoT。** 纯 CoT 在需要大数运算 / 大量枚举的题上
频繁算错——例如大数取模（2^2024 mod 1000）、100! 累加取模、x²+y²<400 的格点计数、
n²+12n−2007 何时为完全平方——而代码辅助把这些交给 sympy/numpy 精确计算，逐题命中。

> **不是 100%，也不该是。** 代码辅助并非万能：`gpt-4o-mini` 偶尔会写出「思路对、
> 细节错」的枚举代码（最常翻车的是第 6 题「两平方和计数」的边界、第 8 题「恰好 6 个
> 约数」的计数逻辑），此时精确执行的是一段有 bug 的代码。因此代码辅助的准确率会在
> 上表区间内随机波动，但「显著高于纯 CoT」这一结论每次运行都稳定成立。换更强的模型
> （见下）通常能把这几道题也补齐到接近满分。

## 如何适配 / 扩展

- **换模型 / 供应商**：设 `MODEL` 环境变量即可换模型（如 `MODEL=gpt-4o`、`MODEL=o4-mini`）；
  换供应商则设 `MOONSHOT_API_KEY`（自动切 Kimi）或 `ARK_API_KEY`（自动切豆包），
  或用 `OPENAI_BASE_URL` 指向任意兼容 OpenAI 协议的端点。更强模型能把偶发的 bug 代码补齐。
- **换题库**：编辑 `problems.json`，每题给出 `question` / `answer`（整数）/ `topic`，
  并附一段 `solution`（打印答案的 Python 参考解）。建议新增题目时像现有题一样**先用
  `python demo.py --selfcheck` 让参考解在沙箱里跑出真值**，避免答案本身出错。
- **换沙箱能力**：`sandbox.py` 的 `PREAMBLE` 预导入 sympy/numpy/scipy；要支持更多库
  就在此追加 import 并同步更新 `requirements.txt`。

## 局限

- 沙箱是教学级实现（子进程 + 超时 + 临时目录），**不是安全隔离边界**；生产环境应换成
  容器 / gVisor / 无网络的强隔离沙箱。
- 准确率依赖模型质量：小模型仍可能写出有 bug 的代码（见上），代码辅助降低但不消除错误。
- 答案抽取按 `FINAL ANSWER: <整数>` 解析，仅支持整数型答案；非整数 / 多值答案需改
  `extract_answer` 与判分逻辑。

## 文件

| 文件 | 说明 |
| --- | --- |
| `demo.py` | 主程序：对照实验 + function calling 循环 + 结果表 + 离线自检（`--selfcheck`） |
| `sandbox.py` | 子进程 Python 沙箱（`run_python`，超时保护，预装数学库） |
| `problems.json` | 11 道竞赛题（题面 + 已校验的整数真值 + 考点 + 参考解 `solution`） |
| `requirements.txt` | 依赖 |
| `env.example` | 环境变量样例 |
