# 第 3 章 · 用户记忆和知识库

用户问“我的车约了哪些保养”，助理找到了本田的预约。它还需要查特斯拉吗？本章从两个问题入手：一条相关记录怎样进入检索结果，助理又怎样知道手头的记录够不够回答用户。

[返回主目录](../README.md) · [读第三章正文](../book/chapter3.md)

## 第一次做实验

1. 先在[实验 3-5](sparse-embedding/README.md)搜 `HTTP 404 error`。读返回的两篇文档，找出各自匹配了哪个词，再判断哪篇真正回答了问题。
2. 到[实验 3-6](retrieval-pipeline/README.md)查“植物如何把阳光转化为食物”。融合后的第一名在重排后降到了第三名。想追查是哪一步改变了次序，可以从 [RetrievalPipeline.search](retrieval-pipeline/retrieval_pipeline.py) 沿调用读到[融合函数](retrieval-pipeline/fusion.py)和[重排方法](retrieval-pipeline/reranker.py)。
3. 回到车辆保养问题，打开[实验 3-11](contextual-retrieval-for-user-memory/README.md)的三份回答。核对哪些回答说清了本田已预约、特斯拉只询过价。要看助理怎样在下次对话前准备这些事实，再做[用户记忆实验](user-memory/README.md)，顺着[对话程序](user-memory/conversational_agent.py)和[后台记忆处理程序](user-memory/background_memory_processor.py)读一次写入过程。

复查一个漏答时，先找原始对话，再看从中提取的事实、时间与来源，最后核对回答时取回的片段。索引可以重建，用户实际说过的话仍要回到对话记录里查。各实验使用哪批数据、按什么标准验收，以及到哪里查运行记录，见[实验记录索引](EXPERIMENT_LEDGER.md)。

## 配套项目

| 编号 | 项目 | 类型 | 一句话说明 |
| :--: | --- | :--: | --- |
| 3-1, 3-2 | [user-memory](user-memory/) | ✅ | 四种格式在同一组 60 个用例上的[运行记录](user-memory/validation/runs/20260730T043652Z-3_1_and_3_2-16200e94/evidence.json)，含记忆更新、回答与评分 |
| 3-1、7-3 | [user-memory-evaluation](user-memory-evaluation/) | ✅ | 三层用户记忆评估集与离线评分示例；[第七章实验 7-3](../book/chapter7.md) 使用四档多维 Rubric、逐维证据与幻觉一票否决 |
| 3-2 | [mem0](mem0/) · [memobase](memobase/) | ✅ | 用 mem0、Memobase 两个开源框架各实现一版用户记忆，作为实验 3-2 的对照实现 |
| 3-3 | [log-sanitization](log-sanitization/) | ✅ | 智能日志脱敏系统，基于本地 Ollama 模型检测并脱敏日志中的密钥和 PII 敏感数据 |
| 3-4 | [dense-embedding](dense-embedding/) | ✅ | 向量相似性搜索服务，对比 ANNOY（树）与 HNSW（图）两种 ANN 算法的权衡 |
| 3-5 | [sparse-embedding](sparse-embedding/) | ✅ | 从零实现基于 BM25 的稀疏向量搜索引擎，可视化内部工作机制 |
| 3-6 | [retrieval-pipeline](retrieval-pipeline/) | ✅ | 稠密 + 稀疏 + 神经重排序的完整流水线，用测试用例展示混合检索的互补效果 |
| 3-7 | [structured-index](structured-index/) | ✅ | 实现并对比 RAPTOR（递归抽象树）与 GraphRAG（知识图谱）两种结构化索引 |
| 3-8 | [agentic-rag](agentic-rag/) | ✅ | 用七道题比较单次检索与自主搜索，逐题核对找到了哪些标注法条、用了几次搜索 |
| 3-9 | [agentic-rag-for-user-memory](agentic-rag-for-user-memory/) | ✅ | 用 Agentic RAG 管理用户对话历史，实现跨会话记忆检索 |
| 3-10 | [contextual-retrieval](contextual-retrieval/) | ✅ | 用同一组 15 个查询比较原始分块与带前缀分块：重新生成前缀的正式运行中，BM25 首位命中从 9 题增至 12 题，离线示例使用已有前缀，命中 13 题；正文另引的 49% 和 67% 来自 Anthropic 的 top-20 报告 |
| 3-11 | [contextual-retrieval-for-user-memory](contextual-retrieval-for-user-memory/) | ✅ | 结合 Advanced JSON Cards 与上下文感知 RAG，形成双层记忆结构实现主动服务 |
| 3-12 | [structured-knowledge-extraction](structured-knowledge-extraction/) | ✅ | 以司法判例跑通「因子发现 → 聚类原型 → 对话式建议」三段流水线 |

## 项目类型说明

| 图标 | 类型 | 含义 |
| :--: | --- | --- |
| ✅ | **可独立运行** | 仓库提供实现与运行步骤；离线示例可直接读取归档，重新运行所需的模型、依赖和凭据见项目说明 |
| 📖 | **复现指南** | 依赖需自行 `git clone` 的**外部仓库**（训练框架、评测基准等） |
| 🚧 | **设计文档** | 仅包含架构与实现方案，可运行代码仍在完善中 |
