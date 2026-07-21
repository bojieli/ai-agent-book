# Chapter 3 · User Memory and Knowledge Bases

> Enables Agents to remember users across sessions and access external knowledge. Covers user memory systems, basic RAG pipelines, and knowledge organization and retrieval beyond flat text (structured indexes, knowledge graphs, etc.).

← [Back to main README](../README.en.md) · 📖 [Read chapter text](../book-en/chapter3.md)

## Companion Projects

| Project | Type | Description |
| --- | :--: | --- |
| [user-memory](user-memory/) | ✅ | Builds a long-term user memory system, enabling the Agent to remember user preferences and historical interactions to provide personalized services. |
| [mem0](mem0/) · [memobase](memobase/) | ✅ | Implements a version of user memory using each of the two open-source memory frameworks, mem0 and Memobase, serving as a comparative implementation for Experiment 3-2 "Memory Strategy Comparison," facilitating horizontal comparison of extraction forms and answer quality across different memory solutions. |
| [user-memory-evaluation](user-memory-evaluation/) | ✅ | Systematically evaluates the accuracy, relevance, and effectiveness of user memory systems, including multiple test scenarios and evaluation metrics. |
| [dense-embedding](dense-embedding/) | ✅ | Builds a vector similarity search service, comparing ANNOY (tree-based) and HNSW (graph-based) approximate nearest neighbor index algorithms. Demonstrates the trade-offs between different indexing strategies in terms of performance, memory usage, and update capability. |
| [sparse-embedding](sparse-embedding/) | ✅ | Implements a sparse vector search engine based on the BM25 algorithm from scratch. Provides rich logging and visualization interfaces to understand the internal workings of the search engine, including term frequency weight calculation and inverted index principles. |
| [retrieval-pipeline](retrieval-pipeline/) | ✅ | Builds a complete retrieval pipeline combining dense retrieval, sparse retrieval, and neural re-ranking. Systematically demonstrates the complementary advantages of hybrid retrieval in different scenarios through carefully designed test cases. |
| [multimodal-agent](multimodal-agent/) | ✅ | Compares three multimodal processing strategies: native multimodal processing, extraction to text, and tool-based analysis. Reveals the trade-offs in fidelity, cost, and flexibility among different technical paths through ablation studies within a unified framework. |
| [structured-index](structured-index/) | ✅ | 实现并对比 RAPTOR（递归抽象树）与 GraphRAG（知识图谱）两种结构化索引 |
| [agentic-rag](agentic-rag/) | ✅ | Compare the performance differences between traditional Non-Agentic RAG and Agentic RAG. Show how an Agent, using the ReAct pattern, leads iterative information retrieval, significantly improving answer quality when handling complex judicial Q&A. |
| [agentic-rag-for-user-memory](agentic-rag-for-user-memory/) | ✅ | Apply the Agentic RAG framework to manage user conversation history. Leverage multi-turn iterative search capabilities to handle memory retrieval across sessions, enabling basic recall and cross-session retrieval capabilities. |
| [contextual-retrieval](contextual-retrieval/) | ✅ | Implement the contextual retrieval technique proposed by Anthropic. By generating prefix summaries containing core context for text chunks, it addresses the context loss problem of traditional chunking methods, reducing retrieval failure rates by 49-67%. |
| [contextual-retrieval-for-user-memory](contextual-retrieval-for-user-memory/) | ✅ | Apply contextual retrieval techniques to user memory construction. Combine Advanced JSON Cards with Contextual RAG to form a dual-layer memory structure, enabling higher-level proactive service capabilities. |
| [structured-knowledge-extraction](structured-knowledge-extraction/) | ✅ | Using judicial precedents as an example, implement a three-stage pipeline: "Bottom-up factor discovery → Case prototype clustering → Conversational advisory Agent". Without predefined rigid fields, the LLM autonomously discovers factors from a large number of cases and summarizes them into a modular schema (core factors + charge-specific extension factors). Cases are then clustered into several prototypes, and the importance of each factor for each prototype is calculated. The Agent matches new case facts to the most similar prototype, asks for missing information based on factor importance, and provides evidence-based advice (with a legal disclaimer). |
## Project Types

| Icon | Type | Meaning |
| :--: | --- | --- |
| ✅ | **Standalone** | Full code in this repo, runs after configuring API Key |
| 📖 | **Reproduction Guide** | Detailed doc depending on **external repos** to `git clone` |
| 🚧 | **Design Doc** | Architecture/implementation plan only, runnable code still WIP |
