# Getting Started with AI Agents

If you've used Cursor to write code and watched it search your codebase, edit multiple files, and rerun tests until they pass; used Deep Research on a topic and watched it search, read, and search again until a complete report takes shape; had Manus drive a browser to finish online tasks for you; asked the Doubao phone assistant to book tickets or send messages; or sent Pine AI to call your telecom provider and negotiate your bill down—you've already been using AI Agents.

These products take many forms, but they share one trait: they are no longer the passive "you ask, it answers" kind of conversation. They plan their own execution steps, call whatever tools the task requires, and adjust strategy as results come in. AI Agents are becoming a new way for us to interact with computers.

This chapter starts from practice and works toward the core components of an AI Agent: we'll experience firsthand what modern Agents can do, understand the architecture behind them, and pick up the design patterns and best practices for building Agent systems.

> **Reading Tip**: This chapter is the conceptual map for the whole book—a quick pass through the core formula, the operating loop, the engineering framework, and the design patterns of Agents, establishing the shared vocabulary and reference points that later chapters build on. Don't try to memorize every concept on a first read; aim for a general impression. Each later chapter expands on one aspect introduced here, and you can always come back to check your bearings.

## Modern Agent = LLM + Context + Tools

The essence of a modern Agent system fits into one concise formula: **Agent = LLM (Large Language Model) + Context + Tools**. The formula is simple and practical—provided each term is read broadly:

- **LLM is the Agent's brain**: Not just a set of model parameters, but the Agent's entire decision-making core—it understands intent, thinks, plans, and judges. Just as a human brain is more than a collection of neurons—it also carries ways of thinking shaped by experience—an LLM's capability comes from two sources: the world knowledge and language ability accumulated through **pre-training**, and the decision-making strategies solidified through **post-training** (whose techniques, such as supervised fine-tuning and reinforcement learning, are the subject of Chapter 7).
- **Context is the Agent's eyes**: Not just the text fed into the model, but everything the Agent can see at each decision point—the environment, user memory, domain knowledge, its own state, and task progress. Just as a person making a decision needs to size up the situation, recall relevant experience, and consult references, the Agent's context window is everything it can see at that moment.
- **Tools are the Agent's hands and feet**: Not a handful of callable API functions, but the full set of things the Agent can do—from predefined tool calls to skills (Skills) loaded on demand, from generating code to create new capabilities on the fly to delegating work to sub-agents, from reaching out to the user to responding to external events.

Put more intuitively: **Agent = Brain + Eyes + Hands and Feet**. The brain thinks and decides, the eyes supply everything the thinking needs, and the hands and feet turn decisions into changes in the real world.

These three components correspond exactly to three core concepts in RL (see Chapter 7). The following table is **optional reading**—if you don't have an RL background, feel free to skip it; nothing later depends on it. It exists only to help readers who do know RL map that knowledge onto this book's terminology:

| Intuitive Understanding | Implementation Component | Academic Concept (Optional) | Meaning |
|---------------|----------------|------------------|---------------------------------------------|
| **Brain** | LLM | **Policy** | The decision-making logic that determines "what to do next"—given the current information, choose the most appropriate action from all available options |
| **Eyes** | Context | **Observation Space** | All the information the Agent can see—what it can see, read, remember, and which systems it can access |
| **Hands and Feet** | Tools | **Action Space** | The complete set of things the Agent can do—what "means" are available, from sending messages to executing code to controlling interfaces |

Understanding what each component does, and how they fit together, is the foundation for building effective Agent systems. We'll begin with the most concrete of the three—tools, the hands and feet—and work inward to the brain (LLM) and the eyes (context). First, here's how different kinds of Agents spread out across these three dimensions:

| Agent Product | Eyes (Perception) | Hands and Feet (Action) | Strategy |
|-----------------|------------------------|--------------------------|-----------------------------|
| **Coding Agents (e.g., Cursor)** | Requirements documents, codebase, terminal environment | Open-ended (internal reasoning, code search, file read/write, command execution, etc.) | Incremental development: understand requirements → search relevant code → edit code → test and verify → debug and fix |
| **Search Agents (e.g., Deep Research)** | Web resources, academic databases, local files | Open-ended (internal reasoning, search queries, web reading, summary generation) | Iterative deepening: adjust search direction based on existing information, gradually synthesize a complete report |
| **Computer Control Agents (e.g., Manus)** | Computer screen, browser pages, file system | Open-ended (internal reasoning, clicking, typing, scrolling, screenshots, code execution, etc.) | Visual perception + operation: observe screen → identify target elements → perform actions → verify results |
| **Phone Assistant Agents (e.g., Doubao)** | Phone screen, installed apps | Open-ended (internal reasoning, clicking, swiping, typing, opening apps, etc.) | Intent understanding + App control: understand user needs → locate target app → perform actions → confirm completion |
| **Personal Task Agents (e.g., Pine AI)** | User account information, historical bills, service provider knowledge base | Open-ended (internal reasoning, making calls, sending emails, filling forms, confirming with user) | Multi-step task execution: gather information → formulate negotiation strategy → contact service provider → negotiate → report results |

These systems share three features: an **open-ended action space**—not picking from a fixed set of buttons but generating arbitrary natural language and code; **internal thinking**—planning and reasoning before acting; and **continuous interaction**—adjusting strategy on environmental feedback. These capabilities come precisely from the interplay of brain, eyes, and hands and feet—that is, LLM, context, and tools.

### Tools: The Agent's Hands and Feet

Tools are the Agent's bridge to the outside world. Like human hands and feet, they turn the Agent from a passive observer into an active doer. Without tools, an Agent is all talk; with them, it can actually change the world.

To discuss tools systematically, we can sort them into five types by the direction of the Agent's interaction with the world. For now, a quick pass through each type's representative scenarios is enough to form an impression; later chapters treat each in depth.

**Perception Tools** allow the Agent to access information: search engines provide real-time web data, file systems read local documents, and APIs and databases connect to external services and enterprise core data.

**Execution Tools** allow the Agent to change the world: code execution, file operations, system commands, external API calls—decisions are thus transformed into concrete actions.

**Collaboration Tools** allow the Agent to divide work with other Agents: delegating specialized tasks to sub-agents, requesting human confirmation at key decision points, or coordinating actions in multi-agent systems.

**Event Trigger Tools** are invoked in a fundamentally different way from the first three categories: the Agent doesn't call them—they arrive as external inputs that set the Agent to work. A new email comes in, a scheduled time arrives, another system fires a Webhook callback—the event activates the Agent and kicks off its thinking and action. The Agent never calls these itself, yet they are still a channel through which it meets the outside world, so we count them in the broad tool system.

**User Communication Tools** are the channels through which the Agent reaches out to the user. Where execution tools change the external world, communication tools carry information—delivering the Agent's progress, or a proactive check-in, by text message, voice call, email, and so on.

Chapter 4 covers the full taxonomy and design principles for these five types. The quality of tool design directly determines how far an Agent can go: define interfaces vaguely and the model will misuse them; handle errors poorly and a single failed tool can deadlock the Agent; scope permissions too broadly and one Agent mistake becomes irreparable. As the MCP (Model Context Protocol) standard spreads, wiring up a tool is becoming as easy as installing a plugin—the ecosystem is expanding rapidly, but the design principles won't go out of date.

**Tool Calling** (also known as Function Calling) is a core capability of modern LLM Agents: it lets the model invoke external tools in a structured way, transforming the LLM from a pure text generator into an intelligent system that can take real action. This book uses the term "tool calling" throughout.

Tool calling takes four steps: first, the context tells the model which tools are available (names, purposes, parameters); then the model decides on its own whether to call a tool, which one, and with what arguments; next, once the tool has run, its result is appended to the context; finally, the model decides its next move based on that result. This loop is the foundation of ReAct, introduced later in the chapter.

Taking a weather query scenario as an example, the simplified representation of the four-step process at the API level is as follows:

```
Step 1: Declare tools                  Step 2: Model decides to call
tools: [{                             assistant: {
  name: "get_weather",                  tool_calls: [{
  parameters: {                           function: "get_weather",
    city: "string"                        arguments: {city: "Beijing"}
  }                                      }]
}]                                    }

Step 3: Result appended to context    Step 4: Model responds based on result
tool: {                               assistant: {
  tool_call_id: "call_1",               content: "Today in Beijing: 28°C, sunny."
  content: '{"temp":28,"sky":"clear"}'     }}
```

The developer only defines the tools and executes the calls; the model itself decides whether to call, which to call, and what arguments to pass. Chapter 2 examines this API structure in detail.

When designing tools for an Agent, keep them general-purpose—give the LLM room to maneuver. Instead of a dedicated calculator tool, provide a Python code interpreter and a secure sandbox to run it in. Instead of a special tool for logging work notes, provide file read/write tools and a virtual file system. General-purpose tools let the Agent combine basic capabilities to solve problems creatively.

### LLM: The Agent's Brain

The Large Language Model (LLM) is the Agent's decision-making core. Given a user request, it first has to work out the real intent (what users say is often not what they actually want), then break a vague or complex task into executable steps. Throughout execution it keeps making judgment calls: what to do next, whether to call a tool, which one, with what arguments. This understand–plan–execute capability comes from knowledge accumulated during pre-training, and it is the foundation that workflows and autonomous Agents alike depend on.

A distinctive capability of LLM Agents is **internal reasoning**—before acting, the Agent can plan and think things through. This changes nothing in the external environment, yet it markedly improves the actions that follow. What makes such reasoning effective is pre-training (the initial training on massive amounts of internet text, through which the model learns language patterns and world knowledge): the model reasons along logical rules already distilled into human knowledge—mathematical laws, causal relationships, strategies for decomposing problems. An Agent's reasoning is therefore not blind trial and error; it unfolds on top of a structured body of knowledge.

This structured reasoning lets an LLM Agent take on entirely new tasks cold—two concepts, zero-shot and few-shot, make the point. The direct manifestation is **Zero-shot Generalization**: facing a task it has never seen, the Agent handles it by recombining what it already knows, no examples needed. Nobody ever taught it to write a poem about quantum physics, yet it can produce a respectable one from its existing knowledge of language and physics.

Going further, an LLM Agent can manage **Few-shot Adaptation**: two or three demonstrations in the prompt are enough for it to pick up a new task pattern. Show it a few "user comment -> sentiment label" examples and it can classify the sentiment of new comments. In short: zero-shot is "can do it with no examples"; few-shot is "can learn it from a handful."

#### Model as Agent: When the Model Itself Becomes the Product

The "Model as Agent" paradigm is the newest direction in AI Agent development. Advanced models internalize tool calling as a native ability through post-training (especially reinforcement learning): when to call a tool, which one, with what arguments—the model decides all of it, no manual orchestration required. That does not make the framework layer less important. Quite the opposite: the stronger the model, the more the Harness built around it matters. A harness is, literally, the tack fitted to a horse—reins and all—there not to keep the horse from running but to steer that power in the right direction. In the Agent context, the model is the powerful but unpredictable horse, and the Harness is the engineering shell that channels its capability into reliable task execution. Or picture the support system around a race car driver: seatbelt, track barriers, pit crew. The faster the driver (the model), the more that system matters. In an Agent, the Harness comprises infrastructure such as context management, tool interfaces, safety constraints, and verification and correction mechanisms (see the final section of this chapter).

The more room a model has to decide for itself, the more damage a wrong decision can do—which calls for finer-grained constraint, verification, and correction to keep it reliable. The real advantage of the model vendors is not "making the framework thinner" but being able to co-optimize the model and its surrounding Harness, iterating continuously.

But a deeper question hangs over this: if models keep getting stronger, will today's Harness eventually be "eaten" by the model? In "The Bitter Lesson", Rich Sutton looked back on a scene replayed throughout seventy years of AI research<sup>[[1]](#ref-^ch1-1)</sup>: researchers encode their understanding of a domain into the system—effective in the short run, yet always beaten in the long run by general methods that scale with compute and data: search and learning. Measured by this, how much of the constraint, verification, and correction in a Harness is "human prior" that the model is destined to internalize? This book's stance: **endorse the direction, stay pragmatic about the pace**. On direction, we do not doubt that models will keep eating the Harness—tool calling and long-horizon planning were once external orchestration and are now native capabilities. But on pace, this "eating" is far slower than intuition suggests: training takes months, and a model cannot internalize all the constraints and preferences of real business in one pass; the model's capability boundary of the moment is exactly the Harness's value of the moment. Harness engineering is therefore not a resistance to the Bitter Lesson but its practice on an engineering timescale: whatever the model cannot yet do reliably, the Harness covers first; every layer the model internalizes, the Harness sheds, moving on to backstop the new capability frontier. This thread runs through the whole book—Chapter 2 gives the pragmatic answer from the angle of context engineering, Chapter 8 discusses how an Agent can discover structures of knowledge and capability on its own, and the Afterword returns to the complete answer to "will models eat the Harness."


#### Agent Learning Mechanisms: Post-training, In-context Learning, and Externalized Learning

We've just seen how reinforcement learning lets a model internalize tool calling. But an Agent's learning is not confined to the training phase—many readers, the moment they think of an Agent learning from experience, assume the model must be retrained. In fact, post-training is only one way for an Agent to learn from experience. Its learning mechanisms fall into three complementary paradigms (Figure 1-1):

![Figure 1-1: Three learning paradigms of an Agent](images/fig1-1.svg)

- **Post-training**: Solidifies experience into the model’s parameters through reinforcement learning—the strongest cross-task generality, at the highest update cost (see Chapter 7).
- **In-Context Learning**: Adapts on the fly through pattern retrieval within the context, powered by the attention mechanism (how the model decides which parts of its input to focus on). Show the model a few worked examples of customer service handling in the prompt (say, “customer complaint → appeasement + compensation plan”) and it will handle new customer service conversations the same way—that is in-context learning. Adaptation is fast but transient: it evaporates when the session ends. And despite the name, its inner mechanism is closer to **pattern matching than true learning**. An analogy: shown three solved math problems of the same type and then a fourth, you can probably crack it by following the pattern—that is what in-context learning does. But if the fourth problem needs a genuinely new approach, staring at the first three answers won’t get you there. In other words, in-context learning lets the model **apply patterns it has already seen**, but it cannot **discover entirely new rules**—a fundamental difference from post-training (Chapter 2 develops this claim through the lens of the attention mechanism).
- **Externalized Learning**: Externalizes knowledge and procedures into knowledge bases and executable tool code—persistent and interpretable at once.

The three paradigms complement each other on different time scales: post-training provides foundational capability, in-context learning provides rapid adaptation, and externalized learning provides reliability and efficiency. Chapter 8 systematically compares how the three work in concert.

An analogy: post-training is studying a textbook—ability permanently improved, at a high cost; in-context learning is consulting a reference on the spot—you do well while it's open and forget once it closes; externalized learning is keeping a personal notebook—persistent and always at hand, but it takes deliberate upkeep.

### Context: The Eyes of the Agent

Context is everything an Agent can see at each decision point. Just as a person making a decision needs the materials spread out on the table—task instructions, reference manuals, earlier correspondence, the latest data—an Agent’s context window is its field of vision. From the API’s perspective (detailed in Chapter 2), the context of each LLM call consists of five parts:

- **System Prompt**: Unlike the prompts users type in turn by turn, the system prompt is written by the developer and stays fixed for the whole conversation. It is the Agent’s “job description”—defining its identity, permissions, and rules of conduct. Careful prompt engineering of the system prompt is how we shape the Agent’s way of working. The system prompt also carries **user memory** that persists across sessions (personalized information such as preferences, past behavior, and background settings; see Chapter 3), plus dynamically injected environmental state.
- **Tool Definitions**: Declares the names, functional descriptions, and parameter formats of the tools available to the Agent. Without tool definitions, the Agent cannot recognize or call any tools—an ablation study (Experiment 1-1) will verify this. Tool definitions, together with the system prompt, form the **static prefix** that remains unchanged throughout the conversation.
- **User Messages**: Input from the user. User messages may also contain **external knowledge** dynamically retrieved via RAG (Retrieval-Augmented Generation, see Chapter 3 for details)—covering information beyond the training data cutoff or private domain knowledge.
- **Assistant Messages**: Responses previously generated by the model, which can contain up to three parts—reasoning (the internal chain of thought, maintaining coherence and decision interpretability), content (the response to the user), and tool calls (the way the Agent takes action). In a specific response, these three parts may not all appear simultaneously: for example, when the Agent decides to call a tool, it usually only has reasoning + tool_calls; when giving a final answer, it usually only has reasoning + content.
- **Tool Results**: What comes back after the Agent framework executes a tool. These results are the direct basis for the Agent’s next step of thinking—and what lets it learn from outcomes rather than repeat its mistakes.

The first two items (system prompt + tool definitions) form the static prefix; the last three (user messages + assistant messages + tool results) form the dynamic message history that grows with every interaction. Together, these five parts make up the context of each LLM inference.

Is every component truly indispensable? The most direct way to find out is an **ablation study**—the diagnostic method of ruling out causes one at a time: remove component A and see whether the system still works, then component B, and so on, until each component’s contribution is clear. Experiment 1-1 applies exactly this method to the five components above. The results: remove tool definitions and the Agent is completely incapable of action; remove tool results and it cannot see the previous step’s feedback, so it calls the same tool again and again, stuck in an infinite loop; strip the reasoning out of the assistant messages and consecutive decisions start contradicting each other; drop the message history and the Agent is effectively amnesiac—it restarts the whole task from the beginning, repeating steps already done. Each component’s role rests on experimental evidence, not just theoretical inference.

### Experiment 1-1 ★★: The Critical Role of Context

We probed how each context component shapes Agent behavior with a systematic **ablation study**. Of the five components above, four were tested—the system prompt, as the Agent’s basic identity definition, was exempt: without it the Agent has no role awareness at all, and the test would be meaningless. As Figure 1-2 shows, the experiment ran five controlled groups: a complete baseline retaining every component, plus four groups each missing one, to observe each component’s effect on Agent performance.

![Figure 1-2: Experiment 1-1—Context ablation study design](images/fig1-2.svg)

The experimental results revealed the irreplaceable role of each context component. **Tool Definitions** (part of the static prefix) are the foundation of the Agent’s action capability; without them, the Agent cannot recognize or call any tools. **Tool Results** are key to closed-loop control; their absence causes the Agent to act “blindly” and fall into an infinite loop. The **reasoning process** (the reasoning part of assistant messages) preserves the reasons for the Agent’s previous decisions, making the thought process more coherent and preventing contradictory decisions. **Message history** (user messages, assistant messages, and tool results from previous rounds) prevents redundant operations, maintains task execution coherence, and avoids repeating the same mistakes.

The experiment’s core insight: **context determines what the Agent can see, and the Agent can only decide based on what it sees**. Just as a blindfolded person cannot make sound judgments, an Agent missing any context component suffers a severe loss of decision-making ability—without tool definitions it doesn’t know what tools exist; without previous execution results it doesn’t know what has already been done.

### The ReAct Loop

With the three components in hand, a natural question follows: how do they work together? The ReAct loop is the core mechanism that strings LLM, context, and tools into one system—let’s watch an Agent think and act, step by step.

The core pattern by which an Agent executes a task is called **ReAct** (Reasoning + Acting). The name mentions only reasoning and acting, but the actual loop has three stages: the model first **reasons** about what to do next, then calls a tool to **act**, then **observes** the tool’s result and reasons about the step after that. This “think → do → see → think → do → see” loop repeats until the task is done.

Let’s follow a concrete example—aggregating revenue across multiple currencies—to understand an Agent’s **trajectory**: the message history that accumulates as the Agent works, comprising user messages, assistant messages (with their reasoning and tool calls), and tool results. On every LLM call, the complete context the model receives is the **static prefix** (system prompt + tool definitions) plus the **trajectory** (dynamic message history) (Figure 1-3). This reveals a key fact: **Agent context = static prefix + trajectory**. Concretely, the static prefix is the first two of the five components above (system prompt + tool definitions); the trajectory is the last three (user messages + assistant messages + tool results, growing with each interaction). From this complete context the LLM generates its next response, which is then appended to the trajectory for the call after that.

![Figure 1-3: Agent trajectory—ReAct loop for a multi-currency aggregation task](images/fig1-3.svg)

Here is the structure of a trajectory, in pseudocode:

```
trajectory = [
  {role: "user", content: "Based on the company's quarterly revenue: Q1 2.5M USD, Q2 2.1M EUR, Q3 1.8M GBP, Q4 380M JPY, calculate the company's total annual revenue and average quarterly revenue"},
  
  # First iteration - LLM sees the above trajectory, generates a response
  {role: "assistant",
   reasoning: "Need to convert all currencies to USD...",
   content: "",  # No direct reply to the user
   tool_calls: [
     {name: "convert_currency", args: {amount: 2100000, from: "EUR", to: "USD"}},
     {name: "convert_currency", args: {amount: 1800000, from: "GBP", to: "USD"}},
     {name: "convert_currency", args: {amount: 380000000, from: "JPY", to: "USD"}}
   ]},
  
  # Agent framework executes tools, adds results to trajectory
  {role: "tool", content: "EUR->USD: 2282608.7"},
  {role: "tool", content: "GBP->USD: 2278481.01"},
  {role: "tool", content: "JPY->USD: 2541806.02"},
  
  # Second iteration - LLM sees the complete trajectory, including tool results
  {role: "assistant",
   reasoning: "Conversion results obtained, now need to aggregate and calculate...",
   content: "",
   tool_calls: [
     {name: "code_interpreter", args: {code: "total = 2500000 + 2282608.7 + ..."}}
   ]},
  
  {role: "tool", content: "Total: $9,602,895.73, Average: $2,400,723.93..."},
  
  # Third iteration - LLM sees the complete trajectory, generates the final answer
  {role: "assistant",
   reasoning: "All calculations complete, summarizing results...",
   content: "FINAL ANSWER: Total revenue $9,602,895.73..."}
]
```

Note that the system prompt and tool definitions are not shown in the trajectory—they serve as the static prefix and are automatically prepended to the trajectory before each LLM call.

In our experiment, this loop was on full display. In the first round, the Agent analyzed the task and called three currency conversion tools in parallel; in the second, it fed the conversion results to a code interpreter for the heavier calculation; in the third, having confirmed all calculations were done, it produced the final answer. A complex multi-step task, finished in just 3 iterations and 4 tool calls.

The elegance of this design lies in the **cumulative nature of the context**. Every LLM call sees the complete trajectory, so the model knows which stage of the task it is in, what was tried before, and what came of it. Just as people keep reviewing and summarizing while solving a problem, the Agent holds a global view of the task through its trajectory. And because the trajectory is structured—user messages, assistant messages (reasoning + tool calls), and tool results all cleanly separated—the system is highly interpretable and debuggable.

The trajectory is more than an execution record; it is a mirror of the Agent’s capability. Analyzing trajectories at scale reveals behavior patterns, better decision paths, and better tool designs. Trajectory data can even be distilled into a knowledge base, or used to train stronger Agent models via reinforcement learning—closing the loop of learning from experience.

Now that we understand the Agent's operating loop, let's run two experiments to see how different models drive it.

#### Experiment 1-2 ★: Kimi K3 Native Agent Capability

This experiment demonstrates the native Agent capability of **Kimi K3**, an embodiment of the “Model as Agent” paradigm. Kimi K3, released by Moonshot AI in 2026, is a Mixture of Experts (MoE) model with approximately 2.8 trillion parameters—think of MoE as a team of experts: for each kind of problem, the system automatically calls on the few experts best suited to it rather than putting the whole team to work, gaining capability without paying for it in efficiency. It features a 1 million token context window, native visual understanding, and an always-on “thinking mode”; trained through reinforcement learning, it has internalized tool calling as a native capability and can autonomously decide on and execute tasks such as web searches.

The key observations: the model learned tool use naturally through RL training, with no extra orchestration layer; it decides for itself when to search and what to search for—genuine autonomy; it adjusts strategy dynamically as search results come in and judges on its own whether the information is sufficient. Tool use was not “taught” to the model; it was learned through repeated interaction with the environment.

Kimi K3’s standout advantage in Agent tasks is **the stability of long-chain tool calls**—it can sustain 200–300 consecutive tool calls with coherent reasoning throughout, far beyond the few dozen calls at which most models begin to degrade. K3 is optimized for long-horizon programming and Agent workloads, and was released in two variants: K3 Max (for dialogue and Agent tasks) and K3 Swarm Max (for large-scale parallel processing). As an open-source model, it matches top-tier closed-source systems on software engineering and Agent benchmarks—proof that reinforcement learning can endow a model with native Agent capability.

#### Experiment 1-3 ★: GPT-5.6 Native Deep Research Capability

The second experiment uses **OpenAI GPT-5.6** to show how an advanced model internalizes **Deep Research** as a native capability. GPT-5.6 comes in three variants—Sol (flagship frontier model), Terra (balanced model for everyday work), and Luna (fast, economical lightweight model)—all treating tool calling as native to the model, no external framework required. Its most groundbreaking feature is **Freeform Tool Calling**. Traditionally, a model calling a tool must pack every parameter into strict JSON (a structured data format)—like filling out a form with rigid formatting rules. Freeform tool calling lets the model send raw content straight to the tool (a snippet of Python code, a SQL query), skipping the format conversion entirely—more flexible and more efficient. GPT-5.6 also introduces a Verbosity parameter (controlling output detail) and a Reasoning Effort parameter (adjusting depth of thinking; Sol adds a max level for the most thorough reasoning time), letting developers tune model behavior to the complexity of the task.

GPT-5.6 possesses powerful native **web search and code interpreter** capabilities—the very core of Deep Research: the model can autonomously search the web for real-time information and write code for in-depth analysis, enabling an iterative research process of "search -> read -> analyze -> search again." For example, when faced with a question like "What is the shortest distance between the capitals of the 10 ASEAN countries?", GPT-5.6 automatically searches for the geographic coordinates of each capital, then writes Python code to calculate the great-circle distance between all pairs of capitals, ultimately identifying the closest pair. Similarly, in a task like "Search for Bitcoin's trend over the past month and perform technical analysis," it can fetch real-time price data from multiple financial data sources, use professional technical analysis libraries to calculate moving averages, RSI, MACD, and other technical indicators, generate visual charts, and provide trading recommendations.

More importantly, GPT-5.6 internalizes the design philosophy of the **OpenAI Deep Research** product at the model level, introducing an **intent clarification process**. Given a research request, GPT-5.6 does not start executing right away; it first pins down the user's true intent through a series of questions. For "Search for Bitcoin's trend over the past month and perform technical analysis," it would first ask: "Which data source do you prefer? Which technical indicators would you like analyzed?" This interactive clarification lets GPT-5.6 produce research reports that are more precise and closer to what the user actually needs.

GPT-5.6 is a mature example of "Model as Agent"—Deep Research lives inside the model, with no external orchestration framework to lean on. Its most noteworthy aspect is the intent clarification mechanism: rather than executing a task the moment it arrives, the model first confirms what the user really needs, then formulates a research strategy. The gap between "what the user said" and "what the user actually wants" gets closed before execution even begins.

Figure 1-4 illustrates the complete architecture of native tool calling under the "Model as Agent" paradigm, along with the ReAct execution process of Kimi K3 / GPT-5.6 in real-world tasks.

![Figure 1-4: "Model as Agent" Architecture—Native Tool Calling](images/fig1-4.svg)

## Harness Engineering: Competitiveness Beyond the Model

By now you understand how an Agent works at its core: an LLM runs the ReAct loop, guided by context, using tools to get the task done. The experiments above prove the basic mechanism works—and expose how fragile it is. The model may hallucinate (invent tools or parameters that don't exist), pick the wrong tool, or fail to recover from an error. Between a demo that runs and a product that's reliable lies a vast gap, and those fragilities are exactly what Harness Engineering exists to fix. The first half of this chapter answered what an Agent is; the second half answers how an Agent runs reliably in production.

The preceding sections established the core formula: **Agent = LLM + Context + Tools**. It describes the Agent's **internal composition**—what plays the brain, the eyes, the hands and feet. Harness Engineering adds a second, **engineering-implementation** view of the same system: treat the LLM as one core component (the Model), and call all the supporting code built around it the Harness. The two views are not rivals; they describe the same system at different levels of abstraction. We switch to the more general word "Model" because the principles of Harness Engineering apply to any model that can reason and call tools, not one particular kind. The core of the Harness is the original formula's "Context + Tools," plus three layers of safeguards: **Constrain** (what the Agent may and may not do), **Verify** (whether it did the thing correctly), and **Correct** (how to recover when it didn't).

Expanded as an equation, the complete production-grade composition is:

> **Agent = LLM + [Context + Tools + Constrain + Verify + Correct] = Model + Harness**

A minimal working Agent runs on LLM, context, and tools alone. To keep running reliably in production over the long haul, it needs the three outer engineering layers as well—constrain to prevent overreach, verify to catch errors, correct to recover from failures. These layers are not bolt-on "independent modules"; they are safeguards wrapped around "Context + Tools." Put differently: the minimal formula is the demo view, the expanded formula is the production view—the latter contains the former entirely and adds a safety net around it.

An example to fix the boundaries: embedding the refund policy in the context is "Context," while checking that the refund amount doesn't exceed the order total is "Constrain." Executing an API call is "Tools," while automatically retrying after the API times out is "Correct." The model supplies the underlying understanding and reasoning; the Harness guides, constrains, and amplifies those capabilities into reliable task execution. The engineering practice of designing and optimizing this infrastructure outside the model is **Harness Engineering**.

A concrete example shows what the Harness is worth. Suppose you ask an Agent to refund a user's order placed 3 days ago. **Without a Harness**: the model can't see the refund policy (no context), doesn't know which API to call (no tools), fabricates a refund result for the user (no verification), and the user discovers the refund never happened (no correction). **With a Harness**: the system prompt spells out the 7-day refund policy (context), the Agent calls the `query_order` and `process_refund` tools to do the work (tools), the framework checks that the refund doesn't exceed the order total (constrain), confirms against the database that the refund went through (verify), and automatically retries if the API call times out (correct). Same model—with and without a Harness, the results are night and day.

Returning to the harness metaphor from earlier in this chapter: a model without a Harness is like a runaway horse—immensely capable, but unable to complete tasks reliably.

More precisely, all infrastructure outside the model belongs to the Harness. The core of the Harness is Context and Tools, around which three types of engineering safeguards are built:

| Function | One-Sentence Responsibility | Relationship with Context/Tools |
|----------|-------------------------------------------|------------------------------------------|
| **Context** | Provides the model with perceptual information | Core capability |
| **Tools** | Provides the model with means of action | Core capability |
| **Constrain** | Sets behavioral boundaries—what can and cannot be done | Safety boundary built around context and tools |
| **Verify** | Automatically judges the correctness of operation results | Checking mechanism built around tool execution results |
| **Correct** | Automatically fixes or rolls back when problems are found | Recovery mechanism built around tool call failures |

Context and Tools let the Agent "get things done"—understand the task and act on it. Constrain, Verify, and Correct make sure it "doesn't do things wrong"—not something apart from Context and Tools, but the engineering that keeps them working reliably in production. And along the maturity curve of Agent products, the weight of these two groups shifts.

Early Agent frameworks focused on Context and Tools: give the model tools, give it context, let it get things done. Production-grade systems have shifted their center of gravity to Constrain, Verify, and Correct: making sure tool calls are safe, context is managed, and errors are recoverable.

Take Claude Code. The vast majority of its Harness code does Constrain, Verify, and Correct, not Context and Tools—the tools themselves (file read/write, command execution, search) are only a small part; the safeguards built around them are the true core. These mechanisms include:

- **Process State Management**: Tracks which step the Agent is currently executing
- **Multi-Layer Context Compression**: Automatically prunes information when there is too much
- **Permission Classification**: Controls which operations require user confirmation
- **Circuit Breaker**: Automatically "trips" and stops retrying when errors occur consecutively—like a fuse blowing when a short circuit occurs in a home electrical system, preventing the entire system from crashing
- **Error Recovery Mechanisms**: Catches exceptions, rolls back to the last stable state, retries, or hands off to a human

**The industry is shifting from "getting things done" to "getting things done reliably," making Harness Engineering the core competitive advantage of Agent systems.**

### From Prompt Engineering to Harness Engineering: The Evolution of Engineering Paradigms

Looking back at the development of AI application engineering, a clear evolutionary arc emerges:

**Software Engineering** is the foundation—traditional system design, architecture, testing, and deployment. **Prompt Engineering** was the first wave of innovation—improving output quality by refining the natural-language instructions fed to the model. **Context Engineering** was the second wave—the realization that optimizing the prompt alone is not enough: everything the model can see (system instructions, tool definitions, conversation history, external knowledge) has to be managed systematically. **Harness Engineering** is the current frontier—it widens the view from "what the model can see" to "what kind of system the model runs in," taking in all infrastructure outside the model: constraint mechanisms, verification methods, feedback loops, error recovery.

These four stages are not replacements but nested layers: Prompt Engineering is a subset of Context Engineering, which is a subset of Harness Engineering. Each layer widens the engineer's scope of concern and influence beyond the last. **As models converge in capability and stop being the decisive differentiator, competitive advantage shifts to the engineering outside the model.** Recent engineering practice bears this out. LangChain's work on Terminal Bench 2.0 (a benchmark evaluating an Agent's ability to complete complex tasks in a terminal environment) is a striking example: their Coding Agent improved from 52.8% to 66.5% (jumping from outside the top 30 to the top 5 on the leaderboard). What changed was not the model but the Harness—having the Agent check its own execution results, detect when it was stuck in a repetitive loop, refine its thinking strategy. OpenAI's engineering team has shared a similar experience: 3 engineers completed approximately one million lines of code and nearly 1500 PRs in 5 months, about 10 times traditional development speed. The secret was not a stronger model; it was getting the Harness right.

### Core Principles of the Five Harness Functions

The earlier table listed the Harness's five functions. The table below adds each function's core design principle and where this book treats it, mapping concept to practice:

| Function | Core Principle | Practical Example | See Chapter |
|----------|------------------------------------------|----------------------------------|---------|
| **Context** | Information Sufficiency: Ensure the Agent makes decisions based on sufficient information at every decision point | System prompts, knowledge bases, Agent status bars, Sidecar bypass queries | Chapters 2 & 3 |
| **Tools** | Clear Interface: Tool names are intuitive, parameters have examples, boundaries are explained | MCP tools, code interpreter, search tools | Chapter 4 |
| **Constrain** | Fail-Safe Defaults: All capabilities are off by default and must be explicitly enabled (similar to mobile app permission management) | In Claude Code, every tool requires user authorization by default before execution | Chapter 4 |
| **Verify** | Input Isolation: Security checks only look at structured data (e.g., JSON fields returned by tools), not free-form text generated by the model (because attackers might manipulate model output through prompt injection) | Linter checks, type systems, tool call result validation | Chapters 5 & 6 |
| **Correct** | Don't expose intermediate states until a failure is confirmed unrecoverable (e.g., silently retry a failed tool call instead of showing the user a half-finished result) | Silent retries, continuation generation, fallback to human judgment upon consecutive failures (circuit breaker mechanism) | Chapters 2 & 5 |

The five functions form a closed loop: Context and Tools support decision-making, Constrain prevents errors, Verify detects deviations, and Correct closes the cycle. Drop any link and the system develops a reliability gap. Before getting into specific orchestration patterns and guardrail designs, we first lay out the core principles for building effective Agents and for choosing a model—the foundation for every design decision that follows.

### Core Principles for Building Effective Agents

Based on Anthropic's experience, successful Agent systems follow three core principles.

**Keep it simple.** Start with the simplest solution and add complexity only when truly necessary. Direct API calls beat complex frameworks; clear code beats clever abstraction—every extra layer of abstraction is a new blind spot when you debug.

**Keep it transparent.** Show the Agent's planning steps, execution logs, and decision trajectory plainly. This is not just a debugging convenience; it is a precondition for user trust—an error inside a black box can be neither located nor corrected from outside.

**Design a good tool interface (ACI, Agent-Computer Interface).** ACI means designing the interface from the Agent's perspective—easy for the Agent to understand and use—rather than from the programmer's, as traditional APIs are. Tool names and parameters should be intuitive, and likely misuses should be designed out so the error cannot happen at all—the way a USB connector inserts in only one orientation, so it can't be plugged in backwards. Manufacturing has a name for this "eliminate errors through design" philosophy: **Poka-yoke**, from the Toyota Production System. A badly designed tool makes even the strongest model err constantly—the interface is the only channel between model and tool, and a vague interface gets amplified by the model into systemic error.

The next three sections take up three freestanding but important topics in Harness engineering: model selection, orchestration patterns, and guardrails and safety. None belongs to the five Harness elements proper, but none can be avoided in engineering practice.

### How to Choose a Model

Before we get to orchestration patterns, a practical question: what kind of model should drive your Agent?

The model is the Agent's intelligence substrate, and choosing the right one often beats any amount of prompt tuning. Models iterate too quickly for specific version recommendations to stay useful, so this section offers directions instead.

**Know the "Big Three."** The three most commonly used closed-source model providers in current Agent development are OpenAI (GPT/o series), Anthropic (Claude series), and Google (Gemini series). Each has its strengths: Claude excels in complex reasoning, coding, and tool calling, making it a popular choice for Agent development; Gemini boasts an ultra-long context window and powerful multimodal capabilities, suitable for long texts and multimedia scenarios like images and videos; the GPT/o series offers balanced capabilities across the board and has the largest user base. When selecting a model, don't just look at leaderboards; **evaluate it on your own tasks** (see Chapter 6).

**Chinese Models.** If your application is deployed in China or you are on a tight budget, models from Chinese vendors are a pragmatic choice. ByteDance's Doubao series offers extremely low latency within China, suitable for real-time interaction; Moonshot AI's Kimi is among the stronger Chinese models for Agent capabilities; open-source models like Qwen and DeepSeek have advantages in cost and customizability. Note that models differ widely in tool-calling ability, so be sure to test in your specific scenario before committing. Chinese models are typically accessed via APIs from platforms like Volcano Engine (Doubao) and SiliconFlow (open-source models), while overseas models can be accessed uniformly through OpenRouter.

**Open Source vs. Closed Source.** Closed-source models generally lead in capability but are more expensive and constrained by the vendor's API policies. Open-source models are low-cost, support private deployment, and allow fine-tuning customization, making them suitable for cost-sensitive scenarios or those with data compliance requirements.

**The Vast Majority of Agents Need a Model that Supports Reasoning.** Agents make complex decisions—multi-step reasoning, tool selection—and models without reasoning tend to do them badly. The exceptions are few: a single simple step, or Computer Use GUI operations that amount to clicking a fixed position, where a non-reasoning model can cope. The moment multi-step reasoning or dynamic decision-making enters, a reasoning model is essential.

**Pay Attention to Output Speed and Multimodal Capabilities.** Beyond cost, two dimensions are easy to overlook. One is **output token speed**: Agents typically run many rounds of inference, and each round must finish before the next can start, so output speed directly sets end-to-end latency—a 20-round Agent task that runs 2 seconds slower per round means an extra 40 seconds of waiting. The other is **multimodal support**: if your Agent needs to understand images, audio, or video, multimodal capability is a hard requirement, and models differ widely here.

### Orchestration Patterns: Workflow vs. Autonomous

Orchestration patterns are how the Harness organizes its "context and tools" layer—they determine how context flows between LLM calls, how tools are scheduled, and whether the Agent's execution path is fixed in advance or generated on the fly. Agent orchestration has evolved from simple to complex, and each pattern has its scenarios and its trade-offs. In Anthropic's experience working with dozens of teams building LLM Agents, the most successful implementations rarely use complex frameworks; they use simple, composable patterns.

When building an LLM application, go from simple to complex. Start with a single LLM call—if better prompts and in-context examples solve the problem, don't build an Agent system. When multiple steps are needed and the task decomposes cleanly into fixed sub-tasks, use a workflow. Reach for an autonomous Agent only when you need dynamic decisions and a flexible execution path. And remember: Agent systems typically trade latency and cost for better task performance—weigh carefully whether that trade is worth it.

#### Workflow Pattern: Deterministic Orchestration

A **workflow** is a system that orchestrates LLMs and tools through predefined code paths. Its execution path is deterministic, designed in advance by the developer—what each step does and where it goes next is hardcoded; the LLM handles only the understanding and generation inside each node.

Taking a flight booking Agent as an example, a workflow can be designed with four fixed nodes:

1.  **Verify User Identity**—Call the identity verification API to confirm who the user is.
2.  **Search for Available Flights**—Query the flight database based on user requirements.
3.  **Complete Payment**—Call the payment interface to deduct the amount.
4.  **Confirm Booking**—Call the booking API to lock the seat and send a confirmation to the user.

An LLM can be used within each node (e.g., using natural language to understand the user's travel needs), but the flow sequence between nodes is fixed by code—the system won't book a seat before payment is completed, nor will it start searching for flights before identity verification.

The workflow pattern has two core advantages. First, **strict process control**: the developer can guarantee that critical steps are never skipped or run out of order—business rules like "no booking before payment" are enforced by code, not left to the LLM's judgment. Second, **security**: because the execution path is deterministic, prompt injection or a model error can at most corrupt the processing inside the current node; it cannot make the Agent jump to a branch it shouldn't reach. The attack surface is confined to a single node.

The main limitation of a workflow is its **lack of flexibility**. When something the flow never anticipated happens—the user decides mid-payment to change the booking, or a flight is suddenly canceled and an alternative must be recommended—the fixed path cannot adapt; all it can do is follow a preset exception branch or hand control back to a human.

#### Autonomous Agent: Dynamic Autonomous Decision-Making

When the fixed path of a workflow is insufficient, we need an **autonomous Agent**. The core difference between an autonomous Agent and a workflow is that the execution path is not pre-defined but is determined in real-time by the Agent based on **environmental feedback**.

The flight example again: an autonomous Agent needs no four predefined nodes. The user says, "Book me a flight to Shanghai next Wednesday," and the Agent works it out as it goes—it searches for flights, discovers it needs to log in, verifies identity first, returns to the search, notices the cheapest flight has a layover, asks the user whether that's acceptable; the user says no layovers, so it adjusts the search criteria...

An autonomous Agent therefore has to plan for itself—choose its own execution steps—and to recognize failure and change strategy rather than simply halting on error. But autonomy is not unbounded: explicit **stopping conditions** must be designed in (task complete, maximum iterations reached, unrecoverable error hit), or the Agent slips easily into infinite loops or over-execution.

From an implementation perspective, an autonomous Agent is essentially an LLM using tools in a loop, continuously obtaining environmental feedback to advance the task—this is the ReAct loop introduced earlier. Common exit conditions include: calling a final output tool, the model returning a response without any tool calls, or encountering an error or reaching the maximum number of rounds.

![Figure 1-5: Execution loop of an autonomous Agent](images/fig1-5.svg)

Autonomous Agents are particularly suitable for open-ended problems—those where it's difficult or impossible to predict the number of steps required. Typical application scenarios include: Coding Agents solving SWE-bench (Software Engineering Benchmark, a benchmark for evaluating an Agent's ability to automatically fix real GitHub issues) tasks, "Computer Use" Agents operating computer interfaces like a human, and research tasks requiring iterative search and analysis.

Autonomy also costs more and lets errors compound. Deploying an autonomous Agent therefore demands thorough testing in a sandbox, appropriate guardrails and monitoring, and human-in-the-loop checkpoints at critical decision points.

#### Choosing and Mixing the Two Patterns

In practice, workflows and autonomous Agents are not an either/or—many systems mix the two: critical processes with strict compliance requirements run as workflows for reliability, while the parts that need flexible decisions switch to autonomous mode. n8n, for example, is a mature open-source workflow automation framework in which developers build Agents by dragging functional components around a visual canvas—and workflow nodes and autonomous Agent nodes can live in the same system.

![Figure 1-6: n8n workflow editor interface](images/n8n-workflow.png)

#### Brief Comparison of Mainstream Agent Frameworks

The following table summarizes the current mainstream Agent frameworks/platforms to help readers quickly identify the right one for their scenario:

| Framework/Platform | Core Positioning | Orchestration Pattern | Development Approach | Applicable Scenarios |
|-------------------|--------------------|----------------|----------------|-------------------------|
| **OpenAI Agents SDK** | Lightweight Agent development library | Autonomous (tool loop) | Code-first | Rapid prototyping, single-agent applications |
| **Claude Agent SDK** | Production-grade Agent development framework | Autonomous (tool loop + sub-agents) | Code-first | Complex autonomous tasks, Coding Agent |
| **LangChain / LangGraph** | General-purpose LLM application framework | Workflow + Autonomous | Code-first | Complex chain-of-thought, multi-step workflows |
| **n8n** | Visual workflow automation | Workflow + Autonomous | Low-code (visual drag-and-drop) | Business automation, non-technical teams |
| **Dify** | LLM application development platform | Workflow + Conversational | Low-code (visual + API) | Enterprise-grade RAG, knowledge base applications |
| **CrewAI** | Role-based multi-agent orchestration | Multi-Agent collaboration | Code-first | Team-based task decomposition and execution |
| **OpenClaw** | Open-source all-in-one personal Agent | Autonomous + Event-driven | Configuration + Code (self-hosted) | Personal assistant, Deep Research, Computer Use, multi-platform message integration |

As the "Model as Agent" trend deepens, a framework's core value no longer lies in "orchestrating LLM calls"—models increasingly decide for themselves. What has grown more important is the Harness engineering around the model: context management, the tool ecosystem, security constraints, error recovery. When choosing a framework, the question is not how sophisticated the framework is, but whether it lets you focus on business logic through the thinnest possible layer of abstraction.

Orchestration patterns solve the organization of context and tools within the Harness—how LLM calls, tools, and data flows connect. But getting things done is not enough; they must also be done correctly and safely. So we turn to the chief way the constrain, verify, and correct mechanisms land in practice: guardrails.

### Guardrails and Safety

This section gives a high-level overview of guardrails to establish the big picture. Implementation details and practice follow in Chapter 2 (prompt injection protection), Chapter 4 (tool permission control), and Chapter 5 (code execution security); first-time readers needn't chase every detail.

Guardrails are how the "constrain, verify, and correct" layer of the Harness is chiefly implemented—a layered defense that keeps Agent behavior safe and controllable. Well-designed **guardrails** help manage data privacy risks (say, preventing system prompt leakage) and reputational risks (say, keeping model behavior consistent with the brand). Start with guardrails for the risks you have already identified, then add new ones as new vulnerabilities surface.

Think of guardrails as defense in depth. No single guardrail is likely to protect enough on its own, but several specialized ones combined make a far more resilient Agent system.

#### Types of Guardrails

By where they sit, guardrails fall into three types: input-side, execution-side, and output-side.

**Input-side** guardrails intercept requests before they reach the Agent, typically through four mechanisms. **Relevance classifiers** flag off-topic queries—a coding assistant asked "How tall is the Empire State Building?". **Safety classifiers** detect jailbreaks (inducing the model to bypass its safety restrictions) and prompt injections (embedding malicious instructions in input). The key difference: in a jailbreak, the user themselves tries to get past the model's restrictions; in prompt injection, an attacker manipulates model behavior indirectly through external data (web content, documents). **Content moderation** flags harmful or inappropriate input, such as violent or discriminatory content. **Rule-based protections** apply deterministic measures—blacklists, input length limits, regular-expression filters—against known threats like SQL injection.

**Execution-side** guardrails validate tool calls. The core is **tool risk rating**: based on whether an operation is reversible, its permission level, and financial impact, each tool is assigned a risk level (low/medium/high). High-risk operations require additional review or human confirmation.

**Output-side** guardrails check the response before it is returned to the user. **PII filters** review the output for personally identifiable information (e.g., ID numbers, phone numbers) to prevent unnecessary exposure; **output validation** ensures the reply aligns with brand values through content checks.

Note that some mechanisms (e.g., rule-based regex filtering) can be used on both the input and output sides; the above categorization follows the most common deployment locations.

#### Human Intervention

**Human in the loop** is a key protective measure: it lets an Agent improve real-world performance without degrading the user experience. It matters most in early deployment, when it helps identify failure modes, surface edge cases, and establish a robust evaluation cycle.

With a human-in-the-loop mechanism, an Agent that cannot complete a task can hand over control gracefully. In customer service, that means escalating to a human representative; for a Coding Agent, handing control back to the developer.

There are typically two main situations that trigger human intervention:

**Exceeding Failure Thresholds**
Cap the Agent's retries and operations. If the Agent blows past those caps (say, it still can't grasp the customer's intent after several attempts), escalate to a human.

**High-Risk Operations**
Sensitive, irreversible, or high-risk operations should trigger human oversight—at least until the team has built enough confidence in the Agent's reliability. Typical examples: canceling a user's order, authorizing a large refund, processing a payment.

Back now to the main thread of the five Harness elements—here is how the chapters of this book unfold within that framework.

### This Book as a Practical Guide to Harness Engineering

Seen through the lens of Harness engineering, each chapter of this book systematically builds out one component of the Harness. Security, meanwhile, belongs to no single chapter; it is a cross-cutting concern of the whole book (a cross-cutting concern touches many parts of a system at once—the way logging, in software engineering, has to thread through every module). The table below presents the Harness functions, security aspects, and corresponding chapters in one view:

| Harness Focus | Corresponding Chapter | Core Content | Security Concerns |
|--------------------|--------------------|-------------------------------|------------------------|
| Context Design | Chapter 2 (Context Engineering) | Prompt engineering, Agent status bar, context compression, Agent Skills | Prompt injection and information leakage |
| Context Expansion (Knowledge Persistence) | Chapter 3 (Knowledge Base) | User memory, RAG, structured indexing, agentic RAG | Sensitive information exposure, privacy protection |
| Tool Design and Security Constraints | Chapter 4 (Tool Design) | Tool classification, permission control, MCP standard, asynchronous architecture | Misoperation, unauthorized access, irreversible operations |
| Tool Verification and Correction | Chapter 5 (Code Generation) | Coding Agent's Harness, test-driven development, codified rules | Identity impersonation, responsibility attribution |
| System-Level Verification | Chapter 6 (Evaluation) | Evaluation environment, datasets, automated evaluation, observability | — |
| Model-Level Correction | Chapter 7 (Post-Training) | SFT (Supervised Fine-Tuning), Reinforcement Learning—writing feedback signals accumulated in the Harness into model parameters, seen as an extension of Harness engineering | Goal misalignment, alignment and robustness |
| System-Level Correction | Chapter 8 (Self-Evolution) | Externalized learning, tool creation, experience accumulation | — |
| Multimodal Context and Tools | Chapter 9 (Multimodal and Real-Time Interaction) | Voice Agent, Computer Use, robotic operation | Security filtering of multimodal input, permission control in real-time interaction |
| Constraints and Corrections Among Multiple Agents | Chapter 10 (Multi-Agent Collaboration) | Collaboration architecture, failure modes, Agent society | Trust boundary violations between Agents, shared resource conflicts |

Anthropic's practice in building long-running Agents shows how Harness design can solve problems the model itself cannot. They split complex tasks between an "Initialization Agent" (setting up the environment, decomposing the task list) and an "Execution Agent" (making incremental progress each session and leaving clear handover artifacts), using a structured Harness to tackle the two failure modes of long tasks: running out of context and declaring the task done prematurely. The chapters ahead work through the Harness component by component—Chapter 2 begins with the most central one, context engineering, and Chapter 5 lays out the complete practice of Harness engineering in Coding Agents.

## Chapter Summary

This chapter has built, starting from practice, the basic framework for understanding and constructing AI Agents.

**Agent = Brain + Eyes + Hands and Feet**: The LLM is the brain (the decision-making core), context is the eyes (determining what it can see), and tools are the hands and feet (determining what it can do). None of the three is dispensable.

**Eyes (Context) Are the Decisive Factor**: Context consists of a static prefix (system prompt + tool definitions) and a dynamic trajectory (message history). Ablation shows that removing any component degrades the system markedly. The essence of the ReAct loop is appending to the trajectory, over and over, so the model keeps advancing the task.

**Harness Is the Competitive Advantage**: Model capability is commoditizing; the real differentiator is the Harness—the constrain, verify, and correct mechanisms built around context and tools that make an Agent "reliably get things done." In production-grade Agent systems, the vast majority of Harness code goes into these safeguards, not the context and tools alone.

**From Workflow to Autonomous Agent**: Prompts first, then workflows, autonomous Agents last—that ordering is the most practical way to keep the risk of surprises down. Every orchestration pattern has its home ground; no single one is best everywhere.

**Security Is an Architectural Issue**: Guardrails, human-in-the-loop intervention, alignment (keeping the model's behavior consistent with human intent)—security has to be designed in from the first line of code, not patched on before launch. It spans five levels: model, context, tools, collaboration, and society.

The next chapter goes deep into the Harness's most central component—context engineering. As for the Agent concept's academic roots in reinforcement learning, and a fuller comparison of traditional RL with modern LLM Agents, Chapter 7 covers both systematically.

The thought questions below are designed to take the chapter's core concepts a level deeper.

## Thought Questions

1. ★★ If you could only add one capability to an Agent system—a stronger model, richer context, or more tools—which would you choose? Under what conditions would your choice change?
2. ★★★ In the ReAct loop, each of the Agent's LLM calls sees the full history trajectory, so as the trajectory grows, the cost of this design grows quadratically. Can that quadratic growth be broken without losing critical information?
3. ★★ The "Model as Agent" paradigm means models are becoming more autonomous in tool-calling decisions. However, this chapter argues that the importance of Harness engineering is actually increasing. How can these two trends coexist? Where does the future core value of Agent frameworks lie?
4. ★★ In the ablation experiment, the absence of "tool result feedback" caused the Agent to fall into an infinite loop. In a production environment, besides missing tool results, what other situations could cause an Agent to loop? What detection and termination mechanisms would you design?
5. ★ This chapter analyzed five Agent products along three dimensions: perception, action, and strategy. Pick an AI product you use daily, analyze it along the same three dimensions, and judge whether its architecture makes sense. If you were designing it, what would you improve?
6. ★★ If you were to design a customer service system specifically for booking flights, would you choose a workflow pattern or an autonomous Agent pattern? Is it possible to mix both patterns in the same system?
7. ★★★ The guardrails section mentioned tool risk ratings. If a tool is generally low-risk but becomes high-risk with specific parameter combinations (e.g., `delete_file` deleting a normal file vs. deleting a system file), how would you design dynamic risk assessment?
8. ★★ In the Agent product table in this chapter, all Agents have an "open-ended" action space. In what scenarios would a constrained action space (e.g., only being able to choose from predefined options) be superior to an open-ended one?
9. ★★ The human-in-the-loop intervention mechanism requires the Agent to "gracefully hand over control." However, in practice, the user might be offline, respond slowly, or give vague instructions. What should the Agent do in such cases?
10. ★★★ The introduction states that "good design principles should transcend model iteration cycles." Try to give an example of a current Agent design principle that you believe might become obsolete as models improve, and explain your reasoning.


**References**

<a id="ref-^ch1-1"></a>[1] Sutton, Rich. “The Bitter Lesson”, 2019. http://www.incompletenessideas.net/IncIdeas/BitterLesson.html

