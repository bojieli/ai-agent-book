---
title: 深入理解 AI Agent
description: 围绕核心公式 Agent = LLM + 上下文 + 工具,用 10 章把 AI Agent 从原理讲到工程实战的开源技术书。正文、配图、92 个配套实验全部开源。
hide:
  - navigation
  - toc
---

<div class="lp">

<!-- ══════════════════ HERO ══════════════════ -->
<section class="lp-hero lp-reveal">
  <div class="lp-hero__glow" aria-hidden="true"></div>
  <div class="lp-hero__inner">
    <span class="lp-eyebrow">开源技术书 · Apache-2.0 · 5 种语言在线阅读</span>
    <h1 class="lp-hero__title">深入理解 AI Agent</h1>
    <p class="lp-hero__sub">设计原理与工程实践 —— 用 10 章把 AI Agent 从原理讲到工程实战</p>
    <div class="lp-formula" role="img" aria-label="Agent 等于 LLM 加 上下文 加 工具">
      <span class="lp-formula__t">Agent</span>
      <span class="lp-formula__op">=</span>
      <span class="lp-formula__t">LLM</span>
      <span class="lp-formula__op">+</span>
      <span class="lp-formula__t">上下文</span>
      <span class="lp-formula__op">+</span>
      <span class="lp-formula__t">工具</span>
    </div>
    <div class="lp-cta">
      <a class="lp-btn lp-btn--primary" href="book/introduction/">
        <span class="lp-btn__ic">📖</span> 开始阅读
      </a>
      <a class="lp-btn lp-btn--ghost" href="https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.pdf">
        <span class="lp-btn__ic">📥</span> 下载 PDF
      </a>
      <a class="lp-btn lp-btn--ghost" href="https://github.com/bojieli/ai-agent-book">
        <span class="lp-btn__ic">⭐</span> GitHub Star
      </a>
    </div>
    <div class="lp-stats">
      <div class="lp-stat">
        <span class="lp-stat__num" data-target="10">10</span>
        <span class="lp-stat__label">章正文 · 从基础到生产</span>
      </div>
      <div class="lp-stat">
        <span class="lp-stat__num" data-target="92">92</span>
        <span class="lp-stat__label">配套实验 · 70+ 可独立运行</span>
      </div>
      <div class="lp-stat">
        <span class="lp-stat__num" data-target="5">5</span>
        <span class="lp-stat__label">语言 · 中 / 繁 / 英 / 泰 / 越</span>
      </div>
    </div>
  </div>
</section>

<!-- ══════════════════ 为什么读这本书 ══════════════════ -->
<section class="lp-section lp-reveal">
  <h2 class="lp-h2">为什么读这本书</h2>
  <p class="lp-lead">围绕核心公式 <b>Agent = LLM + 上下文 + 工具</b>,层层递进地把 AI Agent 从原理讲到工程实战。全书正文、配图、配套实验全部开源,欢迎亲手把实验跑一遍。</p>
  <div class="lp-features">
    <div class="lp-feature">
      <span class="lp-feature__ic lp-feature__ic--a">🧭</span>
      <h3 class="lp-feature__title">一以贯之的公式</h3>
      <p class="lp-feature__desc">用一个简洁公式统领全书,10 章都是它的展开。读完你会有一张清晰的 Agent 概念地图。</p>
    </div>
    <div class="lp-feature">
      <span class="lp-feature__ic lp-feature__ic--b">🧪</span>
      <h3 class="lp-feature__title">92 个配套实验</h3>
      <p class="lp-feature__desc">70+ 个可独立运行的项目,覆盖上下文、记忆、工具、Coding Agent、评估、后训练等主题。</p>
    </div>
    <div class="lp-feature">
      <span class="lp-feature__ic lp-feature__ic--c">🏭</span>
      <h3 class="lp-feature__title">从原理到生产</h3>
      <p class="lp-feature__desc">不止讲概念,更讲工程:KV Cache、RAG、MCP、评估、后训练、多 Agent 协作的生产级实践。</p>
    </div>
    <div class="lp-feature">
      <span class="lp-feature__ic lp-feature__ic--d">🌐</span>
      <h3 class="lp-feature__title">开源 · 持续更新</h3>
      <p class="lp-feature__desc">Apache-2.0 许可,5 种语言在线阅读,每次仓库推送后自动重新构建。</p>
    </div>
  </div>
</section>

<!-- ══════════════════ 章节速览 ══════════════════ -->
<section class="lp-section lp-reveal">
  <h2 class="lp-h2">章节速览</h2>
  <p class="lp-lead">十章层层递进,从「模型即 Agent」的新范式,一路走到多 Agent 协作的「Agent 社会」。</p>
  <div class="lp-chapters">

    <a class="lp-ch lp-ch--intro" href="book/introduction/">
      <span class="lp-ch__badge">序</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">📖 引言</span>
        <span class="lp-ch__desc">为什么写这本书 · 好的设计原则如何穿越模型迭代周期</span>
      </span>
    </a>

    <a class="lp-ch" href="book/chapter1/">
      <span class="lp-ch__badge">01</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">🚀 Agent 基础知识</span>
        <span class="lp-ch__desc">「模型即 Agent」新范式 + 核心公式;Harness 工程才是竞争力</span>
      </span>
      <span class="lp-ch__exp">4 实验</span>
    </a>

    <a class="lp-ch" href="book/chapter2/">
      <span class="lp-ch__badge">02</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">🎯 上下文工程</span>
        <span class="lp-ch__desc">上下文决定能力上限:KV Cache、提示工程、Agent Skills、上下文压缩</span>
      </span>
      <span class="lp-ch__exp">9 实验</span>
    </a>

    <a class="lp-ch" href="book/chapter3/">
      <span class="lp-ch__badge">03</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">📚 用户记忆和知识库</span>
        <span class="lp-ch__desc">跨会话记住用户、接入外部知识:用户记忆、RAG、结构化索引、知识图谱</span>
      </span>
      <span class="lp-ch__exp">13 实验</span>
    </a>

    <a class="lp-ch" href="book/chapter4/">
      <span class="lp-ch__badge">04</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">🛠️ 工具</span>
        <span class="lp-ch__desc">工具是 Agent 的双手:MCP 协议、感知/执行/协作三类工具、异步 Agent</span>
      </span>
      <span class="lp-ch__exp">7 实验</span>
    </a>

    <a class="lp-ch" href="book/chapter5/">
      <span class="lp-ch__badge">05</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">💻 Coding Agent 与代码生成</span>
        <span class="lp-ch__desc">代码是「能创造新工具的工具」,生产级 Coding Agent 全景</span>
      </span>
      <span class="lp-ch__exp">12 实验</span>
    </a>

    <a class="lp-ch" href="book/chapter6/">
      <span class="lp-ch__badge">06</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">🎯 Agent 的评估</span>
        <span class="lp-ch__desc">把表现变成可比较信号:评估环境、指标、统计显著性</span>
      </span>
      <span class="lp-ch__exp">11 实验</span>
    </a>

    <a class="lp-ch" href="book/chapter7/">
      <span class="lp-ch__badge">07</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">🧠 模型后训练</span>
        <span class="lp-ch__desc">SFT、强化学习——把 Harness 中积累的反馈信号写入模型参数</span>
      </span>
      <span class="lp-ch__exp">16 实验</span>
    </a>

    <a class="lp-ch" href="book/chapter8/">
      <span class="lp-ch__badge">08</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">🌱 Agent 的自我进化</span>
        <span class="lp-ch__desc">外部化学习、工具创造、经验积累——Agent 自己变得更聪明</span>
      </span>
      <span class="lp-ch__exp">6 实验</span>
    </a>

    <a class="lp-ch" href="book/chapter9/">
      <span class="lp-ch__badge">09</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">🎙️ 多模态与实时交互</span>
        <span class="lp-ch__desc">语音 Agent、Computer Use、机器人操作</span>
      </span>
      <span class="lp-ch__exp">7 实验</span>
    </a>

    <a class="lp-ch" href="book/chapter10/">
      <span class="lp-ch__badge">10</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">🤝 多 Agent 协作</span>
        <span class="lp-ch__desc">协作架构、失败模式、涌现的「Agent 社会」</span>
      </span>
      <span class="lp-ch__exp">7 实验</span>
    </a>

    <a class="lp-ch lp-ch--intro" href="book/afterword/">
      <span class="lp-ch__badge">尾</span>
      <span class="lp-ch__body">
        <span class="lp-ch__title">📝 后记</span>
        <span class="lp-ch__desc">模型会不会吃掉 Harness?完整答案与展望</span>
      </span>
    </a>

  </div>
</section>

<!-- ══════════════════ 多语言 ══════════════════ -->
<section class="lp-section lp-reveal">
  <h2 class="lp-h2">在线阅读 · 多语言</h2>
  <p class="lp-lead">使用顶部导航栏的语言切换器,在不同语言版本之间切换。中文为原版,其余为社区翻译(可能滞后于原版)。</p>
  <div class="lp-langs">
    <span class="lp-lang lp-lang--primary">🇨🇳 中文 <em>原版</em></span>
    <span class="lp-lang">🇹🇼 正體中文 <em>社区翻译</em></span>
    <span class="lp-lang">🇬🇧 English <em>社区翻译</em></span>
    <span class="lp-lang">🇮🇳 தமிழ் <em>社区翻译</em></span>
    <span class="lp-lang">🇻🇳 Tiếng Việt <em>社区翻译</em></span>
  </div>
</section>

<!-- ══════════════════ 结尾 CTA ══════════════════ -->
<section class="lp-cta-band lp-reveal">
  <div class="lp-cta-band__inner">
    <h2 class="lp-cta-band__title">现在就开始读吧</h2>
    <p class="lp-cta-band__sub">正文、配图、92 个配套实验全部开源 · 每次推送后自动重新构建</p>
    <div class="lp-cta">
      <a class="lp-btn lp-btn--primary" href="book/introduction/"><span class="lp-btn__ic">📖</span> 开始阅读</a>
      <a class="lp-btn lp-btn--ghost" href="https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.epub"><span class="lp-btn__ic">📚</span> 下载 EPUB</a>
      <a class="lp-btn lp-btn--ghost" href="https://github.com/bojieli/ai-agent-book"><span class="lp-btn__ic">⭐</span> GitHub</a>
    </div>
    <p class="lp-meta">仓库 <a href="https://github.com/bojieli/ai-agent-book">bojieli/ai-agent-book</a> · 许可证 Apache-2.0 · <a href="https://github.com/bojieli/ai-agent-book/releases">Releases</a></p>
  </div>
</section>

</div>
