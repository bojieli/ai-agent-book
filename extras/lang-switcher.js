// Language switcher: populates a <select> dropdown in the header bar.
// On change, navigates to the equivalent page in the target language and
// rewrites the left sidebar (links + text) to match the new edition.
//
// window.LANG_CONFIG = { zh: {label, prefix, default?}, ... }
// window.SITE_ROOT    = "https://bojieli.github.io/ai-agent-book"

(function () {
  "use strict";

  var cfg = window.LANG_CONFIG;
  if (!cfg) return;

  // ── nav label translations ────────────────────────────────
  // Keyed by the Chinese label in mkdocs.yml; values per target language.
  // When on a non-default language, sidebar text is replaced from this map.
  var NAV_I18N = {
    "首页":         { en: "Home",                               ta: "முகப்பு",                          vi: "Trang chủ",        zhtw: "首頁",        ja: "ホーム" },
    "引言":         { en: "Introduction",                       ta: "அறிமுகம்",                          vi: "Giới thiệu",       zhtw: "引言",        ja: "はじめに" },
    "第1章 Agent基础知识": { en: "Chapter 1 · Agent Basics",     ta: "அதி. 1 · AI ஏஜெண்ட் அடிப்படைகள்",     vi: "Chương 1 · Nền tảng AI Agent", zhtw: "第 1 章 · Agent 基礎知識", ja: "第1章 · Agent の基礎知識" },
    "第2章 上下文工程":     { en: "Chapter 2 · Context Engineering", ta: "அதி. 2 · சூழல் பொறியியல்",          vi: "Chương 2 · Kỹ thuật ngữ cảnh",   zhtw: "第 2 章 · 上下文工程", ja: "第2章 · コンテキストエンジニアリング" },
    "第3章 用户记忆和知识库": { en: "Chapter 3 · User Memory & Knowledge Base", ta: "அதி. 3 · பயனர் நினைவகம் & அறிவுத்தளம்", vi: "Chương 3 · Bộ nhớ & Cơ sở kiến thức", zhtw: "第 3 章 · 使用者記憶和知識庫", ja: "第3章 · ユーザーメモリと知識ベース" },
    "第4章 工具":           { en: "Chapter 4 · Tools",            ta: "அதி. 4 · கருவிகள்",                  vi: "Chương 4 · Công cụ",             zhtw: "第 4 章 · 工具", ja: "第4章 · ツール" },
    "第5章 CodingAgent与代码生成": { en: "Chapter 5 · Coding Agent & Code Generation", ta: "அதி. 5 · குறியீட்டு ஏஜெண்ட் & குறியீடு உருவாக்கம்", vi: "Chương 5 · Coding Agent & Tạo mã", zhtw: "第 5 章 · Coding Agent 與程式碼生成", ja: "第5章 · Coding Agent とコード生成" },
    "第6章 Agent的评估":    { en: "Chapter 6 · Evaluating Agents", ta: "அதி. 6 · ஏஜெண்ட் மதிப்பீடு",          vi: "Chương 6 · Đánh giá Agent",        zhtw: "第 6 章 · Agent 的評估", ja: "第6章 · Agent の評価" },
    "第7章 模型后训练":     { en: "Chapter 7 · Model Post-Training", ta: "அதி. 7 · மாதிரி பிந்தைய பயிற்சி",  vi: "Chương 7 · Post-training mô hình", zhtw: "第 7 章 · 模型後訓練", ja: "第7章 · モデルのポストトレーニング" },
    "第8章 Agent的自我进化": { en: "Chapter 8 · Agent Self-Evolution", ta: "அதி. 8 · ஏஜெண்ட் சுய-பரிணாமம்",    vi: "Chương 8 · Tự tiến hóa của Agent",  zhtw: "第 8 章 · Agent 的自我進化", ja: "第8章 · Agent の自己進化" },
    "第9章 多模态与实时交互": { en: "Chapter 9 · Multimodal & Real-Time", ta: "அதி. 9 · பல்முக & நிகழ்நேரம்",     vi: "Chương 9 · Đa phương thức & Thời gian thực", zhtw: "第 9 章 · 多模態與即時互動", ja: "第9章 · マルチモーダルとリアルタイム対話" },
    "第10章 多Agent协作":   { en: "Chapter 10 · Multi-Agent Collaboration", ta: "அதி. 10 · பல-ஏஜெண்ட் ஒத்துழைப்பு", vi: "Chương 10 · Đa Agent cộng tác",  zhtw: "第 10 章 · 多 Agent 協作", ja: "第10章 · マルチ Agent 協調" },
    "后记":         { en: "Afterword",                          ta: "பின்னுரை",                          vi: "Lời bạt",            zhtw: "後記",        ja: "あとがき" },
    "思考题参考答案": { en: "Reference Answers",                ta: "பதில் வழிகாட்டி",                    vi: "Đáp án tham khảo",    zhtw: "思考題參考答案", ja: "演習問題の解答例" }
  };

  // ── helpers ───────────────────────────────────────────────

  function detectLang(path) {
    var p = path.replace(/\/$/, "");
    var codes = Object.keys(cfg).sort(function (a, b) {
      return cfg[b].prefix.length - cfg[a].prefix.length;
    });
    for (var i = 0; i < codes.length; i++) {
      if (p.indexOf(cfg[codes[i]].prefix) !== -1) return codes[i];
    }
    for (var c in cfg) {
      if (cfg.hasOwnProperty(c) && cfg[c].default) return c;
    }
    return "zh";
  }

  function mapUrl(cleanPath, targetCode, currentLang) {
    if (targetCode === currentLang) return null;
    var src = cfg[currentLang];
    var dst = cfg[targetCode];
    if (cleanPath === "/" || cleanPath === "/index.html") {
      return dst.prefix + "introduction" + (dst.suffix || "") + "/";
    }
    var pp = cleanPath.replace(/^\//, "");
    var url = pp.replace(src.prefix, dst.prefix);
    if (src.suffix) url = url.split(src.suffix + "/").join("/");
    if (dst.suffix) url = url.replace(/\/$/, dst.suffix + "/");
    return url;
  }

  function siteBasePath() {
    try { return new URL(window.SITE_ROOT).pathname; } catch (_) {}
    var p = location.pathname;
    var idx = Math.max(p.indexOf("book-en/"), p.indexOf("book-ta/"), p.indexOf("book-vi/"), p.indexOf("book-zhtw/"), p.indexOf("book/"));
    if (idx === -1) return "/";
    return p.slice(0, idx);
  }

  // ── sidebar rewriting (links + text) ──────────────────────

  function rewriteSidebar(targetCode) {
    var target = cfg[targetCode];
    var defCode = null;
    for (var c in cfg) { if (cfg[c].default) { defCode = c; break; } }
    defCode = defCode || "zh";
    var defCfg = cfg[defCode];

    var defPrefix = defCfg.prefix || "";
    var tgtPrefix = target.prefix || "";
    var defSuf = defCfg.suffix || "";
    var tgtSuf = target.suffix || "";

    // Site base path with a guaranteed trailing slash ("/ai-agent-book/" or "/").
    var base = siteBasePath();
    if (base.charAt(base.length - 1) !== "/") base += "/";

    function rewritePath(href) {
      // MkDocs renders sidebar hrefs relative to the current page
      // (e.g. "../../book/chapter2/" on a book-zhtw page), so resolve
      // against the current URL before doing any prefix/suffix matching.
      var url;
      try { url = new URL(href, location.href); } catch (_) { return null; }
      if (url.origin !== location.origin) return null;
      var path = url.pathname;
      if (path.indexOf(base) !== 0) return null;
      var rel = path.slice(base.length);
      // Only rewrite links into the default edition; leave everything
      // else (e.g. the site homepage link) untouched.
      if (!defPrefix || rel.indexOf(defPrefix) !== 0) return null;
      rel = tgtPrefix + rel.slice(defPrefix.length);
      // Suffix swap (handles both .html and directory forms).
      // Source suffix is stripped; target suffix is inserted before .html or trailing /.
      if (defSuf) {
        // e.g. "chapter1.ta.html" → "chapter1.html"
        rel = rel.split(defSuf + ".").join(".");
        // also: "chapter1.ta/" → "chapter1/"
        rel = rel.split(defSuf + "/").join("/");
      }
      if (tgtSuf) {
        // e.g. "chapter1.html" → "chapter1.ta.html"
        //      "chapter1/"     → "chapter1.ta/"
        rel = rel.replace(/\.html$/, tgtSuf + ".html");
        rel = rel.replace(/\/$/, tgtSuf + "/");
      }
      return base + rel;
    }

    var links = document.querySelectorAll(".md-nav__link");
    for (var i = 0; i < links.length; i++) {
      var el = links[i];
      var href = el.getAttribute("href");
      if (href && href.charAt(0) !== "#") {
        var newHref = rewritePath(href);
        if (newHref) el.setAttribute("href", newHref);
      }

      // Always rewrite link text (regardless of href rewriting).
      var navText = el.querySelector(".md-ellipsis");
      if (navText) {
        var currentText = navText.textContent.trim();
        if (NAV_I18N[currentText] && NAV_I18N[currentText][targetCode]) {
          navText.textContent = NAV_I18N[currentText][targetCode];
        }
      }
    }
  }

  // ── render ────────────────────────────────────────────────

  function render() {
    var rawPath = location.pathname;
    var basePath = siteBasePath();
    var cleanPath = "/" + rawPath.slice(basePath.length).replace(/^\//, "");
    var activeLang = detectLang(cleanPath);
    var siteRoot = window.SITE_ROOT.replace(/\/$/, "") + "/";

    var sel = document.getElementById("lang-selector");
    if (!sel) return;
    if (sel.children.length > 0) return;

    var codes = Object.keys(cfg);
    for (var idx = 0; idx < codes.length; idx++) {
      var code = codes[idx];
      var opt = document.createElement("option");
      opt.value = code;
      opt.textContent = cfg[code].label;
      if (code === activeLang) { opt.selected = true; opt.disabled = true; }
      sel.appendChild(opt);
    }

    sel.addEventListener("change", function () {
      var target = sel.value;
      if (!target || target === activeLang) return;
      var rel = mapUrl(cleanPath, target, activeLang);
      if (rel) location.href = siteRoot + rel;
    });

    var defCode = null;
    for (var c in cfg) { if (cfg[c].default) { defCode = c; break; } }
    if (activeLang !== (defCode || "zh")) {
      rewriteSidebar(activeLang);
    }
  }

  // ── bootstrap ──────────────────────────────────────────────

  function boot() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", render);
    } else {
      render();
    }
    document.addEventListener("locationchange", render);
    var _pushState = history.pushState;
    history.pushState = function () {
      _pushState.apply(this, arguments);
      setTimeout(render, 60);
    };
  }

  boot();
})();
