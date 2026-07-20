# 深入理解 AI Agent：設計原理與工程實踐

**[English](README.en.md) | [中文](README.md) | 台灣正體 | [Tiếng Việt](README.vi.md) | [தமிழ்](README.ta.md)**

本倉庫是《深入理解 AI Agent：設計原理與工程實踐》一書的開源主倉庫，包含**全書正文**與**配套示常式式碼**。全書正文、配圖與配套實驗程式碼全部開源，歡迎把實驗親手跑一遍、提 issue 和 PR。

## 📖 電子書

全書提供多種語言版本：

- **中文 PDF（原版）**：[`book/深入理解-AI-Agent-李博杰-v1.2.pdf`](book/深入理解-AI-Agent-李博杰-v1.2.pdf)
- **台灣正體 PDF**（社群貢獻翻譯，by [@tigercosmos](https://github.com/tigercosmos)）：[`book-zhtw/深入理解-AI-Agent-李博杰-v1.2-zhtw.pdf`](book-zhtw/深入理解-AI-Agent-李博杰-v1.2-zhtw.pdf)
- **英文 PDF**（社群貢獻翻譯，by [@nsdevaraj](https://github.com/nsdevaraj)）：[`book-en/AI-Agents-in-Depth-Bojie-Li-v1.2.pdf`](book-en/AI-Agents-in-Depth-Bojie-Li-v1.2.pdf)
- **泰米爾語 PDF**（社群貢獻翻譯，by [@nsdevaraj](https://github.com/nsdevaraj)）：[`book-ta/AI-Agents-in-Depth-Bojie-Li-v1.2-ta.pdf`](book-ta/AI-Agents-in-Depth-Bojie-Li-v1.2-ta.pdf)
- **越南語 PDF**（社群貢獻翻譯，by [@toanalien](https://github.com/toanalien)）：[`book-vi/AI-Agents-in-Depth-Bojie-Li-v1.2-vi.pdf`](book-vi/AI-Agents-in-Depth-Bojie-Li-v1.2-vi.pdf)

中文正文與編譯好的 PDF 位於 [`book/`](book/) 目錄；台灣正體、英文、泰米爾語與越南語翻譯為**社群貢獻**，分別位於 [`book-zhtw/`](book-zhtw/)、[`book-en/`](book-en/)、[`book-ta/`](book-ta/) 與 [`book-vi/`](book-vi/) 目錄，內容可能滯後於中文原版：

- **正文原始程式碼**：`book/introduction.md`（引言）、`book/chapter1.md` ~ `book/chapter10.md`（第一至第十章）、`book/afterword.md`（後記）
- **自行編譯**：安裝 pandoc、xelatex、ElegantBook 文件類與相關字型後，執行

  ```bash
  cd book && bash build_pdf.sh
  ```

  圖表由 `book/gen_*_figs.py` 生成、存於 `book/images/`，排版細節見 `book/preamble.tex` 與 `book/*.lua`。

## 🌏 關於台灣正體版本

台灣正體中文版位於 [`book-zhtw/`](book-zhtw/) 目錄，是以簡體中文原版（[`book/`](book/)）為基礎，透過**自動化流程**轉換與校正而成，內容可能滯後於簡體原版。這個版本並非人工逐句重譯，而是由以下兩階段管線產生：

1. **OpenCC 字詞轉換**：先以 [OpenCC](https://github.com/BYVoid/OpenCC) 的 `s2twp` 設定（簡體 → 台灣正體，含慣用詞轉換）將原版所有 Markdown、圖表 SVG 文字、`.tex` 與 `.lua` 排版檔一併轉為正體，例如「软件 → 軟體」「内存 → 記憶體」「鼠标 → 滑鼠」。
2. **zhtw-mcp 用語校正**：再以 [zhtw-mcp](https://github.com/sysprog21/zhtw-mcp)（依教育部標準的台灣正體語言校正器）對所有 `.md` 檔執行 `lint --fix`（`lexical_safe` 模式），修正兩岸用語與標點差異，例如「計算機 → 電腦」「構建 → 建構」「反饋 → 回饋」「實時 → 即時」「賬單 → 帳單」，並將全形引號 `“ ”` 改為台灣慣用的 `「 」`。

校正時對**技術術語與識別字**做了保護，避免被自動規則誤改：技術名詞 `ReAct`（推理—行動框架）不會被改成前端框架 `React`；套件／路徑名稱如 `python-constraint`、`python-pptx`、`build-linux-kernel-qemu`、`.github/workflows` 亦維持原本大小寫。人名「李博杰」等專有名詞在轉換後一律還原。

### 自行重建

轉換與校正流程可完整重現：

```bash
# 1. OpenCC 轉換（s2twp）
pip install opencc-python-reimplemented   # 提供 opencc 模組

# 2. zhtw-mcp 校正（需 Rust 工具鏈自 source 建置）
git clone https://github.com/sysprog21/zhtw-mcp && cd zhtw-mcp && make
zhtw-mcp lint <file>.md --fix              # 保護 ReAct 等術語後再套用

# 3. 編譯 PDF（與其他語言版本相同）
cd book-zhtw && bash build_pdf.sh
```

歡迎針對用語校正提 issue 或 PR；若發現自動流程誤改的術語，請一併回報。

## 📑 內容速覽（第 1–10 章）

全書圍繞核心公式 **Agent = LLM + 上下文 + 工具** 展開，十章內容如下：

- **第 1 章 · Agent 基礎知識**：從「模型即 Agent」的新正規化出發，建立 **Agent = LLM + 上下文 + 工具** 的核心公式，並引入 Harness 工程——模型之外的一切工程能力，才是真正的競爭力所在。
- **第 2 章 · 上下文工程**：上下文決定 Agent 的能力上限。深入大模型 API 的上下文結構、KV Cache 友好設計、提示工程、動態提示詞與 Agent Skills、狀態列元資訊，以及上下文壓縮策略。
- **第 3 章 · 使用者記憶和知識庫**：讓 Agent 跨會話記住使用者、並接入外部知識。涵蓋使用者記憶系統、RAG 基礎管道，以及超越扁平文字的知識組織與檢索（結構化索引、知識圖譜等）。
- **第 4 章 · 工具**：工具是 Agent 的雙手。講工具分類與通用設計原則、MCP 協定與工具選擇的挑戰、感知/執行/協作三類工具，以及事件驅動的非同步 Agent。
- **第 5 章 · Coding Agent 與程式碼生成**：程式碼是「能創造新工具的工具」，是通用 Agent 的元能力。以生產級 Coding Agent 為例，展示這一最強通用工具的完整實現。
- **第 6 章 · Agent 的評估**：把 Agent 的表現變成可比較的訊號。從評估環境、資料集設計、指標體系，到統計顯著性、可觀測性、評估驅動選型，直至生產級內部評估與模擬環境。
- **第 7 章 · 模型後訓練**：預訓練、SFT、RL 三階段全景。何時選 SFT、何時選 RL，RLHF、演算法比較、資料與環境，以及讓模型學會工具呼叫、提升樣本效率的前沿探索。
- **第 8 章 · Agent 的自我進化**：不改權重也能成長。三種學習正規化，從經驗中學習、主動工具發現，到「從工具使用者到工具創造者」，讓 Agent 從「聰明」走向「熟練」。
- **第 9 章 · 多模態與即時互動**：把感知與行動從文字擴充套件到語音、GUI 與物理世界。語音三正規化（級聯/端到端全模態/全雙工）、流式語音感知與合成、Computer Use 與機器人操作。
- **第 10 章 · 多 Agent 協作**：群體的智慧可以高於個體。多 Agent 分類框架、何時真正優於單 Agent、共享與不共享上下文的協作、失敗模式，以及湧現的「Agent 社會」。

## 💻 配套程式碼

所有專案按**章節**組織，與全書十章一一對應，涵蓋從基礎概念到高階技術的完整學習路徑，目錄為 `chapterN/專案名/`。第 5、8、9、10 章的絕大多數實驗現均提供可獨立執行的配套 demo，並已對接真實 LLM API 驗證跑通。

### 專案型別說明

配套專案分為三類，請對照下方圖示瞭解每個專案「開箱即用」的程度：

- ✅ **可獨立執行**：本倉庫自帶完整程式碼，配置好 API Key（見文末）即可執行。
- 📖 **復現指南**：專案本身是一份詳細的復現文件，依賴需自行 `git clone` 的**外部倉庫**（訓練框架、評測基準等），見下方《外部倉庫獲取》。
- 🚧 **設計文件**：目前僅包含架構與實現方案的設計文件，可執行程式碼仍在完善中。

下列專案**不是**✅ 可獨立執行，複製本倉庫時請留意：

| 專案 | 型別 | 說明 |
| --- | --- | --- |
| `chapter7/AdaptThink` · `AWorld-train` · `MiniMind-pretrain` · `retool` · `SpatialReasoning` | 📖 復現指南 | 訓練類實驗，依賴外部框架，按 README 復現 |
| 第 6 章全部基準 · 第 7 章多數訓練框架 · 第 9 章 `browser-use`/`claude-quickstarts` · 第 10 章 `use-computer-while-calling` | 📖 復現指南 | 依賴外部倉庫，見《外部倉庫獲取》 |

### 外部倉庫獲取（簡要）

第 6、7、9、10 章的**部分**實驗依賴評測基準、訓練框架、機器人平臺等**外部倉庫**（出於體積與版權未內建本倉庫）。為免一上來資訊過載，**完整的複製命令、上游地址與本書驗證過的提交，見文末《附錄 · 外部倉庫獲取》**。建議先從前面各章可獨立執行的專案上手，需要復現訓練 / 評測 / 機器人類實驗時，再按文末指引快速獲取。

## 🚀 第 1 章 · Agent 基礎知識

### learning-from-experience - 強化學習 vs LLM 對比
`chapter1/learning-from-experience/`

對比傳統強化學習（Q-learning）與基於 LLM 的上下文學習，復現 Shunyu Yao 的 「The Second Half」 博文中的關鍵洞察。透過尋寶遊戲展示 LLM 如何以 250-400 倍的樣本效率超越傳統 RL。

**核心概念**：強化學習、上下文學習、樣本效率、先驗知識

### web-search-agent - Kimi K2 模型即 Agent
`chapter1/web-search-agent/`

實現具備基礎深度搜尋能力的 Agent，能夠進行多輪搜尋和資訊整合。

**核心概念**：網路搜尋、模型原生 Agent

### search-codegen - GPT-5 原生工具整合
`chapter1/search-codegen/`

建構能夠基礎深度搜尋能力和程式碼沙盒能力的 Agent，綜合利用網路搜尋、程式碼執行等工具實現複雜分析。

**核心概念**：網路搜尋、程式碼生成、模型原生 Agent

### context - 上下文消融研究
`chapter1/context/`

透過系統性的消融實驗展示 Agent 上下文各個元件的重要性。支援多種 LLM 提供商（SiliconFlow Qwen、位元組 Doubao、月之暗面 Kimi），配置不同的上下文模式觀察 Agent 行為變化。

**核心概念**：上下文管理、工具呼叫、ReAct 迴圈、消融研究

## 🎯 第 2 章 · 上下文工程

### local_llm_serving - 本地 LLM 部署與工具呼叫
`chapter2/local_llm_serving/`

跨平臺的本地 LLM 部署方案，自動選擇最佳後端（vLLM 或 Ollama）。展示即使 0.6B 的小模型也能透過良好的系統設計實現出色的工具呼叫能力。支援流式響應，即時顯示思考過程。

**核心概念**：模型部署、Chat Template、流式處理、工具呼叫

### attention_visualization - 注意力機制視覺化
`chapter2/attention_visualization/`

視覺化 LLM 的完整輸入輸出 token 序列和注意力權重分佈，深入理解模型如何處理上下文、進行推理和呼叫工具。

**核心概念**：注意力機制、token 分析、推理過程視覺化

### kv-cache - KV Cache 友好的上下文設計
`chapter2/kv-cache/`

探索不同上下文管理模式對 KV Cache 的影響，演示常見的錯誤模式如何破壞快取效率。透過實驗展示正確的上下文設計如何顯著降低延遲和成本。

**核心概念**：KV Cache、上下文最佳化、效能調優

### context-compression - 上下文壓縮策略
`chapter2/context-compression/`

實現並對比多種上下文壓縮策略，包括摘要、關鍵資訊提取、語義壓縮等。在保持 Agent 能力的同時減少 token 使用量。

**核心概念**：上下文壓縮、token 最佳化、資訊密度

### prompt-engineering - 提示工程消融研究
`chapter2/prompt-engineering/`

擴充套件 Tau-Bench 框架，透過系統性的消融實驗量化不同提示工程因素對 Agent 效能的影響。展示語氣風格、指令組織、工具描述等因素如何影響任務完成率。

**核心概念**：提示工程、消融研究、效能基準測試

### system-hint - 系統提示最佳化
`chapter2/system-hint/`

研究系統提示（System Hint）對 Agent 行為的影響，探索如何透過最佳化系統提示提升效能。

**核心概念**：系統提示、行為引導、提示最佳化

### log-sanitization - 日誌脫敏處理
`chapter2/log-sanitization/`

實現智慧的日誌脫敏系統，在保留除錯資訊的同時保護敏感資料。

**核心概念**：隱私保護、日誌處理、資料安全

### prompt-injection - 提示注入攻防實驗
`chapter2/prompt-injection/`

構造 3 種攻擊場景（直接注入、間接注入、記憶注入）× 4 種防禦配置（無防禦、提示詞加固、來源標記、組合防禦）的對照實驗，用確定性規則統計攻擊成功率，直觀展示逐層疊加防禦後注入成功率如何顯著下降。

**核心概念**：提示注入、間接注入、資料與指令分離、執行時校驗

### agent-skills-ppt - Agent Skills 漸進式披露生成 PPT
`chapter2/agent-skills-ppt/`

復現 Agent Skills 的「漸進式披露」思想：Agent 啟動時只看到一份薄 Skill 目錄，識別出任務需要 `pptx` Skill 後才逐層載入其完整流程、細則文件與捆綁指令碼，最終用 python-pptx 生成真實的 `.pptx` 檔案。

**核心概念**：Agent Skills、漸進式披露、按需載入、工具編排

## 📚 第 3 章 · 使用者記憶和知識庫

### user-memory - 使用者記憶系統
`chapter3/user-memory/`

建構長期使用者記憶系統，讓 Agent 能夠記住使用者偏好和歷史互動，提供個人化服務。

**核心概念**：長期記憶、個人化、使用者建模

### mem0 / memobase - 開源記憶框架對照
`chapter3/mem0/` 和 `chapter3/memobase/`

用 mem0、Memobase 兩個開源記憶框架各自實現一版使用者記憶，作為實驗 3-2「記憶策略對比」的對照實現，便於橫向比較不同記憶方案的抽取形態與回答質量。

**核心概念**：記憶框架、mem0、Memobase、方案對比

### user-memory-evaluation - 使用者記憶評估框架
`chapter3/user-memory-evaluation/`

系統化評估使用者記憶系統的準確性、相關性和有效性，包含多種測試場景和評估指標。

**核心概念**：評估框架、測試用例、效能度量

### dense-embedding - 稠密嵌入向量檢索服務
`chapter3/dense-embedding/`

建構向量相似性搜尋服務，對比研究 ANNOY（基於樹）和 HNSW（基於圖）兩種近似最近鄰索引演算法。展示不同索引策略在效能、記憶體佔用和更新能力上的權衡。

**核心概念**：稠密嵌入、向量檢索、ANN 演算法、語義搜尋

### sparse-embedding - 稀疏檢索引擎
`chapter3/sparse-embedding/`

從零實現基於 BM25 演算法的稀疏向量搜尋引擎，透過豐富的日誌和視覺化介面展示搜尋引擎的內部工作機制，理解詞頻權重計算和反向索引原理。

**核心概念**：稀疏嵌入、BM25、TF-IDF、精確匹配

### retrieval-pipeline - 混合檢索流水線
`chapter3/retrieval-pipeline/`

建構完整的檢索流水線，結合稠密檢索、稀疏檢索和神經重排序。透過精心設計的測試用例，系統性展示混合檢索在不同場景下的優勢互補效果。

**核心概念**：混合檢索、神經重排序、跨編碼器、檢索融合

### multimodal-agent - 多模態資訊提取
`chapter3/multimodal-agent/`

對比三種多模態處理策略：原生多模態處理、提取為文字、工具化分析。透過統一框架下的消融研究，揭示不同技術路徑在保真度、成本和彈性上的權衡。

**核心概念**：多模態、視覺理解、OCR、端到端處理

### structured-index - 結構化索引
`chapter3/structured-index/`

實現並對比 RAPTOR（遞迴抽象樹）和 GraphRAG（知識圖譜）兩種先進索引策略。透過索引技術手冊演示如何建構反映知識內在層次和關聯的結構化索引。

**核心概念**：RAPTOR、GraphRAG、層次摘要、知識圖譜

### agentic-rag - 智慧體 RAG
`chapter3/agentic-rag/`

對比傳統 Non-Agentic RAG 與 Agentic RAG 的效能差異。展示 Agent 如何透過 ReAct 模式主導迭代式資訊檢索，在處理複雜司法問答時顯著提升答案質量。

**核心概念**：Agentic RAG、ReAct 迴圈、迭代檢索、主動探索

### agentic-rag-for-user-memory - 利用 Agentic RAG 建構使用者記憶
`chapter3/agentic-rag-for-user-memory/`

將 Agentic RAG 框架應用於管理使用者對話歷史，透過多輪迭代搜尋能力處理跨會話的記憶檢索，實現基礎回憶和多會話檢索能力。

**核心概念**：使用者記憶、對話歷史索引、跨會話檢索

### contextual-retrieval - 上下文感知檢索
`chapter3/contextual-retrieval/`

實現 Anthropic 提出的上下文感知檢索技術，透過為文字塊生成包含核心上下文的字首摘要，解決傳統分塊方法的上下文丟失問題，將檢索失敗率降低 49-67%。

**核心概念**：上下文增強、字首生成、語義錨定、檢索最佳化

### contextual-retrieval-for-user-memory - 上下文感知的使用者記憶系統
`chapter3/contextual-retrieval-for-user-memory/`

將上下文感知檢索技術應用於使用者記憶建構，結合 Advanced JSON Cards 與上下文感知 RAG，形成雙層記憶結構，實現更高層次的主動服務能力。

**核心概念**：雙層記憶、結構化事實、上下文檢索、主動服務

### structured-knowledge-extraction - 結構化知識提取
`chapter3/structured-knowledge-extraction/`

以司法判例為例跑通「自下而上因子發現 → 聚類出案件原型 → 對話式建議 Agent」三段流水線：不預設僵化欄位，由 LLM 從大量案例中自主發現因子並歸納為模組化 schema（核心因子 + 罪名擴充套件因子）；再將案件聚類為若干原型、算出各原型的因子重要性；Agent 對新案情匹配最相似原型、按重要性追問缺失資訊並給出有依據的建議（附法律免責宣告）。

**核心概念**：自下而上知識發現、模組化因子、聚類原型、可解釋決策

## 🛠️ 第 4 章 · 工具

### perception-tools - 感知工具 MCP 伺服器
`chapter4/perception-tools/`

建構全面的感知工具集，提供網路搜尋、多模態理解、檔案系統操作和公共資料來源訪問能力。大部分功能基於免費開放 API（DuckDuckGo、Open-Meteo、Yahoo Finance、OpenStreetMap 等），無需 API 金鑰即可使用。

**核心概念**：MCP 協定、多模態解析、公共資料來源、文件理解、地理資訊服務

### execution-tools - 執行工具 MCP 伺服器
`chapter4/execution-tools/`

實現具備安全機制的執行工具集，包括檔案操作、程式碼直譯器、虛擬終端機和外部系統整合。透過 LLM 二次審批機制防止危險操作，自動摘要複雜輸出，並驗證程式碼。

**核心概念**：MCP 協定、執行安全、LLM 審批、結果摘要、自動驗證

### collaboration-tools - 協作工具 MCP 伺服器
`chapter4/collaboration-tools/`

提供全面的協作能力，包括瀏覽器自動化（browser-use 框架）、人機協同（Human-in-the-Loop）、多渠道通知（Email、Telegram、Slack、Discord）和定時器管理。支援敏感操作的管理員審批和定時任務排程。

**核心概念**：MCP 協定、瀏覽器自動化、HITL 模式、多渠道通知、定時任務

### agent-with-event-trigger - 事件觸發型 Agent 與 MCP 整合
`chapter4/agent-with-event-trigger/`

基於 FastAPI 建構的現代化事件驅動 Agent，預設整合前三個 MCP 伺服器的所有工具。採用原生非同步架構實現清晰的 MCP 工具載入，透過 HTTP API 接收多源事件（Web、即時訊息、GitHub、定時器等）。提供自動 API 文件（Swagger UI）和後臺監控能力。

**核心概念**：FastAPI、原生非同步、MCP 整合、事件驅動、自動 API 文件、工具編排

### active-tool-selection - 主動工具選擇
`chapter4/active-tool-selection/`

實現智慧工具選擇機制，讓 Agent 能夠根據任務需求主動選擇最合適的工具組合，而非被動接受預定義的工具集。

**核心概念**：工具選擇、動態工具載入、任務分析

### async-agent - 帶並行執行和打斷能力的非同步 Agent
`chapter4/async-agent/`

基於 asyncio 單執行緒實現事件驅動非同步 Agent 框架（Flux）的核心：inbox 事件佇列按緊急度分派（打斷/立即/排隊），支援非同步工具並行執行、執行中打斷當前 turn、並對模擬的長任務做取消與狀態查詢。決策由真實 LLM（function calling）完成。

**核心概念**：非同步程式設計、事件佇列、打斷機制、並行工具取消、非阻塞 I/O

> `chapter4/docker-compose.yml` 與 `chapter4/DOCKER_DEPLOYMENT.md` 提供了將上述 MCP 工具伺服器容器化部署的參考方案。

## 💻 第 5 章 · Coding Agent 與程式碼生成

### coding-agent - 生產級 Coding Agent
`chapter5/coding-agent/`

基於 Claude 建構的生產級 AI 編碼助手，採用純 Python 實現所有工具，無需命令列依賴。包含 17 個完整實現的工具，涵蓋檔案操作、搜尋、Shell 操作和專案管理。特別實現了純 Python 的 Grep 工具，完全相容 ripgrep 的功能。

**核心特性**：
- 純 Python 實現，無命令列依賴，特別適合 Mac 使用者
- 完整的工具套件：檔案讀寫編輯、純 Python 正則搜尋、目錄列表、Shell 會話管理
- 系統提示技術：時間戳、工具呼叫計數、TODO 列表管理、詳細錯誤資訊
- 持久化 Shell 環境、自動 Lint 偵測、流式響應支援
- 支援多個 LLM 提供商（Anthropic、OpenAI、OpenRouter）

**核心概念**：程式碼生成、檔案編輯、純 Python 工具、系統提示、Lint 偵測、多提供商支援

### code-for-math - 用程式碼提升數學解題能力
`chapter5/code-for-math/`

讓同一模型在同一組競賽數學題上對比「純思維鏈」與「程式碼輔助」兩種模式：後者把題目形式化為 Python（sympy/numpy/scipy），透過 function calling 在子程序沙箱執行，用精確計算替代易錯的心算，準確率顯著更高。

**核心概念**：程式碼直譯器、符號計算、思維鏈對比、工具增強推理

### code-for-logic - 用程式碼提升邏輯思考能力
`chapter5/code-for-logic/`

把「騎士與無賴」邏輯謎題轉化為約束滿足問題（CSP）：Agent 用 `python-constraint` 定義變數與雙條件約束並呼叫求解器，對比純自然語言推理與程式碼輔助兩種模式在一組 K&K 謎題上的正確率。

**核心概念**：約束求解、CSP 建模、形式化推理、程式碼輔助

### small-model-codified-rules - 小模型程式碼化規則
`chapter5/small-model-codified-rules/`

基於 τ-bench 航空客服場景的對照實驗：把複雜業務政策（退款規則）從自然語言提示詞搬行程式碼/工具後，小模型的任務成功率與政策一致性大幅提升，工具內程式碼校驗能實時攔截模型的錯誤認知。

**核心概念**：程式碼化業務規則、政策執行、工具內校驗、小模型可靠性

### paper-to-ppt - 論文自動生成 PPT（提議者～稽核者）
`chapter5/paper-to-ppt/`

把「做 PPT」重構為程式碼生成問題：Proposer 編寫 Slidev（Markdown+HTML）程式碼，Reviewer 把每頁真正渲染成 PNG 並用 Vision LLM 檢查排版問題，據結構化回饋迭代修訂；雙 Agent 分工使上下文峰值顯著更小。

**核心概念**：程式碼生成、Slidev、提議者～稽核者、視覺質量控制

### paper-to-video - 論文講解影片自動生成
`chapter5/paper-to-video/`

在「論文 → PPT」基礎上為每頁投影片生成口語化講解詞，呼叫 TTS 合成語音，再用 ffmpeg 把每頁截圖與其音訊逐頁同步合成為一段帶旁白的講解影片。

**核心概念**：多媒體生成、講解詞生成、TTS、ffmpeg 音畫同步

### video-edit - 基於 API 的智慧影片剪輯
`chapter5/video-edit/`

使用者給一段多場景影片 + 一句自然語言需求，Agent 透過「兩步 Vision 定位」（先粗後細抽幀讀圖）確定目標場景時間邊界，剪出片段後由 Reviewer 抽取成片關鍵幀核對，不合格則迭代。

**核心概念**：影片剪輯、Vision 定位、由粗到細、提議者～稽核者

### adaptive-log-parser - 適應性日誌解析系統
`chapter5/adaptive-log-parser/`

一個能自我進化的日誌解析系統：遇到無法解析的新格式時不報錯，而是把失敗樣本與報錯交給程式碼生成 Agent 生成 `parse` 函式，自動測試透過後熱更新註冊進解析引擎，全流程無需人工介入。

**核心概念**：程式碼作為系統介面卡、自愈閉環、程式碼熱更新、自動測試

### log-diagnosis - 生產日誌智慧診斷系統
`chapter5/log-diagnosis/`

診斷 Agent 讀取生產軌跡日誌、架構文件與 PRD，自動定位問題與根因、生成結構化報告與迴歸測試用例，用重放框架真正執行驗證，並（mock）透過 MCP 對接 GitHub 建立 Issue。

**核心概念**：軌跡診斷、根因定位、迴歸測試生成、重放驗證

### dynamic-form - 動態表單意圖澄清系統
`chapter5/dynamic-form/`

面對資訊不完整的請求時，Agent 不逐條追問，而是動態生成一個含級聯邏輯的自包含 HTML 表單讓使用者拋棄式補全；前端把表單彙總為 JSON 交回 Agent 繼續任務。

**核心概念**：程式碼生成、意圖澄清、動態表單、級聯邏輯

### erp-agent - 自然語言 ERP Agent（NL → SQL）
`chapter5/erp-agent/`

把中文自然語言查詢轉成 SQL 交由資料庫執行、直接呈現結果表，核心是 artifact（製品）模式：LLM 只生成 SQL 製品、不親自搬運資料，既省 token 又避免手算出錯，幾萬行結果也能秒回。

**核心概念**：NL2SQL、artifact 模式、資料庫執行、成本與準確性

### conversational-ui - 對話式介面定製系統
`chapter5/conversational-ui/`

使用者用自然語言提出 UI 定製需求（顏色/字型/文案/佈局），Agent 自主定位並修改 React 前端原始程式碼，藉助 Vite 熱載入（HMR）讓改動即時生效，支援多輪迭代定製。

**核心概念**：程式碼修改、前端定製、熱載入、多輪迭代

## 🎯 第 6 章 · Agent 的評估

### terminal-bench - 終端機環境基準測試
`chapter6/terminal-bench/`

Terminal-Bench 是測試 AI Agent 在真實終端機環境中表現的基準測試。從編譯程式碼到訓練模型、設定伺服器，評估 Agent 如何處理真實的端到端任務。包含約 100 個任務的資料集和執行框架，支援多種 Agent 實現。

**核心概念**：終端機自動化、任務評估、Docker 沙箱、基準測試

### SWE-bench - 軟體工程基準測試
`chapter6/SWE-bench/`

SWE-bench 是評估大語言模型解決真實 GitHub 問題能力的基準測試。給定程式碼庫和問題描述，模型需要生成能夠解決問題的補丁。包含 SWE-bench、SWE-bench Lite、SWE-bench Verified 和 SWE-bench Multimodal 多個版本。

**核心概念**：程式碼修復、GitHub 問題、補丁生成、Docker 評估

### GAIA - 通用 AI 助手基準測試
`chapter6/GAIA/`

GAIA 旨在評估下一代 LLM（具有工具增強、高效提示、搜尋訪問等能力的 LLM）。包含 450+ 個需要不同程度工具和自主性的非平凡問題，答案明確無歧義。分為 3 個難度級別。

**核心概念**：工具使用、多步推理、自主性評估

### OSWorld - 作業系統級 Agent 基準
`chapter6/OSWorld/`

評估 Agent 在完整作業系統環境中執行復雜任務的能力，包括檔案管理、應用程式操作和系統配置。

**核心概念**：作業系統自動化、多應用協作、系統級任務

### android_world - Android 環境基準
`chapter6/android_world/`（📖 外部倉庫，見《外部倉庫獲取》）

評估 Agent 在 Android 移動環境中的表現，包括應用導航、UI 互動和任務完成能力。

**核心概念**：移動自動化、Android UI、應用互動

> `chapter6/android-world/`（連字元命名）並非基準程式碼，而是本書對 T3A Agent 在 android_world 上失敗案例的分析筆記（`t3a*.md`），可作為閱讀材料參考。

### tau2-bench - 工具增強推理基準
`chapter6/tau2-bench/`

專注於評估 Agent 使用工具進行復雜推理的能力，包括計算、搜尋和資料處理等場景。

**核心概念**：工具增強推理、多步驟任務、工具組合

### elo-leaderboard - ELO 排行榜系統
`chapter6/elo-leaderboard/`

實現基於 ELO 評分系統的 Agent 效能排行榜，透過對戰比較來評估不同 Agent 的相對能力。

**核心概念**：ELO 評分、相對評估、排行榜系統

### model-benchmark - 多維度模型效能基準測試
`chapter6/model-benchmark/`

對多個 OpenAI 相容的 LLM API 提供商做橫向基準測試，用流式介面精確測量首 token 延遲（TTFT），在並行下測出端到端延遲分位數（p50/p95）、吞吐與成功率，一條命令跑出多維度對比表，說明選型是多維權衡而非只看排行榜。

**核心概念**：TTFT、延遲分位數、吞吐、並行壓測、模型選型

### agent-cost-analysis - Agent 任務端到端成本分析
`chapter6/agent-cost-analysis/`

對典型多輪 Agent 任務（客服退款）做全鏈路成本拆解：用自建輕量 tracing 記錄每次 LLM 呼叫的輸入/輸出/快取 token、時延與成本，聚合出「哪一步最貴」，再用 A/B 量化 KV-cache 友好設計 + 上下文壓縮帶來的真實節省。

**核心概念**：可觀測性、成本拆解、prompt caching、A/B 對比

### tts-quality-eval - 全自動 TTS 質量評估流水線
`chapter6/tts-quality-eval/`

用多種 TTS 配置（不同 model/voice/speed）合成同一組挑戰性文字，再以多模態 LLM-as-a-Judge 按 Rubric 逐維度（清晰度/自然度等）打分，彙總成可復現的配置對比表。

**核心概念**：LLM-as-a-Judge、Rubric 評分、TTS 評估、多維對比

## 🧠 第 7 章 · 模型後訓練

本章包含多個模型後訓練專案，涵蓋監督微調（SFT）和強化學習（RL）的各種技術和應用場景。

### AdaptThink - 適應性推理深度
`chapter7/AdaptThink/` 和 `chapter7/AdaptThink-original/`

讓推理模型學會根據問題難度適應性選擇推理模式（Thinking vs NoThinking）。透過約束最佳化和重要性取樣，在大幅降低推理成本（45-69%）的同時提升準確率。基於 DeepSeek-R1-Distill-Qwen 模型，使用 DAPO 演算法訓練。

**核心概念**：適應性推理、推理成本最佳化、約束最佳化、重要性取樣

### retool - 工具增強數學推理
`chapter7/retool/`

使用多輪對話和程式碼沙箱提升大語言模型數學推理能力。透過 SFT 和 RL 兩階段訓練，讓模型學會使用程式碼執行環境輔助數學問題求解。基於 Qwen2.5-32B-Instruct，在 AIME 2024 資料集上訓練，使用 DAPO 演算法和 SandboxFusion 沙箱。

**核心概念**：工具使用、程式碼執行、數學推理、多輪對話、DAPO 演算法

### AWorld / AWorld-train - 具身 Agent 訓練
`chapter7/AWorld/` 和 `chapter7/AWorld-train/`

基於 AWorld 框架訓練具身 Agent，讓 Agent 能夠在虛擬環境中執行復雜任務並從經驗中學習。

**核心概念**：具身智慧、環境互動、經驗學習

### SFTvsRL - SFT 與 RL 對比研究
`chapter7/SFTvsRL/`

系統性對比監督微調（SFT）和強化學習（RL）在不同任務上的效果，分析兩種方法的優劣和適用場景。

**核心概念**：SFT vs RL、訓練方法對比、效能分析

### verl - 高效 RL 訓練框架
`chapter7/verl/`

verl 是專門為大語言模型 RLHF 訓練設計的高效強化學習框架，支援 PPO、GRPO、DAPO 等多種演算法。

**核心概念**：RLHF、PPO、分散式訓練、高效最佳化

### Intuitor - 直覺推理訓練
`chapter7/Intuitor/`

訓練模型的直覺推理能力，讓模型能夠快速做出合理判斷而不需要詳細的思考鏈。

**核心概念**：直覺推理、快速決策、思考鏈最佳化

### MultilingualReasoning - 多語言推理
`chapter7/MultilingualReasoning/`

訓練模型在多種語言環境下的推理能力，提升跨語言任務的表現。

**核心概念**：多語言、跨語言推理、語言泛化

### SpatialReasoning - 空間推理訓練
`chapter7/SpatialReasoning/`

專注於訓練模型的空間推理能力，處理涉及位置、方向、距離等空間關係的問題。

**核心概念**：空間推理、幾何理解、位置關係

### SimpleVLA-RL - 視覺～語言～動作 RL
`chapter7/SimpleVLA-RL/`

結合視覺、語言和動作的強化學習訓練，讓模型能夠理解視覺輸入並執行相應動作。

**核心概念**：視覺～語言～動作、多模態 RL、具身智慧

### continued-pretraining - 持續預訓練
`chapter7/continued-pretraining/`

在特定領域資料上進行持續預訓練，提升模型在目標領域的表現。

**核心概念**：持續預訓練、領域適應、知識注入

### MiniMind-pretrain - 小型模型預訓練
`chapter7/MiniMind-pretrain/`

從零開始預訓練小型語言模型，理解預訓練的完整流程和關鍵技術。

**核心概念**：預訓練、小型模型、訓練流程

### sesame - 序列建模與評估
`chapter7/sesame/`

專注於序列建模任務的訓練和評估方法。

**核心概念**：序列建模、評估方法、效能最佳化

### orpheus - 音樂生成與理解
`chapter7/orpheus/`

訓練模型的音樂生成和理解能力。

**核心概念**：音樂生成、音訊理解、創意 AI

### tinker-cookbook - 訓練技巧集錦
`chapter7/tinker-cookbook/`

收集各種模型訓練的實用技巧和最佳實踐。

**核心概念**：訓練技巧、最佳實踐、調優方法

## 🔄 第 8 章 · Agent 的自我進化

本章聚焦讓 Agent 在不改動權重的前提下從經驗中持續成長：把成功軌跡沉澱為可複用的經驗、把重複操作外化為工具，以及把提示與觀察蒸餾進模型。

### gaia-experience - 從成功經驗中學習
`chapter8/gaia-experience/`

基於 AWorld 框架和 GAIA 基準測試，實現完整的「學習～應用」閉環。Agent 自動總結成功的任務軌跡為結構化經驗，並在新任務中檢索應用，實現自我進化。

**核心概念**：經驗學習、策略摘要、軌跡總結、自我進化

### browser-use-rpa - 工作流錄製與重播
`chapter8/browser-use-rpa/`

實現瀏覽器自動化的工作流錄製系統，將重複性操作序列自動封裝為引數化工具。透過從昂貴的 LLM 推理切換到精確的自動化執行，實現 3-5 倍速度提升。

**核心概念**：工作流錄製、RPA、工具生成、外部化學習

### prompt-distillation - 提示蒸餾
`chapter8/prompt-distillation/`

將複雜提示的效果蒸餾到模型引數中，減少推理時的提示長度，把上下文中的經驗固化為引數化知識。

**核心概念**：知識蒸餾、提示最佳化、引數化知識

### prompt-auto-optimization - 系統提示詞自動最佳化
`chapter8/prompt-auto-optimization/`

基於人類回饋的自動化系統提示學習：以 tau-bench 風格航空客服「過度轉接」問題為例，讓一個 Coding Agent 讀取系統提示詞檔案、定位有問題的規則、生成精確修改並真的改寫 prompt 檔案，再重新評測驗證，形成「回饋 → 改寫 → 驗證」閉環。

**核心概念**：提示詞自動最佳化、人類回饋、Coding Agent、閉環評測

### active-tool-discovery - 主動工具發現
`chapter8/active-tool-discovery/`

對比「全量注入 120+ 工具 schema」與「主動按需發現」兩種正規化：後者只在 system 裡保留少量基礎工具 + 一個 `discover_tools` 元工具，用嵌入相似度從工具庫檢索 3-5 個最相關的專用工具，既省 token 又避免模型在超長工具列表下錯選/濫用通用工具。

**核心概念**：主動工具發現、嵌入檢索、token 最佳化、指令遵循

### self-evolving-tools - 從網路尋找工具實現自我進化
`chapter8/self-evolving-tools/`

Alita 式「最小預定義，最大自我進化」：Agent 不預置任何領域工具，只有五個通用元工具，遇到不會做的任務時自己上網找開源庫/API、讀文件、在沙箱測試，把可行方案封裝成新工具存入工具庫並複用，全程強調幻覺控制。

**核心概念**：自我進化、工具創造、工具複用、幻覺控制

### self-evolution-eval - 自我進化 Agent 評估資料集
`chapter8/self-evolution-eval/`

為評估 Agent 的「自我進化」能力（自己發現、創造並複用工具）設計的專用資料集與驗證方法：20 個跨領域任務（不暗示工具名）+ 四層分層驗證 harness + 可控參考 Agent，超越「結果對不對」去考察發現、創造與複用質量。

**核心概念**：評估資料集設計、分層驗證、工具複用度量、自我進化

## 🎙️ 第 9 章 · 多模態與即時互動

### live-audio - 即時語音對話
`chapter9/live-audio/`

即時語音聊天演示，整合語音轉文字、AI 對話和文字轉語音功能。支援多個 AI 服務提供商（OpenAI、OpenRouter、ARK、Siliconflow），提供低延遲的對話體驗。

**核心特性**：
- 即時語音輸入與 VAD（Voice Activity Detection）
- 多提供商支援：ASR（OpenAI Whisper、SenseVoice）、LLM（GPT-4o、Gemini、Doubao）、TTS（Fish Audio）
- WebSocket 即時通訊、低延遲音訊流
- 即時延遲監控和日誌記錄

**核心概念**：語音識別、即時對話、TTS、WebSocket、多提供商架構

### browser-use - 瀏覽器自動化 Agent（Computer Use）
`chapter9/browser-use/`

Browser-Use 是強大的瀏覽器自動化框架，讓 LLM 能夠控制瀏覽器完成複雜任務。支援表單填寫、網頁導航、資料提取等場景，是 GUI 自動化（Computer Use）的典型實現。

**核心特性**：
- LLM 驅動的瀏覽器自動化
- 支援多種 LLM（ChatBrowserUse、OpenAI、Google、本地模型）
- 自訂工具擴充套件、認證處理
- 沙箱部署支援、雲端服務整合

**核心概念**：瀏覽器自動化、Computer Use、視覺理解、工具擴充套件

### claude-quickstarts - Claude 快速入門
`chapter9/claude-quickstarts/`

Claude API 的快速入門示例和最佳實踐，涵蓋各種使用場景。

**核心概念**：Claude API、提示工程、最佳實踐

### phone-agent - 電話 Agent
`chapter9/phone-agent/`

演示語音 Agent「代替使用者與外部世界進行電話互動」：上層是標準 ReAct Agent，接到自然語言任務後自行想清號碼與通話目標，呼叫 `make_phone_call` 工具（基於電話語音 API 抽象）完成整段通話，讀取結構化通話記錄並按需追問再撥，最後向使用者彙報。

**核心概念**：語音 Agent、電話互動、ReAct、工具抽象

### end-to-end-speech - 端到端語音思考 vs 級聯流水線
`chapter9/end-to-end-speech/`

對應 Step-Audio R1 的端到端語音思考正規化（單一模型「聽 → 想 → 說」）：跑通「語音輸入 → 思考 → 語音輸出」閉環，並與 ASR→LLM→TTS 級聯正規化直觀對比延遲與副語言資訊（情緒/語氣/語速）的損失差異。

**核心概念**：端到端語音、級聯對比、副語言資訊、邊想邊說

### streaming-speech - 模擬流式語音感知
`chapter9/streaming-speech/`

演示流式語音感知的核心權衡：把連續音訊按遞增長度分塊餵給 ASR，每收到一小段就產出「當前部分識別結果」以極低首包延遲儘早出文字，代價是早期分塊因缺後半句上下文可能出錯，隨音訊累積逐步收斂，與「等整句到齊再識別」的高準確/高延遲形成對照。

**核心概念**：流式感知、分塊識別、首包延遲、過早決策代價

### controllable-tts - 控制標記驅動的可控 TTS
`chapter9/controllable-tts/`

讓主 LLM 的輸出帶上控制標記（情感/語速/風格/停頓/笑聲），執行層解析標記並對映到參考語音庫的對應風格檔案再合成語音，把「在哪停頓、用什麼語氣」的決策交給 LLM，同一段文字可合成出不同風格與情感。

**核心概念**：可控 TTS、控制標記、參考語音庫、韻律控制

## 🤝 第 10 章 · 多 Agent 協作

### use-computer-while-calling - 雙 Agent 架構
`chapter10/use-computer-while-calling/`（📖 完整程式碼已獨立為 [19PINE-AI/TalkAct](https://github.com/19PINE-AI/TalkAct)，本目錄僅保留說明文件）

實現電話呼叫 Agent 和電腦使用 Agent 的雙 Agent 協作架構。兩個 Agent 透過 WebSocket 直接通訊，無需協調器。電話 Agent 處理語音互動，電腦 Agent 執行瀏覽器自動化，並行工作完成需要語音和網頁操作的複雜任務。

**核心特性**：
- 直接 Agent 間通訊（無協調器）
- 標準工具呼叫進行訊息傳遞
- 並行操作：語音對話 + 瀏覽器自動化
- 簡單的 JSON 訊息協定

**架構元件**：
- Phone Call Agent（Node.js）：語音 I/O、ASR/TTS、LLM 對話
- Computer Use Agent（Python）：瀏覽器自動化、browser-use、網頁抓取
- WebSocket 通訊：Agent 間直接訊息傳遞

**核心概念**：多 Agent 協作、Agent 間通訊、並行任務處理、語音+瀏覽器整合

### staged-system-prompt - 按執行階段切換系統提示詞
`chapter10/staged-system-prompt/`

同一個 Coding Agent 在任務不同執行階段（需求澄清 → 程式碼實現 → 程式碼審查）載入不同的系統提示詞與工具集，從而在一段對話裡扮演不同角色、表現不同行為，而對話歷史與任務狀態在階段間連續共享，審查不透過還可回退到實現階段。

**核心概念**：階段化提示詞、角色切換、共享上下文、階段流水線

### multi-role-transfer - 多角色轉換與自主移交
`chapter10/multi-role-transfer/`

演示共享上下文下的鏈式移交（handoff）：一個會話裡存在多個專業角色 Agent，各有獨立系統提示詞與專屬工具集，透過 `transfer_to_agent` 工具由 Agent 根據任務進展自主判斷該切換到哪個角色；因共享同一段對話歷史，移交時完整上下文天然保留。

**核心概念**：角色移交、handoff、共享上下文、自主切換

### book-translation - 書籍翻譯 Agent（管理者模式）
`chapter10/book-translation/`

用管理者模式（Orchestration）把長文件翻譯拆給術語表/翻譯/審校等專職 Agent：Manager 只儲存任務、計畫、呼叫記錄和檔案索引，完整譯文全部落盤，因此上下文基本恆定；並對比單 Agent 方案，用真實 token 數說明如何控制上下文膨脹、用共享術語表保證全書一致。

**核心概念**：管理者模式、上下文隔離、上下文膨脹控制、共享術語表

### parallel-web-research - 並行多源資訊蒐集 Agent
`chapter10/parallel-web-research/`

演示多個同構 Agent 的並行搜尋 + 中心協調：主協調器同時啟動 N 個子 Agent 各訪問一個來源找答案，一旦某個命中目標其餘立即優雅停止。訊息匯流排、並行派發、即時監控、級聯終止與競態處理均為真實實現（用可控模擬資訊源代替真實瀏覽器）。

**核心概念**：並行 Agent、中心協調、訊息匯流排、級聯終止

### voice-werewolf - 語音狼人殺 Agent 系統
`chapter10/voice-werewolf/`

用多 Agent 狼人殺演示「上下文不共享」下的資訊權限控制：每個玩家是獨立 LLM Agent 且維護嚴格隔離的私有上下文，由程式碼驅動的確定性法官決定每條資訊投遞進哪些玩家上下文並登記審計，遊戲結束自動校驗隔離是否正確。語音為可選增強。

**核心概念**：資訊不對稱、私有上下文隔離、法官編排、審計校驗

## 📖 學習建議

### 核心理念：Agent = 模型 + 上下文 + 工具

本書的核心框架是 **Agent = 模型 + 上下文 + 工具**，這三個元件相互協作，共同實現 Agent 的智慧行為：

- **模型（Model）**：Agent 的大腦，提供理解、推理和決策能力
- **上下文（Context）**：Agent 的作業系統，包含系統指令、對話歷史、推理過程、工具互動記錄等
- **工具（Tools）**：Agent 的雙手，讓 Agent 能夠感知環境、執行操作、與外部世界互動

### 學習路徑

學習路徑與全書章節一一對應，圍繞三大支柱層層展開：

- **第 1 章 · 基礎篇**：建立對 Agent 系統的完整認知框架——理解 RL 中的 Agent 定義、對比傳統 RL 與 LLM+RL 正規化的樣本效率差異、理解「模型即 Agent」的新正規化，掌握 **Agent = 模型 + 上下文 + 工具** 的核心框架。**關鍵洞察**：先驗知識的重要性超越演算法和環境。

- **第 2–3 章 · 上下文篇**：上下文是 Agent 的作業系統。第 2 章覆蓋系統提示、KV Cache 友好設計、上下文壓縮與提示工程消融；第 3 章覆蓋使用者記憶、稠密/稀疏/混合檢索、Agentic RAG、上下文感知檢索與結構化知識提取。**關鍵洞察**：完整的上下文包括系統指令、對話歷史、推理過程、工具互動記錄、使用者記憶和外部知識。

- **第 4–5 章 · 工具篇**：工具是 Agent 與世界互動的橋樑。第 4 章覆蓋感知/執行/協作三類 MCP 工具、事件觸發與非同步架構；第 5 章深入生產級 Coding Agent 的完整實現。**關鍵洞察**：工具設計應通用化（程式碼直譯器優於計算器），程式碼是能創造新工具的元能力。

- **第 6–7 章 · 模型篇**：如何度量與放大智慧。第 6 章覆蓋 Terminal-Bench、SWE-bench、GAIA、OSWorld、Tau2-Bench 等評估基準；第 7 章覆蓋 SFT、RL、RLHF、樣本效率等後訓練技術。**關鍵洞察**：獨立的驗證訊號比「讓模型再想一遍」更可靠；「模型即 Agent」透過 RL 把工具呼叫內化為原生能力。

- **第 8 章 · 自我進化篇**：讓 Agent 在不改權重的前提下從經驗中成長——經驗學習、工作流外化為工具、提示與觀察蒸餾進引數。**關鍵洞察**：從經驗中學習是 Agent 從「聰明」走向「熟練」的關鍵。

- **第 9–10 章 · 拓展與協作篇**：第 9 章把感知與行動從文字擴充套件到語音、GUI 與物理世界；第 10 章透過多 Agent 分工協作處理複雜任務。**關鍵洞察**：多 Agent 系統的每個設計決策都能在單 Agent 的三要素中找到對應。

### 難度分級

- **入門級**（第 1–2 章）：適合初學者，理解基本概念
- **進階級**（第 3–4 章）：需要一定程式設計基礎，涉及系統整合
- **高階**（第 5–6 章）：需要較強程式設計能力，涉及複雜系統設計
- **專家級**（第 7–8 章）：需要深度學習和訓練/自我進化經驗
- **應用級**（第 9–10 章）：綜合運用前面所學，建構實際應用

### 實踐建議

1. **動手實踐**：每個專案都設計為可獨立執行，建議親自執行並修改程式碼
2. **結合書籍**：配合本倉庫 [`book/`](book/) 中的書稿相應章節閱讀，理解理論與實踐的結合
3. **實驗對比**：多個專案包含消融研究和對比實驗，透過對比加深理解
4. **漸進學習**：從簡單專案開始，逐步深入複雜系統
5. **關注協定**：第 4 章的 MCP 伺服器專案展示了標準化工具協定，這是建構可擴充套件 Agent 的關鍵

## 🔑 API 金鑰

建議大家申請幾個平臺的 API key，方便學習：
- **Kimi**: https://platform.moonshot.cn/ 月之暗面的 Kimi 系列，長上下文與 Agent 能力強
- **智譜 GLM**: https://open.bigmodel.cn/ 智譜 AI 的 GLM 系列（GLM-4.6 等），中文能力強、價效比高，也很推薦
- **Siliconflow**: https://siliconflow.cn/ 上面有各種開源模型，包括 DeepSeek、Qwen 等
- **火山引擎**: https://www.volcengine.com/product/ark 上面有位元組的閉源模型（豆包），國內訪問延遲比較低
- **OpenRouter**: https://openrouter.ai/ 可以從國內直接訪問海外的各種閉源和開源模型，包括 Gemini 2.5 Pro、Claude 4 Sonnet、OpenAI GPT-5 等（官方 API 需要海外 IP 和支付方式，OpenAI 還需要海外身份實名認證，註冊比較麻煩）

模型選型可以參考：https://01.me/2025/07/llm-api-setup/

## 📦 附錄 · 外部倉庫獲取

出於體積與版權考慮，第 6、7、9 章用到的評測基準與訓練框架**未內建**在本倉庫，需要自行複製到對應目錄（下方為各倉庫的上游地址與本書驗證過的提交）。可將以下命令儲存為指令碼拋棄式拉取：

```bash
# 第 6 章 · 評測基準
git clone https://github.com/google-research/android_world.git         chapter6/android_world
git clone https://huggingface.co/datasets/gaia-benchmark/GAIA          chapter6/GAIA
git clone https://github.com/xlang-ai/OSWorld.git                      chapter6/OSWorld
git clone https://github.com/SWE-bench/SWE-bench.git                   chapter6/SWE-bench
git clone https://github.com/sierra-research/tau2-bench.git            chapter6/tau2-bench
git clone https://github.com/laude-institute/terminal-bench.git        chapter6/terminal-bench

# 第 7 章 · 訓練框架（bojieli/* 為本書適配的分支）
git clone https://github.com/bojieli/minimind.git                      chapter7/MiniMind-pretrain/minimind      # 實驗 7-3 從零訓 LLM
git clone https://github.com/bojieli/minimind-v.git                    chapter7/MiniMind-pretrain/minimind-v    # 實驗 7-4 從零訓 VLM（投影層）
git clone https://github.com/bojieli/AdaptThink.git                    chapter7/AdaptThink-original
git clone https://github.com/bojieli/AWorld.git                        chapter7/AWorld
git clone https://github.com/bojieli/SFTvsRL.git                       chapter7/SFTvsRL
git clone https://github.com/bojieli/verl.git                          chapter7/verl
git clone https://github.com/thinking-machines-lab/tinker-cookbook.git chapter7/tinker-cookbook
git clone https://github.com/bojieli/lighteval.git                     chapter7/Intuitor/lighteval
git clone https://github.com/19PINE-AI/rlvp.git                        chapter7/RLVP/rlvp                       # 實驗 7-14 RLVP 論文程式碼
git clone https://github.com/PRIME-RL/SimpleVLA-RL.git                 chapter7/SimpleVLA-RL/SimpleVLA-RL       # 實驗 7-13 視覺-語言-動作 RL

# 第 9 章 · 瀏覽器自動化與 Claude 示例
git clone https://github.com/browser-use/browser-use.git               chapter9/browser-use
git clone https://github.com/anthropics/claude-quickstarts.git         chapter9/claude-quickstarts

# 第 10 章 · 雙 Agent 架構（已獨立為 TalkAct 專案）+ 斯坦福 AI 小鎮
git clone https://github.com/19PINE-AI/TalkAct.git                     chapter10/use-computer-while-calling
git clone https://github.com/joonspk-research/generative_agents.git    chapter10/generative_agents             # 實驗 10-7 斯坦福 AI 小鎮
```

> 各專案 README 中如標註了特定提交（commit），請按其說明 `git checkout` 到對應版本，以保證復現結果一致。
> 第 10 章 `use-computer-while-calling` 已發展為持續維護的獨立倉庫 [19PINE-AI/TalkAct](https://github.com/19PINE-AI/TalkAct)，本倉庫僅保留一份指向它的說明文件（`chapter10/use-computer-while-calling/README.md`）。

**依賴真實硬體 / 外部環境的實驗（無本倉庫程式碼，指向上游文件）：**

- **實驗 9-8 / 9-9 · XLeRobot 遙操作與 LLM Agent 控制**：需 SO-100/XLeRobot 機械臂，按上游檔案操作—— [Teleop](https://xlerobot.readthedocs.io/en/latest/software/getting_started/XLeRobot_teleop.html) · [LLM Agent](https://xlerobot.readthedocs.io/en/latest/software/getting_started/LLM_agent.html)
- **實驗 9-10 · RGB 零樣本 Sim2Real 抓取**：[`StoneT2000/lerobot-sim2real`](https://github.com/StoneT2000/lerobot-sim2real)（模擬訓練部分可純 GPU 完成，真實部署需 SO-100 機械臂）
- **實驗 6-11 · OpenVLA + RoboTwin2 模擬評估**：VLA 訓練/環境依賴見 `chapter7/SimpleVLA-RL` 的 README（其中說明 OpenVLA、RoboTwin2 的獲取與配置）

**讀者練習類實驗（書中作為練習題給出，複用已文件化的既有專案，無專屬目錄）：**

- **實驗 5-12 · 能創造 Agent 的 Agent**：基於 `chapter5/coding-agent` 自舉擴充套件
- **實驗 6-2 / 6-3 / 6-4 / 6-9**：分別為人肉基準、記憶評估、JSON Cards vs RAG、記憶選型——改造複用第 3 章 `user-memory` / `user-memory-evaluation` / `contextual-retrieval` 等專案
- **實驗 7-8 · Prompt 蒸餾**：落地實現見第 8 章 `chapter8/prompt-distillation`（跨章複用）
- **實驗 7-9 · CoT 蒸餾 `[擴充套件]`**：書中給出實驗設計與驗收標準，作為讀者擴充套件實驗，暫無專屬程式碼

## 🤝 貢獻

本書與配套程式碼全部開源，非常歡迎社群透過 Pull Request 參與共建。以下幾類貢獻我們都非常歡迎：

1. **書籍內容改進**：勘誤、補充、更清晰的表述，或新增前沿進展（正文見 `book/chapter*.md`）
2. **程式碼改進與 Bug 修復**：讓配套專案更健壯、更易用、更貼近生產實踐
3. **新的實踐專案**：為某個實驗補充/替換更好的實現，或貢獻全新的示例專案
4. **書籍配圖的設計改進**：讓 `book/images/` 中的圖表在設計上更清晰、更美觀（配圖由 `book/gen_*_figs.py` 生成）
5. **新語言的翻譯版本**：歡迎將本書翻譯成更多語言，可參考台灣正體（`book-zhtw/`）、英文（`book-en/`）、泰米爾語（`book-ta/`）、越南語（`book-vi/`）版本的組織方式

提交前建議先把相關實驗親手跑一遍、確認可復現；也歡迎先提 issue 討論想法。

## 📄 許可證

本專案採用 [Apache License 2.0](LICENSE) 開源許可證，詳見 [`LICENSE`](LICENSE) 檔案。部分子專案可能包含各自的許可證資訊，請以子專案中的說明為準。

## ⭐ Star History

<a href="https://star-history.com/#bojieli/ai-agent-book&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/star-history-dark.png" />
    <source media="(prefers-color-scheme: light)" srcset="assets/star-history-light.png" />
    <img alt="Star History Chart" src="assets/star-history-light.png" width="720" />
  </picture>
</a>

<sub>圖表由 [`scripts/gen_star_history.py`](scripts/gen_star_history.py) 繪製（自 2026 年 7 月 15 日起），[GitHub Actions 定時任務](.github/workflows/star-history.yml) 每天自動更新並提交到 <code>assets/</code> 目錄；點選可跳轉到 star-history.com 檢視即時資料。</sub>
