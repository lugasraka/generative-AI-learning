# Part 4: Types of Agentic RAG

Agentic RAG systems can be classified based on how agents operate and the complexity of their interactions with the retrieval and generation components. There are several types, each suited for different tasks and levels of complexity:

## 1. Single-Agent RAG

In this setup, a single intelligent agent is responsible for managing the entire retrieval and generation process. The agent decides which sources to query, what data to retrieve, and how the data should be used in generating the final response.

This type is ideal for simpler tasks or systems where decision-making doesn't require much complexity. Single-agent RAG is efficient when managing routine queries with straightforward information retrieval needs.

## 2. Multi-Agent RAG

Multi-agent RAG involves multiple agents working together, each handling different aspects of the retrieval and generation process. One agent might handle retrieval from a specific source, while another might focus on optimizing the integration of data into the LLM's response.

Multi-agent systems are well-suited for more complex scenarios, where different types of data need to be fetched from various sources or when tasks need to be broken down into smaller, specialized parts.

## 3. Hierarchical Agentic RAG

In this setup, agents are organized in a hierarchy, where higher-level agents supervise and guide lower-level agents. Higher-level agents may decide which data sources are worth querying, while lower-level agents focus on executing those queries and returning the results.

This type is beneficial for highly complex tasks, where strategic decision-making is required at multiple levels. For example, hierarchical Agentic RAG is useful in systems that need to prioritize certain data sources or balance competing priorities.

---

**Previous:** [Part 3: Agentic RAG Capabilities](part3_agentic_rag_capabilities.md)
**Next:** [Part 5: Implementing Agentic RAG](part5_implementing_agentic_rag.md)
