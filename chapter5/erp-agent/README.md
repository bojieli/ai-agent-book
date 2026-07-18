# 实验 5-10：自然语言交互的 ERP Agent（NL → SQL，artifact 模式）

把中文自然语言查询自动转成 SQL，由系统执行并直接呈现结果表。核心是 **artifact（制品）模式**：
Agent 只负责「生成 SQL」这个制品，真正的数据查询交给数据库执行，**LLM 不亲自搬运数据**——
既省 token、又避免大模型手算出错，几万行结果也能秒回。

## 数据模型（两张表）

- `employees`：员工ID、姓名、部门、级别（数字越大越高）、入职日期、离职日期（NULL = 在职）
- `salaries`：员工ID、发薪日期（每月一条，`YYYY-MM-01`）、工资

数据由 `seed.py` 用固定随机种子（42）生成、以「今天」为基准相对生成，**完全可复现**：
约 40 名员工跨 5 个部门/多级别，含若干已离职者；工资按「入职基准 + 每年固定涨薪额」逐月生成，
每人涨薪额互不相同（保证问题 9 排名唯一）；并刻意为一名在职员工删掉某月工资（制造问题 10 的「拖欠」）。

## 10 个自动回答的问题

1. 平均每个员工在职多久　2. 每个部门有多少在职员工　3. 哪个部门平均级别最高
4. 每个部门今年/去年各新入职多少人　5. 前年3月到去年5月 A 部门平均工资
6. 去年 A/B 部门平均工资哪个高　7. 今年每个级别平均工资
8. 入职一年内 / 一到两年 / 两到三年员工的最近一月平均工资
9. 去年到今年涨薪最大的 10 位员工　10. 有没有拖欠工资（某月在职却没发薪）

其中 A 部门 = 研发部，B 部门 = 销售部（在 prompt 中约定）。

## 运行

```bash
pip install -r requirements.txt
cp env.example .env      # 填入 OPENAI_API_KEY
python demo.py           # 等价于 python demo.py run
```

**通用 OpenRouter 兜底**：未配置 `OPENAI_API_KEY` 时，设置 `OPENROUTER_API_KEY` 即自动
改走 OpenRouter（`gpt-*` → `openai/*`，其它 → `openai/gpt-5.6-luna`）。默认模型
`gpt-5.6-luna` 属 gpt-5.x，直连 OpenAI 需组织实名认证，故设置了 `OPENROUTER_API_KEY`
时会优先走 OpenRouter。

`demo.py` 提供 4 个子命令（不带子命令时等价于 `run`）：

| 子命令 | 是否需要 API | 作用 |
| --- | --- | --- |
| `run` | 需要 | 在线：Agent 生成 SQL → 执行 → 与参考实现比对，逐题打印并给出总通过率 |
| `gold` | **不需要** | 离线自检：执行内置「标准 SQL」（`gold.py`）跑 10 题并比对，证明数据模型自洽 |
| `ask` | 需要 | 单条自然语言查询 → 生成 SQL → 执行并打印结果表 |
| `initdb` | 不需要 | 建表并把种子数据灌入一个 SQLite 文件，便于用 `sqlite3` 手工查看 |

常用参数：`--only 1,5,10`（只跑指定题号）、`--db erp.db`（用文件库而非内存库）、
`--model gpt-5.6-luna`（覆盖模型）、`--output result.json`（导出逐题明细）。示例：

```bash
python demo.py gold                 # 离线跑通 10 题，无需 API
python demo.py run --only 2,3,6     # 只让 Agent 生成这 3 题的 SQL 并校验
python demo.py ask "研发部现在有多少在职员工？"
```

在线模式会：建 SQLite 内存库 → 灌种子数据 → 逐题让 Agent 生成 SQL → 执行 → 打印
「问题 / 生成的 SQL / 查询结果 / 是否通过」，最后给出总通过率。

## 正确性校验

`reference.py` 是**独立的 Python 参考实现**：不走 SQL，直接在种子数据上把每题答案算一遍。
`demo.py` 把 SQL 的执行结果与参考答案按「多重集合 + 数值容差」比对，逐题打印 通过/不通过。
`gold.py` 是人工编写的 10 条「标准 SQL」，`python demo.py gold` 离线执行它们即可自检，无需 API。

最近一次真实运行：离线 `gold` 通过率 **10/10**；在线 `run`（`gpt-4o-mini`，temperature=0）
同样稳定通过（本次抽查题 2/3/6，均 通过）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `demo.py` | 命令行入口（run/gold/ask/initdb）：建库、灌数据、跑题、执行 SQL、比对、打印通过率 |
| `seed.py` | 可复现的种子数据生成 + 建表灌数 |
| `reference.py` | 10 题的独立 Python 参考实现（校验基准） |
| `gold.py` | 10 题人工编写的「标准 SQL」（SQLite 方言），供 `gold` 离线自检 |
| `questions.py` | 10 个自然语言问题 + 给 Agent 的「返回列/业务口径」提示 |
| `agent.py` | NL→SQL Agent（OpenAI SDK，读 `OPENAI_API_KEY` 或 `OPENROUTER_API_KEY` 兜底，默认 `gpt-5.6-luna`） |
| `schema_postgres.sql` | 书中 PostgreSQL 版建表 DDL（迁移到真实 Postgres 时参考） |

## 关于数据库

本项目用 **SQLite**（零依赖、可直接复现）。书中示例用 **PostgreSQL**，SQL 大体通用，
差异主要在日期函数：本项目用 SQLite 的 `strftime('%Y','now')`、`julianday()`、`date('now','-1 year')` 等；
迁到 PostgreSQL 时对应换成 `EXTRACT(YEAR FROM now())`、`AGE()`/日期相减、`now() - interval '1 year'` 等即可。

## 说明与注意事项

- Agent 的 prompt 里补充了 schema 级提示：期望返回哪些列/顺序、业务口径（在职=leave_date 为空、
  今年/去年如何用 `strftime(...,'now',...)` 推导、A/B 部门映射），以及**禁止硬编码年份**
  （否则模型不知道「今天」是哪年，会把「前年/去年」猜错）。这些是合理的 schema 提示，不泄露具体答案。
- 问题 8、10 较复杂（工龄分档取最近一月工资、递归生成在职月份找空缺），在提示里给了推荐的
  SQL 结构模板，帮助较小模型稳定产出正确 SQL。
- `temperature=0` 让输出尽量稳定，但 LLM 仍非严格确定性；若个别题偶发偏差，重跑即可，
  也可换更强的模型（设 `OPENAI_MODEL`）。
