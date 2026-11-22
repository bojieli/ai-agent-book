# Experiment 5-12: Permission-Embedded Data Objects / 实验 5-12：权限内嵌的数据对象（★★★）

生成代码能够灵活处理数据，也增加了权限检查被遗漏的可能。本节学习怎样把访问约束放在独立的数据接口中，使调用方需要通过统一入口使用数据。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4)。

<a id="learning-0"></a>

## 理解问题与方法

权限属于执行与数据层的责任，不应仅写在模型提示词中。数据对象可以提供受控操作，并限制哪些字段或记录对当前调用者可见。接口设计还需考虑错误处理和审计，才能解释一次访问为何被允许。

### 实验目标

验证业务代码可以动态生成或重写时，系统仍能保证权限和数据完整性。实验把应用层故意做得很薄：生成的代码只调用稳定的对象存储接口；权限规则、校验器、对象关系和后果声明附着在数据类型上，由对象存储在每次操作时统一检查。

确定性演示包含三类操作：合法的招聘流程更新应当成功；跳过候选人状态机或写入超出职位范围的工资应由数据层拒绝；跨租户读取应由权限边界拒绝。

### 技术方案

项目是运行在 PostgreSQL 之上的 Python 中间层。`models.py` 定义数据对象、对象类型、权限规则和访问上下文；`store.py` 实现三层流水线：同步执行权限检查与校验器，完成持久化和引用完整性处理，再以受控深度异步执行 reactions（后果反应）。`scenarios/` 提供招聘、项目管理等带状态机、跨对象校验和多租户隔离的示例 schema。`run_targeted_eval.py` 则是可选的在线评测：让模型分别为裸 SQL 和 PEDO 接口生成代码，再用对抗性请求检查最终数据库状态。

这个实验关注的不是生成的 handler 有没有写出一条正确的 `if`，而是同一请求到达稳定数据层后能否被可靠接受或拒绝。生成代码只能携带受限的 `AccessContext`，不能拿到可绕过规则的高权限数据库连接。

<a id="learning-1"></a>

## 准备环境与输入

本节适合先结合已有记录阅读。先弄清记录对应的任务、版本与运行条件，再决定是否准备完整环境复现；已有输出是学习材料，也有其适用范围。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读示例数据对象和权限测试，列出不同角色应能读取的范围。再按下文建立本地样例数据库，检查允许与拒绝的正常访问案例。阅读生成代码时，关注它是否通过受控接口，而不是增加越权尝试。

### 运行

先启动 PostgreSQL，并准备 `pedo_test` 数据库，然后执行：

```bash
cd chapter5/permission-embedded-data-objects
python -m pip install -r requirements.txt
createdb pedo_test
python demo.py
pytest -q
```

可通过 `PEDO_DSN` 指定其他 PostgreSQL 连接串。在线评测还需要安装
`anthropic`、`openai` 并配置对应的 API 凭证；它会在隔离测试库中执行模型生成的代码，不应直接指向生产数据库。

<a id="learning-3"></a>

## 分析结果与形成判断

一次拒绝只能说明该访问被阻止；还要确认合法任务能完成，并且错误消息不会暴露受限数据。评估结论应限定在测试覆盖的接口和权限规则内。

### 检查自己的解释

同一查询涉及多个权限等级的记录时，接口应返回部分结果，还是整体拒绝？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

This project is the implementation companion for the **dynamic software**
discussion in Chapter 5. It is adapted from the
`PermissionEmbeddedDataObjects` prototype: the implementation code, scenarios,
tests, and the targeted generated-code evaluator are included here; the paper,
PDF, website, and large result files are intentionally left out.

### 文件

- `demo.py`：无需调用 LLM 的确定性演示；
- `pedo/core/`：权限内嵌对象模型和三层对象存储；
- `pedo/scenarios/`：招聘、项目管理及其他多租户场景；
- `tests/`：核心权限、校验、租户隔离和反应机制测试；
- `run_targeted_eval.py`：可选的 Agent 生成代码安全对照评测。

## English

### Goal

Show how an application whose business code may be generated or rewritten by an
Agent can still enforce authorization and data integrity. The experiment makes
the application layer deliberately small: generated code calls a stable object
store, while permissions, validators, relationships, and consequences are
declared with the data type and checked by the store on every operation.

The deterministic demo exercises three cases:

1. a valid hiring-pipeline update is accepted;
2. generated code that skips a candidate status transition or writes an
   out-of-range salary is rejected by the data-layer validator;
3. a cross-tenant read is rejected by the permission boundary.

### Technical plan

The prototype is a Python middleware layer over PostgreSQL:

- `pedo/core/models.py` defines `DataObject`, `ObjectType`, `PermissionRule`,
  `AccessContext`, relationships, and reaction declarations;
- `pedo/core/store.py` implements the three-tier pipeline: synchronous
  permission checks and validators, persistence and referential-integrity
  mechanics, then asynchronous reactions with a bounded depth;
- `pedo/scenarios/` registers realistic hiring, project-management, and other
  multi-tenant schemas with state machines and cross-object validators;
- `run_targeted_eval.py` is an optional live comparison that asks models to
  generate code for raw SQL and PEDO APIs on adversarial prompts, then checks
  the resulting database state.

The key comparison is not whether the generated handler contains a correct
`if` statement. It is whether the same request is accepted or rejected when it
reaches the stable data layer. The generated layer receives a scoped
`AccessContext`; it does not receive a privileged database connection.

### Run the deterministic demo

PostgreSQL must be running and the database named by `PEDO_DSN` must be
reachable. The default is `dbname=pedo_test`.

```bash
cd chapter5/permission-embedded-data-objects
python -m pip install -r requirements.txt
createdb pedo_test                 # if the database does not exist yet
python demo.py
pytest -q
```

Use another connection string with, for example,
`PEDO_DSN='dbname=pedo_test host=localhost user=postgres'`.

The optional live evaluator needs provider SDKs and credentials in addition to
the core requirements:

```bash
python -m pip install anthropic openai
DATAGUARDBENCH_DSN="$PEDO_DSN" python run_targeted_eval.py
```

Run that evaluator only in an isolated test database. It executes model-
generated code by design and is not a production security boundary.
