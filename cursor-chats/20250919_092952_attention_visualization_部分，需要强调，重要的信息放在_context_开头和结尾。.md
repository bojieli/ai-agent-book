# Cursor Chat: ai-agent-book

## Metadata
- **Project**: ai-agent-book
- **Path**: `/Users/boj`
- **Date**: 2025-09-19 09:29:52
- **Session ID**: `81cd0b9e-50f1-4b3e-8f5a-61257dfc68a7`

## Conversation

### 👤 You

attention visualization 部分，需要强调，重要的信息放在 context 开头和结尾。

系统提示技术的理论基础 部分，不要讲元认知，而要讲任务规划，侧信道信息，以及世界当前状态的感知。另外需要回顾，重要的信息放在 context 结尾，也就是系统提示，这就是为什么要把这些信息补充在 agent trajectory 的结尾。

任务规划就是 TODO list，防止 agent trajectory 太长，仅仅关注当前的局部任务，而忘记了用户的原始诉求和任务约束，忘记了后面还有多少事要办。

侧信道信息包括事件发生的时间、用户当时的地点等等，是加在每个事件（用户输入和 tool result）

世界当前状态的感知包括当前的时间，系统的环境信息（例如系统信息、当前目录），异常操作提醒，以及从隐式状态到显式状态的转换。隐式状态是指根据 agent trajectory 可以提取出的信息，但 LLM 每次都从隐式状态中重新提取信息，效率低下，且容易出错。例如，机器人之前执行一些动作之后，现在什么位置，身体是什么姿态，手里现在有什么东西；已调用的工具次数、任务进展、系统环境；如果一个工具重复执行多次，需要有异常操作提醒。

---

### 🤖 Cursor Assistant

Of course. I will update the sections on "Attention Visualization" and "Theoretical Basis of System Prompt Technology" in `book/chapter2.md` to incorporate your feedback.

First, I will read the existing content of `book/chapter2.md` to understand its current structure.

---

### 🤖 Cursor Assistant

Okay, I will update `book/chapter2.md` based on your instructions. Here is my plan:

First, I will create a task list to track the changes you requested. Then, I will address the "Attention Visualization" section by adding a point about the importance of placing critical information at the beginning and end of the context. After that, I will rewrite the "Theoretical Basis of System Prompt Technology" section to incorporate your feedback on task planning, side-channel information, and world state perception, while also removing the concept of metacognition.

---

### 🤖 Cursor Assistant

I have updated the `book/chapter2.md` file as you requested.

First, I added a note to the "Attention Visualization" section, highlighting the tendency of language models to recall information more accurately when it is placed at the beginning or end of the context. This emphasizes the importance of strategic information placement within the context window.

Second, I have completely rewritten the "Theoretical Basis of System Prompt Technology" section. The revised text removes the previous discussion on metacognition and instead focuses on the concepts you specified: task planning, the inclusion of side-channel information, and the agent's perception of the current world state. I also included a concluding paragraph that links these concepts back to the attention mechanism, explaining that these critical hints are placed at the end of the agent's trajectory to maximize their impact on the model's reasoning process.

I believe these changes align with your instructions. Please let me know if there is anything else I can assist you with.

---

### 👤 You

再者是**对世界当前状态的感知**。这包括几个层面。一是**动态环境信息**，如当前的系统时间、操作系统环境、当前工作目录等，这些信息帮助 Agent 做出与环境适配的决策。二是**异常操作提醒**，例如，当一个工具被重复调用多次且持续失败时，系统会明确提示"该工具已连续失败 N 次"，这种显式的提醒能有效帮助模型跳出无效循环，调整策略。三是**从隐式状态到显式状态的转换**。Agent 的许多状态信息（如机器人执行一系列动作后的物理位置和姿态、已调用工具的次数、任务的总体进展）都隐含在长长的轨迹中。每次都让模型从头重新推断这些信息，不仅效率低下，而且容易出错。系统提示技术通过计算将这些隐式状态提取出来，并以结构化的形式明确地展示给模型，极大地降低了模型的认知负荷。

这一段可以补充上，跟命令行和 GUI 的设计原则一致，好的命令行和 GUI 也都是让人类用户清晰地感知到当前状态

---

### 🤖 Cursor Assistant

Of course. I will add a sentence to the paragraph on "Perception of the Current State of the World" to draw a parallel with the design principles of command-line and graphical user interfaces.

---

### 🤖 Cursor Assistant

Excellent point. I have updated the paragraph on "perception of the current state of the world" to include the analogy to command-line and graphical user interfaces. The text now explains that making the system state explicit for the AI Agent follows the same design principles as effective user interfaces, which aim to provide clarity and enable better decision-making for human users.

If you have any other suggestions, please let me know.

---


*Exported from [Cursor View](https://github.com/saharmor/cursor-view)*