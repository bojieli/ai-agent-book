# 实验 5-2：用代码生成工具提升逻辑思考能力

《深入理解 AI Agent》配套代码。

本实验评估 Agent 通过**约束求解**代码来辅助逻辑思考的能力：为同一个 LLM 配备一个预装
`python-constraint` 的 Code Interpreter，让它把「骑士与无赖」(Knights & Knaves) 逻辑谜题
转化为形式化的**约束满足问题(CSP)**——识别变量(每个岛民是骑士还是无赖)、定义约束
(“骑士说真话、无赖说假话”)，再调用求解器搜索满足所有约束的解。

我们用一组 12 道 K&K 谜题(2~5 人，均带唯一真值解)对比三种模式：

- **纯思考(pure)**：LLM 只用自然语言链式推理，直接给答案；
- **代码辅助(code)**：LLM 用 `run_python` 工具写约束模型并调求解器，再据结果作答；
- **约束求解(solver)**：**离线基线**，直接用 `python-constraint` 求解结构化陈述，
  不需要任何 API/网络——它是确定性求解器路径本身，理论上 100% 正确，用来验证
  「把谜题翻译成约束程序并求解」这一核心论点(见下方真实运行结果)。

## 核心思想：为什么代码辅助更强

K&K 谜题的关键建模规则只有一条——对每位居民 X 加一条**双条件(等价)约束**：

```
X 是骑士(True)  <=>  X 说的那句话为真
```

即 `X == (该陈述的语义真值)`。把它交给确定性求解器**穷举**所有布尔组合，逻辑上不会出错；
而纯思考在多人、含计数(“恰好两个骑士”)或自指(“我和 B 同类”)的谜题上，很容易在心算
真值传播时出错。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `demo.py` | 主程序：跑 纯思考/代码辅助/约束求解 的对照实验，打印准确率对比表 |
| `csp_solver.py` | 离线约束求解器：结构化陈述 DSL + `python-constraint` 求解(供 demo 的 solver 模式与 build_puzzles 校验共用) |
| `sandbox.py` | 极简 Code Interpreter：子进程沙箱执行模型生成的 Python(预装 python-constraint) |
| `puzzles.json` | 12 道谜题的题面 + 结构化陈述 + 唯一真值解(给 LLM 的只有题面) |
| `build_puzzles.py` | 生成/校验谜题：用 `python-constraint` 求解并断言每题“解唯一”，可导出精选题或随机生成 |
| `requirements.txt` | 依赖(openai + python-constraint) |
| `env.example` | 环境变量样例 |
| `last_run.json` | 每次运行后自动保存的逐题完整记录(含模型生成的代码)，便于复盘 |

## 快速开始

```bash
pip install -r requirements.txt
```

### 1) 离线约束求解基线（不需要 API Key，推荐先跑）

```bash
python demo.py --mode solver          # 用 python-constraint 离线求解全部 12 题
python demo.py --mode solver --min-people 4   # 只跑 >=4 人的难题
```

这条路径完全离线、确定性，直接演示「谜题→约束程序→求解」的核心论点，准确率 100%。

### 2) LLM 对照实验（需要 OPENAI_API_KEY 或 OPENROUTER_API_KEY）

```bash
cp env.example .env        # 然后编辑 .env 填入 OPENAI_API_KEY
# 或直接 export OPENAI_API_KEY=sk-...

python demo.py             # 默认 both：纯思考 vs 代码辅助，全部 12 题
python demo.py --mode pure # 只跑纯思考基线
python demo.py --limit 4   # 只跑前 4 题(省钱冒烟测试)
python demo.py --max-people 3        # 只跑 <=3 人的谜题(按难度筛选)
python demo.py --model gpt-5.6-luna  # 指定模型(默认 gpt-5.6-luna)
python demo.py --puzzles my.json --output run.json   # 换数据集/输出路径
```

**通用 OpenRouter 兜底**：未配置 `OPENAI_API_KEY` 时，只要设置了 `OPENROUTER_API_KEY`
即自动改走 OpenRouter（`gpt-*` → `openai/*`，其它 → `openai/gpt-5.6-luna`）。默认模型
`gpt-5.6-luna` 属 gpt-5.x，直连 OpenAI 需组织实名认证，故设置了 `OPENROUTER_API_KEY`
时会优先走 OpenRouter。

完整参数见 `python demo.py --help`（中文说明）。

### 3) 生成/扩充谜题数据集

```bash
python build_puzzles.py                     # 导出内置 12 道精选题(默认)
python build_puzzles.py --generate 20 --min-people 3 --max-people 5 --seed 7
python build_puzzles.py --generate 20 --output my.json
```

随机生成器会用 `python-constraint` 求解每个候选谜题，只保留「解唯一」的题目。

`sandbox.py` / `csp_solver.py` 也可单独运行做自测：
`python sandbox.py`、`python csp_solver.py` 都会用 python-constraint 求解一道最简谜题。

## 真实运行结果（一）：离线约束求解基线（`--mode solver`，无需 API）

`python demo.py --mode solver` 的真实输出（12 道精选题，完全离线、确定性）：

```
== 约束求解(solver，离线) ==
  [solver] kk01 (2人) ✓  解数=1  预测={'A': 'knight', 'B': 'knave'}
  [solver] kk05 (3人) ✓  解数=1  预测={'A': 'knave', 'B': 'knave', 'C': 'knight'}
  [solver] kk11 (5人) ✓  解数=1  预测={'A': 'knight', 'B': 'knight', 'C': 'knave', 'D': 'knave', 'E': 'knight'}
  ...（其余题略）
------------------------------------------------------------
准确率            100.0%
============================================================
约束求解   准确率: 100.0%  (12/12)
```

这条路径把每题的结构化陈述翻译成 `python-constraint` 约束并穷举求解，12/12 全对——
它直接证明了「谜题→约束程序→求解」的确定性；LLM 只要把谜题正确翻译成同样的约束，
就能拿到同样 100% 的结果（下节）。随机生成的谜题（`build_puzzles.py --generate`）经
solver 复核同样 100% 解出且与生成时的唯一解一致。

## 真实运行结果（二）：LLM 对照实验（gpt-4o-mini，12 题）

```
准确率对比表
============================================================
题号      人数    纯思考       代码辅助
------------------------------------------------------------
kk01    2     ✓         ✓
kk02    2     ✓         ✓
kk03    2     ✓         ✓
kk04    3     ✓         ✓
kk05    3     ✗         ✓
kk06    3     ✗         ✓
kk07    3     ✗         ✓
kk08    4     ✗         ✓
kk09    4     ✗         ✓
kk10    4     ✓         ✓
kk11    5     ✗         ✓
kk12    5     ✓         ✓
------------------------------------------------------------
准确率             50.0%    100.0%
============================================================
纯思考   准确率: 50.0%  (6/12)
代码辅助 准确率: 100.0% (12/12)
提升: +50.0 个百分点
```

> 说明：`gpt-4o-mini` 具有随机性，多次运行数字会有小幅波动；但稳定结论是
> **代码辅助达到 90%+ 且显著高于纯思考**，尤其在 4~5 人的谜题上差距明显。

### 一道谜题的约束建模代码（模型自动生成，kk11，5 人链式+计数）

题面：A 说“B 是骑士”；B 说“C 是无赖”；C 说“D 是骑士”；D 说“E 是无赖”；
E 说“我们五人当中至少有两个骑士”。

```python
from constraint import Problem

p = Problem()
for name in ['A', 'B', 'C', 'D', 'E']:
    p.addVariable(name, [True, False])   # True=骑士(说真话), False=无赖(说假话)

# 每句话都写成「X == (那句话的真值)」的双条件约束
p.addConstraint(lambda a, b: a == (b == True), ['A', 'B'])          # A:"B 是骑士"
p.addConstraint(lambda b, c: b == (c == False), ['B', 'C'])        # B:"C 是无赖"
p.addConstraint(lambda c, d: c == (d == True), ['C', 'D'])         # C:"D 是骑士"
p.addConstraint(lambda d, e: d == (e == False), ['D', 'E'])        # D:"E 是无赖"
p.addConstraint(lambda a, b, c, d, e: e == ((a + b + c + d + e) >= 2),
                ['A', 'B', 'C', 'D', 'E'])                          # E:"至少两个骑士"

for s in p.getSolutions():
    print({k: ('knight' if v else 'knave') for k, v in s.items()})
# 输出: {'A': 'knight', 'B': 'knight', 'C': 'knave', 'D': 'knave', 'E': 'knight'}
```

求解器直接穷举 2^5=32 种组合，返回满足全部约束的唯一解——这正是纯思考在链式真值
传播中最容易算错的题型。

## 注意事项

- **成本**：默认 `gpt-4o-mini`，跑完 12 题两种模式约几分钱人民币，很便宜。
- **API Key**：从环境变量或 `.env` 读 `OPENAI_API_KEY`（或 `OPENROUTER_API_KEY` 兜底）；用 `MODEL` 可换模型。
- **沙箱**：`sandbox.py` 用子进程 + 超时执行代码，属教学用极简沙箱；生产环境应换成
  容器/gVisor 等更强隔离。
- **谜题可靠性**：`build_puzzles.py` 用 `python-constraint` 求解每题(内置精选题或随机生成)，
  断言“解唯一”后才写出，确保真值解无歧义；想自己加题就改 `CURATED` 或用 `--generate`。
