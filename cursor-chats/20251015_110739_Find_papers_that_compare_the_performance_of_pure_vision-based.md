# Cursor Chat: ai-agent-book

## Metadata
- **Project**: ai-agent-book
- **Path**: `/Users/boj`
- **Date**: 2025-10-15 11:07:39
- **Session ID**: `fe8748b4-6a0b-474b-98d4-bce37f0e64dc`

## Conversation

### 👤 You

Find papers that compare the performance of pure vision-based and a11y + vision-based GUI operation agents (computer use or mobile use). Is there any evidence that a11y + vision-based is better?

---

### 🤖 Cursor Assistant

I'll search for research papers comparing pure vision-based and accessibility+vision-based GUI operation agents.

---

### 🤖 Cursor Assistant

Based on my extensive search, I found some interesting insights about this comparison, though the findings may not be what you expected:

## Key Finding: Limited Direct Comparisons

**There appear to be no published papers that directly compare pure vision-based vs. accessibility+vision-based GUI operation agents** in a controlled study. This is a notable gap in the literature.

## Current Research Landscape

### 1. **Pure Vision-Based Approaches (Recent Trend)**

The recent trend actually shows **pure vision-based agents performing surprisingly well**:

- **UGround** (arXiv:2410.05243): This paper argues for a "human-like" approach where agents rely solely on visual perception. Notably, it claims their vision-only agents **outperformed state-of-the-art agents that used additional text-based inputs** (like HTML or accessibility trees) by up to 20%.

- **Aguvis** and **OmniParser** (Microsoft Research): Both demonstrate state-of-the-art performance using pure vision-based approaches, suggesting that with proper visual grounding models, vision-only can be highly effective.

### 2. **Arguments Against Accessibility Trees**

The UGround paper specifically mentions challenges with accessibility/text-based approaches:
- Noise and incompleteness in accessibility trees
- Increased computational overhead
- Platform dependency issues

### 3. **Accessibility-Enhanced Work**

- **AccessFixer** (arXiv:2502.15142): Focuses on using R-GCN with accessibility data to fix GUI accessibility issues (81.2% success rate), but this is about fixing interfaces for users with disabilities, not comparing agent performance.

## What's Missing?

There's a clear **research gap**: No rigorous ablation studies comparing:
- Vision-only vs. Vision+A11y tree
- Vision-only vs. Vision+DOM/HTML
- Vision-only vs. Vision+XML (for mobile)

## My Assessment

Interestingly, the evidence suggests the field may be moving **toward** pure vision-based approaches rather than multimodal (vision+a11y) approaches. This contradicts the common intuition that "more information is better." However, this could be because:

1. Recent vision-language models have become much more capable
2. Accessibility trees can be noisy/incomplete in practice
3. Vision-only is more platform-agnostic

**Would you like me to look into specific benchmarks (like ScreenSpot, AndroidWorld, OSWorld) to see if they report different modality results, or search for any specific agent papers you have in mind?**

---

### 👤 You

Yes, look into the specific benchmarks

---

### 🤖 Cursor Assistant

I'll search for specific benchmark papers and their reported results comparing different input modalities.

---

### 👤 You

Is there any papers on XML 辅助视觉提升成功率 for mobile using agents?

---

### 🤖 Cursor Assistant

I'll search for papers specifically about mobile agents that show XML (view hierarchy) assisting vision to improve success rates.

---

### 🤖 Cursor Assistant

Based on my extensive search, here's what I found regarding XML-assisted vision for mobile agents:

## **Key Finding: No Evidence Supporting XML+Vision > Vision-Only**

**I could not find any published papers demonstrating that XML (view hierarchy) + vision outperforms pure vision-based approaches for mobile agents.** In fact, the research trend suggests the opposite.

## Current Research Landscape

### **1. Dominant Trend: Pure Vision Approaches**

Recent papers **explicitly avoid** using XML/view hierarchy:

- **Mobile-Agent** (arXiv:2401.16158): Emphasizes that it does NOT use XML files or system metadata, positioning this as an **advantage** for better cross-platform adaptability
  
- **Aria-UI**: Pure vision approach achieving 82.4% accuracy on ScreenSpot benchmark across computers and mobile devices

- **UGround** (mentioned earlier): Claims vision-only agents **outperform** agents using additional text-based inputs by up to 20%

### **2. Arguments Against XML/Structured Data**

The research literature suggests XML/accessibility trees have **disadvantages**:
- Adds noise and incompleteness
- Platform-dependent (requires system-specific customization)
- Increased computational overhead
- Not always available or reliable

### **3. Why This Matters**

The trend toward pure vision may be driven by:
1. **Recent VLM capabilities**: GPT-4V, Gemini, Claude 3.5 with strong visual grounding
2. **Real-world robustness**: Vision works across any platform/app
3. **Simplicity**: No need to parse/maintain XML structures

## What's Missing?

There's a **clear research gap**: No rigorous ablation studies showing:
- ❌ XML+Vision vs Vision-only performance comparison
- ❌ When/why XML information helps (if at all)
- ❌ Specific scenarios where structured data complements vision

## My Assessment

**The evidence suggests pure vision approaches are currently considered superior to multimodal (vision+XML) approaches in mobile agent research.** This is counterintuitive but appears to be the consensus based on recent 2023-2024 papers.

If you're writing about this topic, you might want to note this as a surprising finding or a potential research opportunity to explore whether there are specific cases where XML could help despite the current trend.

---


*Exported from [Cursor View](https://github.com/saharmor/cursor-view)*