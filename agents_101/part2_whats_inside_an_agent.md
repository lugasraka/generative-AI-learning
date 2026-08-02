# Part 2: What's Inside an Agent: The Harness

A widely used way to break down the harness is into four parts.

![Screenshot 2024-04-07 at 2.53.23 PM.png](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/resources/img/Screenshot_2024-04-07_at_2.53.23_PM.png)

Image Source: [Introduction to LLM Agents, Nvidia](https://developer.nvidia.com/blog/introduction-to-llm-agents/)

## 1. Agent Core (The Brain)

The central decision loop. It holds the agent's goal, decides which tool to use and when, pulls in relevant memory, and often carries a persona or set of operating rules. With reasoning models (the o-series, DeepSeek-R1 and successors), a lot of the planning that used to be hand-built now happens inside the model's own chain of thought.

## 2. Memory

Where the agent keeps state. Short-term memory holds the current task's working context; long-term memory holds facts and history across sessions, usually retrieved by semantic similarity plus signals like recency and importance. Managing what goes into the context window, and what stays out, is a core skill now often called **context engineering**.

## 3. Tools

The actions the agent can take. Tools range from web search and code execution to retrieval (RAG) and any API. The **Model Context Protocol (MCP)** has become the common standard for connecting an agent to tools and data sources, so you wire a capability once and reuse it across agents.

## 4. Planning

How the agent breaks a hard task into steps, critiques its own work, and decides what to do next. Task decomposition and reflection are the staples; reasoning models made this dramatically more capable.

## An Alternative Framework

An earlier survey framed the same idea as brain, perception, and action. It is another useful lens on the same structure.

![Screenshot 2024-04-07 at 2.39.12 PM.png](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/resources/img/Screenshot_2024-04-07_at_2.39.12_PM.png)

Image Source: [The Rise and Potential of Large Language Model Based Agents: A Survey](https://arxiv.org/pdf/2309.07864.pdf)

---

**Previous:** [Part 1: Introduction to LLM Agents](part1_introduction_to_llm_agents.md)
**Next:** [Part 3: Multi-Agent Systems](part3_multi_agent_systems.md)
