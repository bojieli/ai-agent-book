# 实验 9-6：由失败轨迹触发 Agent 自我修改

工具已经说明错误不可重试，Agent 却仍重复调用，这可能是控制逻辑的问题。本实验学习如何从这类轨迹提出代码修改，并验证候选没有破坏其他行为。

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

重试、熔断和停止条件属于运行控制。候选代码应在独立环境中执行测试，改进证据来自失败用例与正常用例的共同结果。模型提出补丁与补丁被采用是两个阶段。

本项目演示实验 9-6 的 Agent 自我修改：生产轨迹显示同一个 `retryable=false` 错误仍被连续调用时，系统应修改 Agent 的重试与熔断控制代码，而不是只在 Prompt 中追加一句“不要重复调用”。

### 从失败簇形成候选修改

实验从 `failure_trajectories.json` 聚合重复故障。只有同一模式在多条轨迹中得到支持才形成修改请求；诊断模块将根因定位到 `stable/retry_policy.py`。提案生成器从稳定源码产生最小 diff，但只写入 `output/candidate/`，不会覆盖正在运行的稳定版本。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

### 准备隔离执行环境

候选代码的运行验证需要 Docker。首次运行会从锁定摘要的 Python 3.12 Alpine
基础镜像自动构建内容寻址的本地沙箱镜像；也可以通过
`SELF_MODIFY_SANDBOX_IMAGE` 指定预先审核并构建好的镜像。待验证代码只在一次性
容器中执行：容器禁用网络和 IPC、使用只读根文件系统和非 root 用户、丢弃全部
Linux capabilities、禁止提权，并限制 CPU、内存、进程数、文件描述符、临时空间、
输出大小和墙钟时间。超时、OOM、Docker 不可用或协议输出异常都会关闭失败，不能
进入 Canary。

`python demo.py` 仍保留为单提案教学入口，不能单独关闭真实实验。`run_experiment_9_6.py` 才是验收入口：它先保留一个会禁用所有临时错误重试的已拒绝提案，把具体失败原因提供给真实 Coding Agent，再让确定性生成器和真实 Coding Agent 经过同一组模型外门槛。

### 配置其他模型服务

如需改用 OpenAI 直连：

```bash
# 从仓库根目录开始：使用共享的第 9 章环境
uv sync --locked --python 3.12 --extra ch9
# Apple Silicon macOS 需要 macOS 14+（锁文件中的 bitsandbytes wheel 要求）；
# 更早的 macOS 请使用下方单项目兼容路径。

# 切换目录前先激活环境：
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch9]"

cd chapter9/self-modifying-agent

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

export OPENAI_API_KEY=your_api_key_here
python run_experiment_9_6.py --provider openai --model gpt-4o-mini
```

真实模式使用 OpenAI 兼容的 Chat Completions API 读取失败诊断和稳定源码，返回完整代码提案。模型输出仍只能写入 `validation/<run>/candidates/` 隔离目录；静态编译、失败重放、旧任务回归、发布决定与回滚版本全部由模型外部代码执行。若 LLM 生成了看似合理但破坏旧重试行为的补丁，命令会明确返回 `reject_candidate`。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读失败轨迹，找到不可重试标记出现后仍继续调用的位置。再检查现有控制逻辑与测试。按下文准备隔离执行环境和模型后，生成候选并查看它如何改变重试分支。

### 运行单元测试与完整实验

机制单元测试与真实验收是两条不同路径：

```bash
python -m pytest -q test_evolution.py
python run_experiment_9_6.py \
  --provider ark --model doubao-seed-1-6-250615 --seed 8501
```

<a id="learning-3"></a>

## 分析结果与形成判断

少一次调用不一定正确：可重试错误仍可能需要恢复。测试应同时覆盖继续、停止和超时，并说明候选能修改的范围。

### 验证候选的行为

验证阶段先在宿主机做不执行源码的编译和 AST 预筛，再在 Docker 安全边界内检查公开函数签名、原失败轨迹、首次永久错误熔断、临时超时恢复、旧阈值回归、影子 Canary、回滚制品和行为指标。AST 拒绝列表只是快速纵深防御，不被视作执行不可信 Python 的安全边界。所有检查（包括 `sandbox_execution`）通过才生成 `release_to_canary`，绝不直接发布生产；否则返回 `reject_candidate`。

`release_manifest.json` 记录失败簇、逐条来源轨迹及哈希、根因、目标组件与文件、影响预测、代码 diff、潜在回退、全部检查、提案哈希和回滚哈希。生成前后还会比较稳定代码、失败轨迹和沙箱验证器的 SHA-256，证明 Coding Agent 没有越权修改可信根。

### 已有运行记录与结果

真实运行的原始请求、原始响应、响应 ID、Token、延迟、请求/响应哈希和不含凭据的后端元数据保存在 `validation/<run>/evidence.json`；`validation/latest.json` 指向最近一次完整证据。当前仓库内的 [OpenRouter/GPT-5.6-sol 沙箱规范运行](validation/real_20260802T043954Z/evidence.json)使用 839 输入 Token、392 输出 Token、1,231 总 Token，供应商报告成本为 0.015955 美元；确定性提案与真实 LLM 提案均为 `release_to_canary`，且包含 `sandbox_execution` 在内的全部门槛通过。

故障调用均值从基线 3.5 降为 1，临时故障恢复率保持 1.0，旧任务回归数为 0；负对照按预期被拒绝。

确定性补丁只用于可复现对照；真实验收必须包含真实 Coding Agent 的 API 回执。提案分支、失败重放、旧任务回归、灰度和回滚协议不交给生成补丁的模型自行批准。稳定代码、审计日志和发布验证器属于可信根，不在普通自我修改权限之内。

### 检查自己的解释

若模型用“一律不重试”通过了失败用例，还需要什么保留用例才能发现这种退化？
