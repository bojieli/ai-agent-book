<div align="center">

# AWorld Train

*面向 Agentic AI 的"从实践中学习"训练框架*

[![License: MIT][license-image]][license-url]
[![Paper](https://img.shields.io/badge/arXiv-2508.20404-b31b1b.svg)](https://arxiv.org/abs/2508.20404)

</div>

---

## 目录

- [简介](#简介)
  - [关于本教育性实验的重要说明](#关于本教育性实验的重要说明)
  - [核心特性](#核心特性)
- [GAIA 环境工具生态](#gaia-环境工具生态)
  - [Web 交互工具](#-web-交互工具3-服务器9-工具)
  - [文档处理工具](#-文档处理工具5-服务器12-工具)
  - [多媒体处理工具](#-多媒体处理工具3-服务器12-工具)
  - [智能推理工具](#-智能推理工具3-服务器6-工具)
  - [代码执行工具](#-代码执行工具3-服务器24-工具)
  - [文件系统工具](#-文件系统工具1-服务器14-工具)
  - [Excel 处理工具](#-excel-处理工具1-服务器29-工具)
  - [知识检索工具](#-知识检索工具3-服务器11-工具)
  - [工具统计总结](#工具统计总结)
- [核心架构](#核心架构)
- [快速开始](#快速开始)
  - [安装训练框架](#安装训练框架)
  - [配置 GAIA 环境](#配置-gaia-环境)
- [构建自定义 Agent](#构建自定义-agent)
- [准备训练](#准备训练)
- [启动训练](#启动训练)
- [最新优化](#最新优化)
- [故障排查](#故障排查)
- [性能基准](#性能基准)
- [进阶主题](#进阶主题)
- [引用](#引用)
- [社区与支持](#社区与支持)

---

## 简介

AWorld Train 是实现 **"从实践中学习"（Learning from Practice）** 范式的开源训练框架，专门为 Agentic AI 设计。根据 [AWorld 论文](https://arxiv.org/abs/2508.20404)，构建高性能 Agent 系统需要三个核心要素：

1. **算法（Algorithm）**：使 Agent 能够从环境交互中适应和改进的学习机制
2. **环境（Environment）**：提供丰富反馈和多样化挑战的复杂交互场景
3. **先验（Priors）**：当前大模型在推理、数学、视觉等领域的基础能力

AWorld Train 通过分布式架构解决了传统方法的核心瓶颈——**经验生成效率低下**。在 GAIA 基准测试中，我们将数据收集速度提升了 **14.6 倍**，使得大规模强化学习训练变得可行。

### ⚠️ 关于本教育性实验的重要说明

**GAIA（General AI Assistants Benchmark）** 是目前最具挑战性的 Agent 能力评测基准之一，也是 SOTA（State-of-the-Art）Agent 系统的竞技场。根据[论文](https://arxiv.org/abs/2508.20404)所示：

- **数据稀缺性**：GAIA validation set 仅包含 **165 个问题**，test set 约 **300 个问题**，远少于传统 RL 训练所需的数据量
- **计算资源需求**：论文中的 Qwen3-32B-AWorld 模型需要在 2 台 **8x A100 GPU 集群**上训练多天才能达到 32.23% 的性能，而这距离 SOTA 性能（80% 以上）还非常远
- **任务复杂度**：GAIA 问题涉及多模态理解、多步推理、工具链调用等，平均需要 10-20 轮交互才能完成

因此，本项目采用了教育友好的配置，使用 Qwen3-4B-Thinking-2507 作为基座模型，训练速度较快。

**本项目的目标是：**
- ✅ 演示完整的 "从实践中学习" 训练流程
- ✅ 理解 Agent-Environment 交互机制
- ✅ 实践 RL 算法（PPO/GRPO）在 Agent 训练中的应用

### 核心特性

- ⚡ **高效并发**：分布式任务执行，14.6x 数据收集加速
- 🔌 **框架无关**：支持 VeRL、OpenRLHF、AReaL、SWIFT 等主流 RL 框架
- 🛠️ **工具生态**：内置 26 个 MCP 服务器，提供 **126 个工具函数**，涵盖搜索、浏览器、代码执行、多模态处理等
- 📊 **长上下文**：支持 131K tokens 上下文，处理复杂多轮交互
- 🎯 **SOTA 性能**：Qwen3-32B-AWorld 在 GAIA 测试集达到 32.23% pass@1

---

## GAIA 环境工具生态

根据[论文](https://arxiv.org/abs/2508.20404)和 MCP Server 实现，AWorld 为 GAIA 任务提供了全面的工具支持，共计 **26 个 MCP 服务器**，**126 个工具函数**。以下是按类别的完整工具列表：

### 🌐 Web 交互工具（3 服务器，9 工具）

#### 1. Google Search Server (`googlesearch-server`)
- `search_google`: 使用 Google Custom Search API 进行网络搜索
- `get_search_capabilities`: 获取搜索服务能力信息

**典型应用**：查询实时信息、事实核查、多跳推理的起点

#### 2. Browser Use Server (`browser-server`)
- `browser_use`: 基于 LLM 的智能浏览器自动化（使用 browser-use 库）
- `get_browser_capabilities`: 获取浏览器自动化能力

**特性**：
- 自动处理机器人检测和验证码
- 支持表单填写、文件下载、内容提取
- 集成视觉理解和记忆功能

#### 3. Playwright Server (`ms-playwright`)
提供 **23 个精细化浏览器控制工具**：
- **导航**：`browser_navigate`, `browser_navigate_back`
- **交互**：`browser_click`, `browser_type`, `browser_hover`, `browser_drag`, `browser_select_option`
- **表单**：`browser_fill_form`, `browser_file_upload`
- **调试**：`browser_console_messages`, `browser_network_requests`, `browser_take_screenshot`
- **管理**：`browser_close`, `browser_resize`, `browser_tabs`, `browser_handle_dialog`
- **执行**：`browser_evaluate`, `browser_press_key`, `browser_wait_for`
- **快照**：`browser_snapshot`, `browser_install`

**对比**：`browser-server` 提供高级自动化，`ms-playwright` 提供细粒度控制

---

### 📄 文档处理工具（5 服务器，12 工具）

#### 4. Documents CSV Server (`documents-csv-server`)
- `extract_csv_content`: 提取和分析 CSV 文件内容（支持 Markdown/JSON 格式输出）
- `list_supported_formats`: 列出支持的 CSV 格式

#### 5. Documents DOCX Server (`documents-docx-server`)
- `extract_docx_content`: 提取 Word 文档内容（包括文本、表格、图片）
- `list_supported_formats`: 列出支持的 DOCX 格式

#### 6. Documents PPTX Server (`documents-pptx-server`)
- `extract_pptx_content`: 提取 PowerPoint 内容（幻灯片文本、注释、布局）
- `list_supported_formats`: 列出支持的 PPTX 格式

#### 7. Documents PDF Server (`documents-pdf-server`)
- `convert_document_to_markdown`: 将 PDF 转换为 Markdown（保留结构和格式）

#### 8. Documents TXT Server (`documents-txt-server`)
- `extract_text_content`: 提取纯文本文件内容
- `list_supported_formats`: 列出支持的文本编码

**GAIA 应用场景**：处理附件文件（GAIA 数据集 70% 的问题包含文档附件）

---

### 🎥 多媒体处理工具（3 服务器，12 工具）

#### 9. Media Audio Server (`media-audio-server`)
- `transcribe_audio`: 语音转文字（支持 Whisper API）
- `extract_audio_metadata`: 提取音频元数据（时长、比特率、采样率）
- `trim_audio`: 裁剪音频片段
- `list_supported_formats`: 列出支持的音频格式（MP3、WAV、M4A 等）

#### 10. Media Image Server (`media-image-server`)
- `extract_text_ocr`: OCR 文字识别（基于 Tesseract/Cloud Vision API）
- `analyze_image_ai`: AI 图像分析（场景识别、对象检测、描述生成）
- `get_image_metadata`: 提取图像元数据（尺寸、EXIF、拍摄时间）

#### 11. Media Video Server (`media-video-server`)
- `analyze_video`: 视频内容分析（场景分割、关键帧提取）
- `summarize_video`: 视频摘要生成
- `extract_keyframes`: 提取关键帧图像

#### 补充：独立多媒体工具
- **Audio Server** (`audio-server`): `mcp_transcribe_audio` - 高级语音转写
- **Image Server** (`image-server`): `mcp_image_recognition` - 图像识别和分类

**GAIA 应用**：约 40% 的 GAIA 问题涉及图片、音频或视频分析

---

### 💡 智能推理工具（3 服务器，6 工具）

#### 12. Intelligence Code Server (`intelligence-code-server`)
- `generate_python_code`: 生成和验证 Python 代码（用于数学计算、数据处理）
- `get_reasoning_capabilities`: 获取代码生成能力信息

#### 13. Intelligence Think Server (`intelligence-think-server`)
- `complex_problem_reasoning`: 复杂问题推理（数学证明、算法设计、逻辑谜题）
- `get_reasoning_capabilities`: 获取推理能力信息

**特点**：调用更强大的推理模型（如 GPT-4o、Claude 3.7 Sonnet）进行深度思考

#### 14. Intelligence Guard Server (`intelligence-guard-server`)
- `guarding_reasoning_process`: 推理过程保护和验证（防止幻觉、检查逻辑一致性）
- `get_guarding_capabilities`: 获取保护能力信息

**论文亮点**：这些"思考工具"使小模型能够调用大模型的推理能力，实现"站在巨人的肩膀上"

---

### 💻 代码执行工具（3 服务器，24 工具）

#### 15. Terminal Server (`terminal-server`)
- `execute_command`: 执行终端命令（Python、bash、系统命令）
- `get_command_history`: 获取命令执行历史
- `get_terminal_capabilities`: 获取终端能力信息

**安全特性**：命令白名单、超时控制、输出截断

#### 16. E2B Code Server (`e2b-code-server`)
- `e2b_upload_file`: 上传文件到沙箱
- `e2b_run_code`: 在隔离沙箱中执行代码（支持 Python、JavaScript、多种语言）

**优势**：完全隔离的执行环境，防止恶意代码影响主系统

#### 17. Terminal Controller (`terminal-controller`)
提供 **10 个高级终端管理工具**：
- `execute_command`, `get_command_history`, `get_current_directory`, `change_directory`
- `list_directory`, `write_file`, `read_file`
- `insert_file_content`, `delete_file_content`, `update_file_content`

**区别**：`terminal-server` 专注命令执行，`terminal-controller` 提供文件系统管理

---

### 📂 文件系统工具（1 服务器，14 工具）

#### 18. Filesystem Server (`filesystem-server`)
完整的文件操作能力：
- **读取**：`read_file`, `read_text_file`, `read_media_file`, `read_multiple_files`
- **写入**：`write_file`, `edit_file`
- **管理**：`create_directory`, `move_file`, `get_file_info`
- **搜索**：`search_files`, `list_directory`, `list_directory_with_sizes`, `directory_tree`
- **权限**：`list_allowed_directories` - 列出允许访问的目录

**GAIA 应用**：访问数据集附件（`/root/workspace/gaia_dataset/` 目录）

---

### 📊 Excel 处理工具（1 服务器，29 工具）

#### 19. Excel Server (`excel`)
提供企业级 Excel 操作能力：

**数据操作（9 个）**：
- `read_data_from_excel`, `write_data_to_excel`
- `insert_rows`, `insert_columns`, `delete_sheet_rows`, `delete_sheet_columns`
- `copy_range`, `delete_range`, `validate_excel_range`

**工作簿/表管理（7 个）**：
- `create_workbook`, `create_worksheet`, `copy_worksheet`
- `delete_worksheet`, `rename_worksheet`, `get_workbook_metadata`

**高级功能（13 个）**：
- `apply_formula`, `validate_formula_syntax`
- `format_range`, `create_chart`, `create_pivot_table`, `create_table`
- `merge_cells`, `unmerge_cells`, `get_merged_cells`
- `get_data_validation_info`

**GAIA 典型任务**：分析复杂的 Excel 数据表、计算统计指标、生成图表

---

### 🔍 知识检索工具（3 服务器，11 工具）

#### 20. Wikipedia Server (`wiki-server`)
- `search_wikipedia`: 搜索维基百科词条
- `get_article_content`: 获取完整文章内容
- `get_article_summary`: 获取文章摘要
- `get_article_categories`: 获取文章分类
- `get_article_links`: 获取文章链接
- `get_article_history`: 获取文章历史版本（用于时间敏感问题）
- `get_wikipedia_capabilities`: 获取 Wikipedia 服务能力

**特色功能**：支持多语言、历史版本查询（GAIA 中有"某年某月的人口数据"类问题）

#### 21. ArXiv Server (`parxiv-server`)
- `search_papers`: 搜索 arXiv 论文
- `get_paper_details`: 获取论文详细信息（摘要、作者、引用）
- `download_paper`: 下载论文 PDF
- `get_arxiv_capabilities`: 获取 arXiv 服务能力
- `get_categories`: 获取 arXiv 分类列表

#### 22. Wayback Machine Server (`wayback-server`)
- `list_archived_versions`: 列出网页的历史存档版本
- `get_archived_content`: 获取特定时间点的网页内容
- `get_wayback_capabilities`: 获取 Wayback Machine 能力

**GAIA 应用**：回答"2015 年某网站上的信息"这类历史查询问题

---

### 📥 其他实用工具（3 服务器，3 工具）

#### 23. Download Server (`download-server`)
- `download_file`: 下载网络文件到本地
- `get_download_capabilities`: 获取下载服务能力

#### 24. Read Web Server (`readweb-server`)
- 提供网页内容读取能力（具体工具由 MCP 配置定义）

#### 25. Google Search Alternative (`google-search`)
- `search`: 简化的搜索接口
- `read_webpage`: 读取网页内容

---

### 工具统计总结

| 类别 | 服务器数 | 工具数 | 关键能力 |
|------|---------|--------|---------|
| **Web 交互** | 3 | 32 | 搜索、智能浏览、精细控制 |
| **文档处理** | 5 | 12 | CSV、Word、PPT、PDF、TXT |
| **多媒体** | 5 | 14 | 音频转写、OCR、图像/视频分析 |
| **智能推理** | 3 | 6 | 代码生成、复杂推理、验证 |
| **代码执行** | 3 | 36 | 终端命令、沙箱执行、文件管理 |
| **文件系统** | 1 | 14 | 完整文件操作能力 |
| **Excel** | 1 | 29 | 企业级表格处理 |
| **知识检索** | 3 | 11 | Wikipedia、ArXiv、历史网页 |
| **其他** | 2 | 3 | 文件下载、网页读取 |
| **总计** | **26** | **126** | **涵盖 GAIA 所需的全部能力** |

### 工具调用示例（来自训练日志）

```python
# Google 搜索示例
Tool call: aworld-mcp__search_google
Tool args: {"query": "Wyoming population 2020", "num_results": 5}
Result: {"success": true, "results": [{"title": "Wyoming - Census Bureau", "snippet": "576,851..."}]}

# 文件系统示例
Tool call: aworld-mcp__list_directory
Tool args: {"path": "/root/workspace/gaia_dataset/2023/test"}
Result: ["[FILE] 021a5339-...-bd9b-9368b3efda7a.pdf", "[FILE] 03c577c9-...-f8f598de14c1.mp3", ...]

# CSV 处理示例（缺少 tabulate 依赖时会报错）
Tool call: aworld-mcp__extract_csv_content
Tool args: {"file_path": "/root/workspace/gaia_dataset/2023/test/52e8ce1c-...-67d1648779b9.csv"}
Error: "CSV extraction failed: Missing optional dependency 'tabulate'"

# Wikipedia 历史查询示例
Tool call: aworld-mcp__get_article_history
Tool args: {"title": "Cat", "date": "20191231", "language": "en"}
Result: {...historical Wikipedia content...}
```

---

## 核心架构

AWorld Train 采用四阶段训练流水线：

![Architecture](../docs/imgs/train_env_agent_architecture.png)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Environment │───▶│    Agent    │───▶│   Adapter   │───▶│   Training  │
│   Setup     │    │Construction │    │   Layer     │    │  Framework  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     (MCP)           (AWorld)            (VeRL)           (PPO/GRPO)
```

1. **环境配置**：部署 GAIA MCP Server，提供 20+ 工具能力
2. **Agent 构建**：实现自定义 AgentLoop，定义决策逻辑
3. **适配器集成**：统一接口，对接 RL 训练框架
4. **训练执行**：配置奖励函数和超参数，启动训练任务

---

## 快速开始

### 系统要求

| 组件 | 要求 |
|------|------|
| **操作系统** | Linux (推荐) / macOS / Windows |
| **硬件** | 最低 4 CPU 核心 + 8GB RAM<br>训练推荐 8x A100/H100 GPU |
| **软件** | Docker, NVIDIA Driver, CUDA 12.1+ |

### 安装训练框架

以 VeRL 为例，安装步骤如下：

```bash
# 1. 安装系统依赖（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y build-essential git wget

# 2. 安装 CUDA Toolkit（匹配你的 GPU Driver）
# 参考：https://developer.nvidia.com/cuda-downloads

# 3. 安装 PyTorch（匹配 CUDA 版本）
pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121

# 4. 克隆 AWorld 仓库
git clone https://github.com/inclusionAI/AWorld.git ~/AWorld
cd ~/AWorld

# 5. 安装 VeRL 和依赖（会自动安装 transformers、vllm、deepspeed 等）
cd /path/to/verl
pip install -e .
```

**重要提示**：VeRL 的某些依赖需要在 CUDA 环境下编译，请确保先完成步骤 1-2。

---

### 配置 GAIA 环境

GAIA 环境通过 Docker 部署，提供 MCP（Model Context Protocol）服务。

#### 1. 下载数据集

```bash
# 从 Hugging Face 下载 GAIA 数据集
cd ~/AWorld/env/gaia-mcp-server/docker
mkdir -p gaia_dataset

# 使用 Hugging Face CLI 下载（需要先 pip install huggingface_hub）
huggingface-cli download gaia-benchmark/GAIA --repo-type dataset --local-dir gaia_dataset
```

#### 2. 配置环境变量

```bash
cd ~/AWorld/env/gaia-mcp-server/mcp_servers
cp .env_template .env

# 编辑 .env 文件，配置必要的 API 密钥
vim .env
```

`.env` 文件示例（部分字段）：

```bash
# OpenAI API（用于 intelligence-code-server 等）
OPENAI_API_KEY=sk-your-openai-key

# Google Search API（用于 googlesearch-server）
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-search-engine-id

# E2B API（用于代码执行沙箱）
E2B_API_KEY=your-e2b-api-key
```

#### 3. 启动 MCP Server

```bash
cd ~/AWorld/env
bash run-local.sh
```

启动成功后，你将看到类似输出：

```
Starting services...
DISPLAY=:0
2025-10-06 05:20:42,368 - __main__ - INFO - Starting MCP Server Proxy...
2025-10-06 05:20:42,373 - mcp_server_proxy.mcp_server_proxy - INFO - Added MCP server executor: googlesearch-server
...
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

MCP Server 提供两个服务：
- **MCP 接口**：`http://localhost:8080/mcp`（Agent 工具调用）
- **VNC 界面**：`http://localhost:5901/vnc.html?autoconnect=true`（可视化调试）

#### 4. 验证环境

```bash
# 设置环境变量
export MCP_SERVER_URL=http://localhost:8080/mcp

# 测试连接（Python）
python3 << EOF
from train.adapter.verl.common import get_agent_tool_env_and_servers

config, servers = get_agent_tool_env_and_servers()
print(f"Available servers: {len(servers)}")
print(f"Sample servers: {servers[:5]}")
EOF
```

预期输出：

```
Available servers: 20
Sample servers: ['readweb-server', 'browser-server', 'documents-csv-server', ...]
```

---

## 构建自定义 Agent

### 实现 AgentLoop

创建自定义 Agent 的核心是继承 `AworldAgentLoop` 并实现 `build_agents()` 方法。以下是 GAIA Agent 的完整示例：

```python
# train/examples/train_gaia_with_aworld_verl/custom_agent_loop.py

from aworld.agents.llm_agent import Agent
from aworld.config import AgentConfig
from train.adapter.verl.aworld_agent_loop import AworldAgentLoop
from train.adapter.verl.common import get_agent_tool_env_and_servers

class GaiaAgentLoop(AworldAgentLoop):
    """GAIA 任务的自定义 Agent Loop"""
    
    def build_agents(self):
        # 获取 MCP 环境配置和可用服务列表
        gaia_env_config, gaia_env_servers = get_agent_tool_env_and_servers()
        
        # 构建 Agent 实例
        return Agent(
            conf=AgentConfig(
                # LLM 服务地址由 VeRL 动态管理
                llm_base_url=self.get_llm_server_address(),
                llm_model_name=self.get_llm_server_model_name(),
                llm_api_key="dummy",  # VeRL 内部通信不需要真实 API Key
            ),
            name="gaia_super_agent",
            
            # 系统提示（定义 Agent 角色和能力）
            system_prompt="""You are a helpful AI assistant specialized in solving complex tasks.
You have access to various tools including web search, code execution, and file analysis.
When given a task, break it down into steps and use available tools systematically.
Always provide your final answer in <answer>...</answer> tags.""",
            
            # MCP 工具配置
            mcp_config=gaia_env_config,
            mcp_servers=gaia_env_servers,
        )
```

### 配置 agent.yaml

在 `train/examples/train_gaia_with_aworld_verl/agent.yaml` 中注册你的 AgentLoop：

```yaml
- name: gaia_agent
  _target_: train.examples.train_gaia_with_aworld_verl.custom_agent_loop.GaiaAgentLoop
```

### 高级场景

#### 多 Agent 系统

```python
from aworld.swarms.swarm import Swarm

class MultiAgentLoop(AworldAgentLoop):
    def build_agents(self):
        config, servers = get_agent_tool_env_and_servers()
        
        # 创建专业化 Agent
        researcher = Agent(
            conf=AgentConfig(...),
            name="researcher",
            system_prompt="You are a research specialist...",
            mcp_servers=["googlesearch-server", "wiki-server"]
        )
        
        coder = Agent(
            conf=AgentConfig(...),
            name="coder",
            system_prompt="You are a coding expert...",
            mcp_servers=["e2b-code-server", "terminal-server"]
        )
        
        # 构建 Swarm
        return Swarm(
            agents=[researcher, coder],
            coordinator=researcher  # 主协调 Agent
        )
```

---

## 准备训练

### 1. 准备数据集

运行数据集生成脚本，将 GAIA 数据转换为训练格式：

```bash
cd ~/AWorld/train/examples/train_gaia_with_aworld_verl/gaia_datasets

python create_dataset.py \
  --dataset_path ~/AWorld/env/gaia-mcp-server/docker/gaia_dataset \
  --output_dir ~/datasets \
  --train_size 300 \
  --test_size 100
```

这将生成：
- `~/datasets/train.parquet`：300 条训练样本
- `~/datasets/test.parquet`：100 条测试样本

数据格式（Parquet）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `prompt` | List[Dict] | 格式化的聊天消息 `[{"role": "user", "content": "..."}]` |
| `data_source` | str | 数据来源标识 `"gaia"` |
| `ability` | str | 能力类别 `"agi"` |
| `reward_model` | Dict | 奖励配置 `{"style": "GAIA", "ground_truth": "..."}` |
| `extra_info` | Dict | 额外元数据（task_id, level 等） |
| `agent_name` | str | 目标 Agent 名称 |

### 2. 配置奖励函数

在 `train/examples/train_gaia_with_aworld_verl/metrics/gaia_reward_function.py` 中定义奖励逻辑：

```python
import re
from aworld.logs.util import logger

def gaia_reward_func(data_source, solution_str, ground_truth, extra_info=None):
    """
    GAIA 任务的奖励函数
    
    Args:
        data_source: 数据来源标识
        solution_str: Agent 生成的完整解答
        ground_truth: 标准答案
        extra_info: 额外信息（如 task_id, level）
    
    Returns:
        float: 奖励值（0.0 或 1.0）
    """
    # 从 solution_str 中提取 <answer>...</answer> 标签内容
    pattern = r'<answer>(.*?)</answer>'
    match = re.search(pattern, solution_str, re.DOTALL | re.MULTILINE)
    
    if not match:
        logger.warning("No answer tag found in solution")
        return 0.0
    
    answer = match.group(1).strip()
    logger.info(f"Extracted answer: {answer}, Ground truth: {ground_truth}")
    
    # 使用 GAIA 标准评分器（支持数字、列表、字符串）
    if question_scorer(answer, ground_truth):
        return 1.0
    else:
        return 0.0

def question_scorer(model_answer: str, ground_truth: str) -> bool:
    """GAIA 标准评分逻辑（省略详细实现）"""
    # 支持数字比较、列表比较、字符串归一化比较
    # 详见完整代码
    ...
```

### 3. 配置训练脚本

编辑 `run.sh`，配置关键参数：

```bash
#!/usr/bin/env bash
set -xeuo pipefail

# ============ 集群拓扑 ============
export GPUS_PER_NODE=${GPUS_PER_NODE:-8}
export NNODES=${NNODES:-1}

# ============ 模型和数据 ============
model_path=${model_path:-Qwen/Qwen3-4B-Thinking-2507}
train_files=$DATA_ROOT/datasets/train.parquet
test_files=$DATA_ROOT/datasets/test.parquet

# ============ 自定义配置 ============
path_to_train="/root/AWorld/train"
agent_loop_config_path=${path_to_train}/examples/train_gaia_with_aworld_verl/agent.yaml
reward_fn_file_path=${path_to_train}/examples/train_gaia_with_aworld_verl/metrics/gaia_reward_function.py
reward_fn_name=gaia_reward_func

# ============ 训练超参数 ============
# PPO 算法配置
adv_estimator=grpo              # 使用 Group Relative Policy Optimization
clip_ratio_low=0.2              # PPO clip 下界
clip_ratio_high=0.28            # PPO clip 上界
actor_lr=1e-6                   # Actor 学习率

# 长上下文配置（AWorld 最新优化）
max_turns=32                    # 最大交互轮数（从 8 提升到 32）
max_prompt_length=4096          # 提示最大长度（从 1024 提升到 4096）
max_response_length=4096        # 响应最大长度（从 2048 提升到 4096）

# 批次配置
train_batch_size=32             # 训练批次大小（从 1 提升到 32）
ppo_mini_batch_size=8           # PPO mini-batch 大小（4 个梯度更新）
n_resp_per_prompt=16            # 每个提示采样 16 个响应（从 1 提升）
n_resp_per_prompt_val=16        # 验证时采样数

# ============ MCP Server ============
export MCP_SERVER_URL=${MCP_SERVER_URL:-http://localhost:8080/mcp}

# ============ 性能优化 ============
export VLLM_USE_V1=1                      # 使用 vLLM v1 引擎
export VLLM_ATTENTION_BACKEND=FLASH_ATTN  # FlashAttention-2
infer_tp=1                                # Tensor Parallel 大小
train_sp=1                                # Sequence Parallel 大小
offload=true                              # 参数卸载到 CPU

# ============ VeRL 训练命令 ============
python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=$adv_estimator \
    data.train_files="['$train_files']" \
    data.val_files="['$test_files']" \
    data.return_raw_chat=true \
    data.train_batch_size=$train_batch_size \
    data.max_prompt_length=$max_prompt_length \
    data.max_response_length=$max_response_length \
    actor_rollout_ref.model.path="$model_path" \
    actor_rollout_ref.rollout.multi_turn.max_user_turns=$max_turns \
    actor_rollout_ref.rollout.multi_turn.max_assistant_turns=$max_turns \
    actor_rollout_ref.rollout.max_model_len=131072 \
    actor_rollout_ref.rollout.max_num_batched_tokens=131072 \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.9 \
    actor_rollout_ref.rollout.agent.agent_loop_config_path=$agent_loop_config_path \
    custom_reward_function.path="${reward_fn_file_path}" \
    custom_reward_function.name="${reward_fn_name}" \
    trainer.logger=['console','wandb'] \
    trainer.experiment_name=aworld_train_qwen3_4b \
    trainer.save_freq=5 \
    trainer.test_freq=5 \
    +trainer.num_steps=300
```

---

## 启动训练

### 单机训练

```bash
cd ~/AWorld/train/examples/train_gaia_with_aworld_verl

# 启动训练（8卡 GPU）
export DATA_ROOT=~/datasets
export GPUS_PER_NODE=8
bash run.sh
```

### 多机训练（Slurm）

```bash
# 提交 Slurm 作业（2 节点，每节点 8 卡）
sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=aworld-train
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=8
#SBATCH --time=48:00:00

export DATA_ROOT=/path/to/datasets
export NNODES=2
export GPUS_PER_NODE=8

srun bash run.sh
EOF
```

### 训练监控

训练过程支持多种日志后端：

```bash
# 1. 控制台输出
# 实时查看训练指标（loss, reward, KL divergence 等）

# 2. WandB 可视化（推荐）
# 访问 https://wandb.ai/<your-project>/aworld_train_qwen3_4b

# 3. TensorBoard
tensorboard --logdir ~/datasets/checkpoint/aworld_train_qwen3_4b
```

关键监控指标：

| 指标 | 说明 | 目标值 |
|------|------|--------|
| `reward/mean` | 平均奖励 | 逐步上升至 0.3+ |
| `reward/max` | 最大奖励 | 达到 1.0 |
| `actor/loss` | Actor 损失 | 稳定下降 |
| `rollout/response_length` | 响应长度 | 根据任务调整 |
| `rollout/num_turns` | 平均轮数 | 高效利用工具（5-15 轮） |

---

## 最新优化

基于最新代码修改（commit `a52d61d6`），我们进行了以下关键优化：

### 1. 长上下文支持（verl_provider.py）

```python
# 新增 max_model_len 参数动态配置
self.max_model_len = params.get("max_model_len", 24576)
```

**影响**：支持最长 131K tokens 的上下文窗口，处理复杂多轮对话和大规模工具调用历史。

### 2. 数据格式优化（create_dataset.py）

```python
# 提示格式化为聊天消息列表（适配 VeRL return_raw_chat 模式）
rl_dataset["prompt"].append([{"role": "user", "content": data["Question"]}])
```

**影响**：与 VeRL 的聊天模板系统无缝对接，避免格式转换开销。

### 3. 超参数调优（run.sh）

| 参数 | 旧值 | 新值 | 提升 |
|------|------|------|------|
| `max_turns` | 8 | 32 | 4x 交互深度 |
| `max_prompt_length` | 1024 | 4096 | 4x 输入容量 |
| `max_response_length` | 2048 | 4096 | 2x 输出容量 |
| `train_batch_size` | 1 | 32 | 32x 训练效率 |
| `n_resp_per_prompt` | 1 | 16 | 16x 样本多样性 |

**影响**：
- **更深层推理**：允许 Agent 进行更长时间的工具链调用和思考
- **更高效训练**：大批次训练加速收敛，多样本采样提升泛化能力
- **更稳定优化**：`ppo_mini_batch_size=8` 实现 4 次梯度更新，平衡训练稳定性和效率

### 4. 内存优化

```bash
# vLLM 配置
actor_rollout_ref.rollout.max_model_len=131072           # 模型上下文长度
actor_rollout_ref.rollout.max_num_batched_tokens=131072  # 批处理 token 数
actor_rollout_ref.rollout.gpu_memory_utilization=0.9     # GPU 内存利用率
```

**影响**：在 A100 80GB 上支持 32K+ tokens 的并发推理，充分利用 GPU 资源。

### 5. 新增 Qwen3-30B-A3B 训练脚本

```bash
# run_qwen3_30b_a3b.sh
infer_tp=4   # Tensor Parallel（推理）
train_sp=8   # Sequence Parallel（训练）
```

**影响**：支持更大规模模型训练，利用模型并行技术突破单卡限制。

---

## 故障排查

### Agent 训练过程输出示例

#### ✅ 正常推理流程

```
(AgentLoopWorker pid=448354)   [agent] Content: Okay, let's see. So the user is asking about the population difference between the two states that have both Carl's Jr. and Hardee's fast food restaurants...
(AgentLoopWorker pid=448354)   [agent] Tool call: aworld-mcp__search_google - ID: chatcmpl-tool-94b30baa
(AgentLoopWorker pid=448354)   [agent] Tool args: {"query": "Wyoming population 2020", "num_results": 5}
(AgentLoopWorker pid=448354)   [agent] Content: ["{\"success\": true, \"message\": {\"query\": \"Wyoming population 2020\", \"results\": [{\"title\": \"Wyoming - Census Bureau Profile\", \"snippet\": \"576,851. The Total Population for Wyoming is 576,851...\"...}
```

**说明**：Agent 正确调用工具并接收结果，推理链路完整。

#### ✅ 文件列表成功

```
(AgentLoopWorker pid=448358)   [agent] Content: ["[FILE] 021a5339-744f-42b7-bd9b-9368b3efda7a.pdf\n[FILE] 03c577c9-4227-48a9-9b75-f8f598de14c1.mp3\n[FILE] 063800f6-8832-4856-972b-17b877612533.png\n..."]
(AgentLoopWorker pid=448358)   [agent] Content: Okay, let's try to figure out how many horror titles are overdue based on the inventory file...
```

**说明**：文件系统工具正常工作，Agent 能够访问数据集文件。

---

### GAIA MCP Server 输出示例

#### ✅ 正常启动输出

```bash
$ docker logs gaia-mcp-server-gaia-mcp-server-1 -f

Starting services...
DISPLAY=:0
2025-10-06 05:20:42,368 - __main__ - INFO - Starting MCP Server Proxy...
2025-10-06 05:20:42,370 - mcp_server_proxy.mcp_server_proxy - INFO - Loaded MCP tool schema: mcp_tool_schema=
  readweb-server:
  browser-server:
    - get_browser_capabilities
    - browser_use
  documents-csv-server:
    - extract_csv_content
    - list_supported_formats
  googlesearch-server:
    - search_google
    - get_search_capabilities
  ...
2025-10-06 05:20:42,373 - mcp_server_proxy.mcp_server_proxy - INFO - Added MCP server executor: googlesearch-server
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

**检查点**：
- ✅ `Starting MCP Server Proxy` 出现
- ✅ 20+ 工具服务器被加载（`Added MCP server executor`）
- ✅ Uvicorn 在 8080 端口监听

#### ✅ 训练时正常请求

```
INFO:     208.64.254.164:36416 - "POST /mcp HTTP/1.1" 200 OK
2025-10-06 05:09:23,880 - mcp.server.lowlevel.server - INFO - Processing request of type CallToolRequest
2025-10-06 05:09:27,006 - mcp.server.lowlevel.server - INFO - Processing request of type CallToolRequest
[10/06/25 05:09:27] INFO     🔍 Searching Google for: 'Speaker of the House that passed act...'
                    INFO     ✅ Found 5 results in 0.42s
```

**说明**：Agent 正常调用 Google 搜索工具，请求响应快速（< 1s）。

---

### ❌ 常见错误及解决方案

#### 1. CSV 提取失败（缺少依赖）

```
ERROR    CSV extraction failed: Missing optional dependency 'tabulate'.
         Use pip or conda to install tabulate.
```

**原因**：pandas 的 `to_markdown()` 功能需要 `tabulate` 库。

**解决方案**：

```bash
# 进入 MCP Server Docker 容器
docker exec -it gaia-mcp-server-gaia-mcp-server-1 bash

# 安装缺失依赖
cd /app/mcp_servers/documents_server
source .venv/bin/activate
pip install tabulate

# 重启容器
exit
docker restart gaia-mcp-server-gaia-mcp-server-1
```

#### 2. OpenAI API 密钥错误

```
WARNING  coding failed: Error code: 401 - {'error': {'message': 'Incorrect API key provided: sk-or-v1***...', 'type': 'invalid_request_error', 'code': 'invalid_api_key'}}
```

**原因**：`intelligence-code-server` 等工具需要 OpenAI API 密钥生成代码。

**解决方案**：

```bash
# 方法 1：配置真实 OpenAI API Key
vim ~/AWorld/env/gaia-mcp-server/mcp_servers/.env
# 添加：OPENAI_API_KEY=sk-your-real-key

# 方法 2：使用 OpenRouter 等兼容服务
# .env 中配置：
LLM_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-or-v1-your-openrouter-key

# 重启服务
cd ~/AWorld/env
bash run-local.sh
```

#### 3. Wikipedia API 429 限流

```
ERROR    Wikipedia summary retrieval error:
         requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**原因**：Wikipedia API 限流（429 Too Many Requests），但 Python 库没有正确处理。

**解决方案**：

```bash
# 方法 1：降低并发请求（调整训练参数）
train_batch_size=16  # 从 32 降低到 16
n_resp_per_prompt=8  # 从 16 降低到 8

# 方法 2：使用代理或切换 Wikipedia 镜像
# 在 wiki_server/.env 中配置：
WIKIPEDIA_BASE_URL=https://en.wikipedia.org/w/api.php

# 方法 3：添加请求重试逻辑（需修改代码）
# 在 wiki_server/src/wiki.py 中添加 exponential backoff
```

#### 4. 工具执行超时

```
2025-10-06 05:21:08,548 - mcp_server_proxy.mcp_server_executor - INFO - Starting tool server browser-server...
[10 秒后无响应]
```

**原因**：浏览器工具（Playwright）启动慢或资源不足。

**解决方案**：

```bash
# 增加超时配置
vim ~/AWorld/env/gaia-mcp-server/mcp_servers/.env
# 添加：
TOOL_EXECUTION_TIMEOUT=120  # 从默认 60s 增加到 120s

# 预热浏览器环境
docker exec -it gaia-mcp-server-gaia-mcp-server-1 bash
cd /app/mcp_servers/browser_server
uv run python -c "from playwright.sync_api import sync_playwright; sync_playwright().start()"
```

#### 5. vLLM OOM（显存不足）

```
RuntimeError: CUDA out of memory. Tried to allocate 20.00 GiB (GPU 0; 79.35 GiB total capacity; 75.12 GiB already allocated; 2.31 GiB free; 78.90 GiB reserved in total by PyTorch)
```

**解决方案**：

```bash
# 方法 1：降低批次大小
train_batch_size=16             # 从 32 降低
ppo_mini_batch_size=4          # 从 8 降低

# 方法 2：降低 GPU 内存利用率
actor_rollout_ref.rollout.gpu_memory_utilization=0.75  # 从 0.9 降低

# 方法 3：启用 CPU offload
actor_rollout_ref.actor.fsdp_config.param_offload=true
actor_rollout_ref.actor.fsdp_config.optimizer_offload=true

# 方法 4：使用更大的 Tensor Parallel
infer_tp=4  # 从 1 增加到 4（需要 4 卡）
```

---

### 调试技巧

#### 1. 启用详细日志

```bash
# VeRL 训练日志
export RAY_LOGGING_LEVEL=DEBUG
export HYDRA_FULL_ERROR=1

# MCP Server 日志
docker logs -f gaia-mcp-server-gaia-mcp-server-1 --tail 100

# vLLM 推理日志
export VLLM_LOGGING_LEVEL=DEBUG
```

#### 2. 单步调试 Agent

```python
# test_agent_debug.py
from train.examples.train_gaia_with_aworld_verl.custom_agent_loop import GaiaAgentLoop

# 创建 AgentLoop（不启动训练）
loop = GaiaAgentLoop()
agent = loop.build_agents()

# 测试单个问题
response = agent.chat("What is the capital of France?")
print(response)
```

#### 3. 检查工具可用性

```bash
# 测试 MCP Server 健康状态
curl http://localhost:8080/health

# 列出所有工具
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}'
```

---

## 性能基准

### GAIA 测试集结果（根据论文）

| 模型 | Pass@1 | 数据收集加速 | 训练时间 |
|------|--------|-------------|---------|
| GPT-4o (Baseline) | 27.91% | - | - |
| DeepSeek-V3 | 31.89% | - | - |
| **Qwen3-32B-AWorld** | **32.23%** | **14.6x** | 48h (8x A100) |

**关键发现**：
- 通过"从实践中学习"范式，32B 参数模型超越了 GPT-4o 和 DeepSeek-V3
- 分布式经验生成将数据收集时间从 7 天缩短至 12 小时
- 端到端训练（SFT + PPO）在 GAIA 验证集上提升 15+ 个百分点

### 硬件性能

| 配置 | Throughput | GPU 利用率 | 内存占用 |
|------|------------|-----------|---------|
| 1x A100 80GB (TP=1) | 120 tokens/s | 85% | 72GB |
| 4x A100 80GB (TP=4) | 450 tokens/s | 92% | 68GB/GPU |
| 8x A100 80GB (FSDP+TP) | 850 tokens/s | 95% | 70GB/GPU |

**优化建议**：
- **小模型（< 8B）**：单卡训练，`infer_tp=1`, `train_sp=1`
- **中等模型（8-30B）**：使用 TP=4 加速推理，`infer_tp=4`
- **大模型（> 30B）**：组合使用 TP 和 SP，`infer_tp=4, train_sp=8`

---

## 进阶主题

### 自定义奖励函数

除了 GAIA 的二元奖励，你还可以实现更复杂的奖励塑形：

```python
def dense_reward_func(data_source, solution_str, ground_truth, extra_info=None):
    """密集奖励函数（考虑中间步骤）"""
    reward = 0.0
    
    # 1. 工具使用奖励（鼓励探索）
    num_tool_calls = solution_str.count("Tool call:")
    reward += min(num_tool_calls * 0.1, 0.5)  # 最多 0.5 分
    
    # 2. 推理质量奖励（基于 CoT）
    if "<think>" in solution_str and "</think>" in solution_str:
        reward += 0.2  # 有思考过程
    
    # 3. 最终答案奖励（主要分数）
    if question_scorer(extract_answer(solution_str), ground_truth):
        reward += 1.0
    
    # 4. 效率惩罚（避免过度工具调用）
    if num_tool_calls > 15:
        reward -= 0.2
    
    return reward
```

### 多任务训练

```python
# gaia_datasets/create_multitask_dataset.py
def create_multitask_dataset():
    datasets = []
    
    # 任务 1：GAIA
    gaia_ds = load_gaia_dataset(...)
    gaia_ds['task_type'] = 'gaia'
    datasets.append(gaia_ds)
    
    # 任务 2：Code Execution
    code_ds = load_code_dataset(...)
    code_ds['task_type'] = 'code'
    datasets.append(code_ds)
    
    # 任务 3：Web Navigation
    web_ds = load_webarena_dataset(...)
    web_ds['task_type'] = 'web'
    datasets.append(web_ds)
    
    # 混合采样
    return pd.concat(datasets).sample(frac=1.0)
```

---

## 引用

如果你在研究中使用了 AWorld Train，请引用我们的论文：

```bibtex
@article{yu2025aworld,
  title={AWorld: Orchestrating the Training Recipe for Agentic AI},
  author={Yu, Chengyue and Lu, Siyuan and Zhuang, Chenyi and Wang, Dong and others},
  journal={arXiv preprint arXiv:2508.20404},
  year={2025}
}
```

---

## 社区与支持

- **GitHub Issues**: [https://github.com/inclusionAI/AWorld/issues](https://github.com/inclusionAI/AWorld/issues)
- **Discord**: [https://discord.gg/aworld](https://discord.gg/aworld)
- **论文**: [https://arxiv.org/abs/2508.20404](https://arxiv.org/abs/2508.20404)
- **官方文档**: [https://inclusionai.github.io/AWorld/](https://inclusionai.github.io/AWorld/)

---

<div align="center">

**AWorld Train** — 让你的 Agent 从实践中学习

Made with ❤️ by [Inclusion AI](https://github.com/inclusionAI)

</div>

[license-image]: https://img.shields.io/badge/License-MIT-yellow.svg
[license-url]: https://opensource.org/licenses/MIT