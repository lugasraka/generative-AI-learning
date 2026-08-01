# Part 8 — Building LLM Apps (Progressive)

> Source: [week7_build_llm_app.md](../../Applied_LLMs_Mastery_2024/week7_build_llm_app.md)

## Concept in 10 lines

- Building an LLM app is a progression from simple to complex. Start with the minimum, add layers only when needed.
- **Stage 1 — Simple prompt + LLM**: the simplest app. A template, an API call, a response. Good for single-task automation.
- **Stage 2 — Prompt chaining**: break a complex task into sequential steps. Each step's output feeds the next. Example: extract topic → look up info → generate answer.
- **Stage 3 — RAG**: add external knowledge. Retrieve relevant documents, stuff them into the prompt, generate grounded answers.
- **Stage 4 — Memory**: add conversation history. The model sees previous turns, enabling multi-turn conversations.
- **Stage 5 — Tools**: add external capabilities. The model can call APIs, search databases, do calculations.
- **Stage 6 — Agents**: combine planning, memory, and tools. The model decides what to do at each step autonomously.
- **Stage 7 — Fine-tuning**: customize the model's behavior for your specific use case. The nuclear option — try everything else first.
- Each stage adds complexity and capability. The key is to **measure whether each addition actually helps** before keeping it.

## Vibe-coding challenge

**Build an LLM app progressively through 5 stages.** Create a Python script called `llm_app_builder.py` that:

1. **Stage 1 — Simple prompt**: Implement `stage1_simple(topic)`:
   - Uses a prompt template: "Provide 3 expert insights about {topic}."
   - Calls `opencode run -m <model>` and returns the raw response
   - Prints the response

2. **Stage 2 — Prompt chaining**: Implement `stage2_chained(question)`:
   - Step 1: "What topic is this question about? Reply with ONE word." → extract topic
   - Step 2: "Provide 3 expert insights about {topic}." → get insights
   - Step 3: "Answer this question using the insights below. Question: {question}. Insights: {insights}" → final answer
   - Prints each intermediate result

3. **Stage 3 — RAG**: Implement `stage3_rag(question)`:
   - Define a small knowledge base (5+ short docs about technology or science)
   - Retrieve top-3 chunks using keyword overlap
   - Generate answer with context: "Answer using ONLY this context: {chunks}. Question: {question}"
   - Prints retrieved chunks and the answer

4. **Stage 4 — Memory**: Implement `stage4_memory()`:
   - Simulate a 3-turn conversation:
     - Turn 1: "My name is Alice and I work in data science." → store in memory
     - Turn 2: "What are the best tools for data visualization?" → answer using memory (should reference data science context)
     - Turn 3: "Can you summarize what we've discussed?" → answer using all previous turns
   - Print the conversation history at each step

5. **Stage 5 — Tools**: Implement `stage5_tools(query)`:
   - Define 2 tools: `calculator(expr)` and `search(query)`
   - Use the agent loop from Part 6: LLM decides tool calls, executes, feeds back observation
   - Test with: "What's 100/7 rounded to the nearest integer?" → should call calculator

6. Runs all 5 stages on the same base topic (e.g., "machine learning") and prints a **comparison** showing what each stage adds.

> Bonus: implement Stage 6 (agent) that combines memory + tools + planning in a single loop. The agent should remember past interactions, use tools when needed, and plan multi-step tasks.

### How to start

Tell me one of:
- *"Scaffold llm_app_builder.py with all 5 stages"*
- *"Start with Stage 1 only, I'll add stages as I go"*
- *"Use opencode CLI for all LLM calls"*
- *"Show me the progression diagram first"*
