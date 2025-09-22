# Conversational Legal Advisor Agent for Case Analysis

## 1. Problem Statement

The legal system is complex and opaque to most non-professionals. When individuals face legal issues, they often struggle to understand their situation, identify relevant facts, or anticipate potential outcomes. They lack the specialized knowledge to articulate their circumstances in a way that is meaningful for legal analysis. This project aims to develop a conversational AI agent that acts as a preliminary legal advisor. The agent will guide users through a structured conversation to gather the critical details of their situation, and then leverage a large database of past legal cases to provide insights, identify similar precedents, and explain the factors that may influence legal outcomes, such as the term of imprisonment.

## 2. Core Challenges

The primary challenge is transforming a massive, unstructured dataset of legal case descriptions into a structured, queryable knowledge base and using it to power an intelligent conversational agent. This breaks down into several key difficulties:

*   **Knowledge Structuring:** The "fact" descriptions in the CAIL dataset are narrative and unstructured. The core task is to extract the legally salient information and represent it in a consistent, structured format (i.e., defining and extracting "tags"). This requires identifying what elements of a case (e.g., severity of injury, presence of a weapon, mitigating circumstances) are determinative for the final judgment.

*   **Identifying Sentencing Factors:** It is not immediately obvious which factors from the case description have the most significant impact on the final sentence. A systematic approach is needed to analyze the structured data and quantify the relationships between case attributes and the length of imprisonment, to answer the question: "What really matters in my case?".

*   **Guided Information Elicitation:** The agent must be more than a simple Q&A bot. It needs to "know what it doesn't know." Given a user's initial, often vague, description, the agent must intelligently ask targeted follow-up questions to elicit the specific details required for a meaningful case comparison and analysis. This requires an internal model of what information is necessary for different types of legal situations.

*   **Case Retrieval and Relevance:** Once sufficient information is gathered, the system must efficiently search through thousands of cases to find the ones that are most analogous to the user's situation. Simple keyword search is insufficient; the matching must be based on the structured, legally relevant factors.

## 3. Proposed Solution

We propose a three-stage solution that encompasses knowledge base construction, analytical modeling, and the development of a conversational agent.

### 3.1 System Architecture Overview

The system will be composed of two main parts: an offline processing pipeline and an online conversational agent.

*   **Offline Pipeline:** This pipeline will process the entire CAIL dataset. It will extract structured information from each case's "fact" description and build a hybrid knowledge base. It will also train a predictive model to analyze sentencing factors.
*   **Online Agent:** This is the user-facing conversational interface. It will manage the dialogue, query the knowledge base, and use the predictive model to provide insights to the user.

### 3.2 Stage 1: Knowledge Extraction and Structuring

This stage focuses on converting raw case text into a structured knowledge base. The central challenge is creating a schema that is comprehensive enough to capture the nuances of many different crime types while remaining consistent and manageable. We will employ a hybrid, data-driven strategy to achieve this.

1.  **Schema Strategy: A Hybrid, Data-Driven Approach**

    We will create a modular, component-based schema rather than a single monolithic one. This involves a multi-step process:

    *   **a. Top-Down Thematic Grouping:** We will first programmatically analyze the entire dataset to identify all unique `accusation` values. These will be grouped into broader legal categories (e.g., "Crimes Against Persons," "Crimes Against Property," "White-Collar Crimes," "Public Order Offenses"). This provides a structured framework for our schema.

    *   **b. Core Schema + Extension Schemas:** We will define a two-level schema:
        *   **`core_schema`**: Contains factors common across most criminal cases. This includes fields for `mitigating_factors` (like confession, compensation, surrender) and `aggravating_factors` (like recidivism, use of a weapon, leading role in a group crime).
        *   **`extension_schemas`**: For each thematic group, we will define a specific extension. For instance, the "Crimes Against Persons" extension will include `victim_injury_level` and `number_of_victims`. The schema for "Financial Crimes" like "Bribery" (受贿) would include `amount_of_bribe` and `details_of_power_abuse`.

2.  **Two-Pass LLM-Powered Extraction and Discovery**

    We will use a two-pass process to leverage the LLM for both factor discovery and structured data extraction.

    *   **a. Pass 1: Automated Factor Discovery (Bottom-Up):** To ensure our schema is based on evidence from the data, we will first sample a few hundred cases from each thematic group. We will prompt an LLM with a broad instruction: "Analyze this legal case and list all key factors and circumstances that likely influenced the final judgment." The output from this discovery pass will be used to refine and validate the fields in our `core_schema` and `extension_schemas`, ensuring we capture the most salient information.

    *   **b. Pass 2: Full Structured Extraction (Top-Down):** With the refined, modular schema in place, we will process the entire dataset. For each case, the LLM will be given a targeted prompt instructing it to populate the fields of both the `core_schema` and the specific `extension_schema` that corresponds to the case's crime type.

3.  **Knowledge Base Creation:** The extracted JSON objects, now consistently structured according to crime type, will be stored in a hybrid database. We recommend using a system like Elasticsearch or a PostgreSQL database with JSONB support. This allows for both:
    *   **Structured Filtering:** Exact queries on specific fields (e.g., `victim_injury_level: "重伤二级"` AND `use_of_weapon: true`).
    *   **Full-Text Search:** Searching the original `fact` text.
    Additionally, we can generate vector embeddings of the `fact` text to enable semantic similarity searches.

### 3.3 Stage 2: Case Grouping and Factor Analysis

Instead of training a traditional regression model to predict sentences, we will use an analytical, unsupervised approach to discover the natural structure within the case data. The goal is to group similar cases into "archetypes" and identify the factors that define these groups. This method is more robust and provides deeper insights than a simple predictive model.

1.  **Case Vectorization:** For each crime category, the extracted structured data will be converted into a composite numerical vector. This is not a text embedding, but a structured representation built by processing each factor type appropriately and concatenating the results:
    *   **Categorical Features** (e.g., `victim_injury_level`, `weapon_type`): These will be converted using **One-Hot Encoding**, creating a binary column for each possible category.
    *   **Boolean and Tag-List Features** (e.g., `use_of_weapon`, `mitigating_factors`): These will be represented using **Multi-Hot Encoding**, creating a binary vector where each position corresponds to a specific factor and is marked '1' if present.
    *   **Numerical Features** (e.g., `punish_of_money`): To handle skewed distributions, these will first undergo a **log transformation** and then be normalized using **Standard Scaling**.
    This composite vector provides a comprehensive numerical fingerprint of each case for the clustering algorithm.

2.  **Clustering for Archetype Discovery:** We will use a density-based clustering algorithm like HDBSCAN on these vectors. This will group the cases into distinct clusters, where each cluster represents a common archetype of that crime (e.g., for assault, one cluster might be "minor disputes with no weapons," while another is "group assaults with serious injuries"). This approach has the advantage of not requiring us to pre-specify the number of archetypes.
3.  **Defining Cluster Characteristics:** Once the clusters are identified, we will analyze the feature distribution within each cluster and compare it to the overall dataset. The factors that are most over-represented or under-represented in a cluster are the ones that define it. For instance, if 90% of cases in a cluster involve `compensation_paid`, that becomes a key characteristic of that archetype.
4.  **Deriving the Factor Importance Hierarchy:** The "Factor Importance Hierarchy" will be derived directly from this clustering analysis. The factors that are most effective at separating cases into distinct, meaningful clusters (especially those with different sentencing outcomes) are deemed the most important. This can be quantified using statistical measures like mutual information or feature variance between clusters. This data-driven hierarchy of factors is the primary output of this stage and will be the core of the agent's intelligence.

### 3.4 Stage 3: Conversational Agent and Case Retrieval

This stage defines the user interaction logic, which is explicitly driven by the Factor Importance Hierarchy derived from the case grouping analysis in Stage 2.

### 3.5 Agent Implementation and Logic

To implement the agent's conversational and reasoning capabilities, we will adopt the **ReAct (Reasoning and Acting)** framework, similar to the architecture used in the `agentic-rag` project. This paradigm allows the agent to intelligently cycle through thoughts, actions, and observations to achieve its goals in a flexible and dynamic way.

**1. ReAct Agent Architecture**

Instead of a rigid pipeline, the agent will be a single, powerful LLM prompted to operate in a ReAct loop. It will have access to a specific set of tools to interact with its environment.

*   **The ReAct Prompt:** The agent's core logic will be guided by a master prompt that instructs it to reason about its current state and choose the next best action. The loop is as follows:
    1.  **Thought:** The agent analyzes the user's query and its internal state (what it knows). It decides what information is missing and what its goal is for the current turn.
    2.  **Action:** Based on its thought, the agent chooses a tool to execute and specifies the parameters for it.
    3.  **Observation:** The agent receives the output from the tool, which becomes the input for the next thought cycle.

*   **Core Components:**
    *   **LLM:** A powerful large language model serves as the central reasoning engine for the agent.
    *   **State Tracker:** A simple dictionary that stores the conversation history and all extracted factors (`slots`) gathered so far. This is the agent's memory.
    *   **Tool Library:** A set of functions the agent can call to perform actions.

**2. Specialized Tools for the Legal Agent**

The agent's capabilities will be defined by its specialized tools:

*   **`GenerateGuidedQuestionnaire(crime_type: str, known_factors: dict)`:**
    *   **Purpose:** This is the primary tool for gathering information from the user.
    *   **Logic:** It takes the classified crime type and the currently known factors. It looks up the pre-computed **Factor Importance Hierarchy** for that crime. It then identifies the most important factors that are still unknown and constructs the full questionnaire, complete with explanations for each question.
    *   **Output:** Returns a single, formatted string to be presented to the user.

*   **`QueryKnowledgeBase(crime_type: str, known_factors: dict)`:**
    *   **Purpose:** To find analogous cases in the structured database.
    *   **Logic:** It takes the collected factors and constructs the weighted query for the knowledge base (e.g., Elasticsearch), using hard filters and boosted scoring as previously described.
    *   **Output:** Returns a structured list of the top N matching cases.

*   **`SynthesizeCaseAnalysis(retrieved_cases: list, user_factors: dict)`:**
    *   **Purpose:** To generate the final, human-readable summary.
    *   **Logic:** It takes the retrieved cases and the user's situation. It identifies the case archetype, calculates the typical sentencing range for those cases, and formulates a nuanced, easy-to-understand explanation for the user, including the all-important disclaimers.
    *   **Output:** Returns the final analysis text for the user.

**3. Example ReAct Conversational Flow**

1.  **User Input:** "I got into a fight and the other person was hurt."
2.  **Cycle 1:**
    *   **Thought:** The user has described a situation that sounds like "Intentional Injury." I have very little information. I need to gather the key facts. My next action should be to generate the standard questionnaire for this type of crime.
    *   **Action:** `GenerateGuidedQuestionnaire(crime_type="Intentional Injury", known_factors={})`
    *   **Observation:** (The agent receives the formatted questionnaire string from the tool.)
    *(The agent presents this questionnaire to the user.)*
3.  **User Response:** (The user answers the questions about injury severity, weapons, compensation, etc.)
4.  **Cycle 2:**
    *   **Thought:** The user has answered the questionnaire. I have now extracted the key factors: `injury_level="serious"`, `weapon_used=false`, `compensation_paid=true`. I have enough information to find similar cases. My next action is to query the knowledge base.
    *   **Action:** `QueryKnowledgeBase(crime_type="Intentional Injury", known_factors={"injury_level": "serious", ...})`
    *   **Observation:** (The agent receives a list of the top 5 most similar cases from the KB.)
5.  **Cycle 3:**
    *   **Thought:** I have the most relevant cases. Now I need to analyze them and present a clear summary to the user. My final action is to synthesize these findings.
    *   **Action:** `SynthesizeCaseAnalysis(retrieved_cases=[...], user_factors={"injury_level": "serious", ...})`
    *   **Observation:** (The agent receives the final summary text.)
    *(The agent presents the final analysis to the user.)*

This ReAct-based approach provides a clear, powerful, and auditable framework for building our intelligent legal advisor.

### 3.6 Result Presentation and Synthesis

Once the most relevant cases are retrieved, the agent moves to the final stage of synthesizing and presenting the information. Leveraging the cluster analysis, the agent can provide more nuanced insights:

*   It can identify the case archetype the user's situation belongs to: "Your situation appears similar to a common group of cases characterized by [Key Factor 1] and [Key Factor 2]."
*   It will present the typical sentencing range for that specific group: "In this group of cases, sentences typically range from X to Y months."
*   It will highlight the key differentiators learned from the analysis: "A critical factor we've seen in these cases is [Important Factor C]. How does that apply to your situation?"
*   This approach, grounded in data-driven archetypes, allows the agent to provide explanations that are more concrete and understandable than a simple statistical prediction.

## 5. Data

The project will use the **CAIL2018 dataset**, specifically the large-scale collection of criminal legal documents. The dataset's JSON structure, with a clear `fact` and `meta` (outcome) separation, is ideal for this supervised learning and extraction task.

## 6. Evaluation

The system's performance will be evaluated across its different components:
*   **Knowledge Extraction:** The accuracy of the LLM-based extraction can be measured by creating a small, manually-annotated "gold standard" set of structured cases and calculating precision, recall, and F1-score against it.
*   **Case Grouping Quality:** The quality of the discovered case archetypes can be evaluated using clustering metrics like the Silhouette Score. We can also perform qualitative analysis to ensure the clusters are legally coherent and meaningful.
*   **Conversational Agent:** Agent quality can be assessed through user studies, measuring task success rate (was the user able to get relevant case information?), conversation length, and user satisfaction scores.

## 7. Ethical Considerations & Disclaimers

This is of paramount importance. The agent must repeatedly and clearly state that it is **not a lawyer** and that its output **does not constitute legal advice**. All information should be presented as being for educational and informational purposes only. The system should strongly encourage users to consult with a qualified legal professional for advice on their specific situation. The potential for misuse or over-reliance on the agent's suggestions must be mitigated through careful design of its conversational script and user interface.
