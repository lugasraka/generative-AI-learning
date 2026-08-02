# Part 2: What is Agentic RAG?

When **RAG and agents** are combined, the agents take charge of the entire process, deciding how and when to retrieve the data and how to use it to generate the best possible response. Instead of simply retrieving information, the agents make smart choices about where to get the data, what is most important, and how to integrate it into the LLM's answer. This results in a system that can handle more complex queries and deliver responses that are both accurate and tailored to the specific situation.

![differences.png](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/resources/img/differences.png)

## How Agentic RAG Works — Step-by-Step Example

Let's walk through an example to understand how Agentic RAG operates in real-time. Suppose you're using a customer support chatbot powered by Agentic RAG to resolve an issue with your internet service. The query you input is:

**"Why is my internet slow in the evenings?"**

### Step-by-Step Breakdown:

1. **User Query**
    - You type your query into the chatbot: "Why is my internet slow in the evenings?"
    - The query is received by the system, which activates the intelligent agent to determine the next steps.
2. **Agent Analyzes the Query**
    - The agent analyzes your question, recognizing that it's a service-related query that might need data on your internet usage patterns, network traffic, and potential service disruptions.
    - Based on this, the agent identifies relevant data sources, such as your service history, network reports, and real-time traffic data.
3. **Agent Decides on Retrieval Strategy**
    - The agent determines which external data sources to query. In this case, it may decide to:
        - Fetch data from your account history to check if there are any noted service issues.
        - Retrieve network traffic reports from the internet service provider (ISP) to analyze peak usage times in your area.
        - Query a public knowledge base to gather information on common causes of evening slowdowns.
4. **Data Retrieval**
    - The retrieval system, directed by the agent, pulls information from multiple sources. It fetches:
        - Your service history, showing an uptick in complaints during the evening.
        - Network traffic reports indicating high congestion in your neighborhood between 6 PM and 10 PM.
        - Articles from the knowledge base explaining how peak-time usage and congestion can cause slower speeds.
5. **LLM Generates Response**
    - Once the relevant data is retrieved, the large language model (LLM) processes it. The model takes into account both its pre-trained knowledge and the real-time data fetched by the agent.
    - The LLM generates a response that integrates these insights: **"It appears that your internet speed slows down in the evenings due to high traffic in your area during peak hours. You might want to consider upgrading your plan or using the internet during off-peak times to avoid congestion."**
6. **Response Delivery**
    - The generated response is delivered to you, providing a clear and accurate explanation of why your internet is slow in the evenings, based on both real-time data and the model's general understanding of network congestion.
7. **Follow-Up Actions**
    - If necessary, the agent could continue assisting by offering additional solutions. For instance, it could recommend a faster internet plan or schedule a technician visit if it detects any ongoing issues with your connection.

## Key Points of Agentic RAG in Action

- The **agent** autonomously decides which sources to query based on your question.
- The **retrieval system** pulls real-time data specific to your query, enhancing the LLM's response.
- The **LLM** generates an answer that is more accurate and context-aware because it integrates both pre-trained knowledge and the fresh data fetched by the agent.

Note that while this is a basic example of how Agentic RAG operates, it can also interact with not just knowledge bases but also other tools and services, similar to the way traditional agents do.

---

**Previous:** [Part 1: Understanding RAG and Agents](part1_understanding_rag_and_agents.md)
**Next:** [Part 3: Agentic RAG Capabilities](part3_agentic_rag_capabilities.md)
