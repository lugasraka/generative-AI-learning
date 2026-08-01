# Part 11 — Emerging Research Trends

> Source: [week10_research_trends.md](../../Applied_LLMs_Mastery_2024/week10_research_trends.md)

## Concept in 10 lines

- **Multimodal LLMs** process text, images, audio, and video together. Architecture: Modality Encoder → Input Projector → LLM Backbone → Output Projector → Modality Generator. Examples: GPT-4o, Gemini, Claude 3.
- **Open-source models** are catching up fast: LLaMA (Meta, 7B-70B), Mistral (7B outperforms many 13B models), OLMo (fully open with training data and code), LLM360 (open checkpoints and datasets).
- **LLM Agents** combine autonomy, task completion, and tool use. Architecture: Profiling (who am I?) + Memory (what do I know?) + Planning (what should I do?) + Action (what tools do I call?).
- **Domain-specific LLMs** are specialized for fields: clinical (BioBERT, Hi-BEHRT), finance (BloombergGPT, FinGPT), code (WizardCoder, CodeT5).
- **Mixture of Experts (MoEs)** replace dense feed-forward layers with sparse expert layers. Only a few experts activate per token → faster training + inference. Mistral Mixtral 8x7B is the most famous example.
- **Mamba** is a new architecture based on Selective State Spaces. Linear time complexity (vs. quadratic for Transformers). 5x faster for long sequences. A potential Transformer successor.
- **RWKV** is a hybrid: RNN-like linear scaling + Transformer-like parallelized training. Integrates with HuggingFace.
- The big trend: models are getting **smaller but smarter** (efficient architectures), **more multimodal** (text+image+audio+video), and **more agentic** (can act, not just generate).

## Vibe-coding challenge

**Build a research trend explorer.** Create a Python script called `research_explorer.py` that:

1. Defines 5 research areas as a nested data structure:
   ```python
   AREAS = {
       "multimodal_llms": {
           "title": "Multimodal LLMs",
           "subtopics": {
               "architecture": "5 components: encoder, projector, backbone, output projector, generator",
               "training": "MM pre-training + instruction tuning (SFT + RLHF)",
               "future": "Mobile deployment, embodied intelligence, continual tuning",
               "key_models": "GPT-4o, Gemini, Claude 3, LLaVA"
           }
       },
       "open_source": { ... },   # LLaMA, Mistral, OLMo, LLM360
       "agents": { ... },        # architecture, capabilities, future directions
       "domain_specific": { ... }, # clinical, finance, code
       "new_architectures": { ... } # MoE, Mamba, RWKV
   }
   ```

2. Presents an **interactive menu**:
   ```
   Research Areas:
   1. Multimodal LLMs
   2. Open-Source Models
   3. LLM Agents
   4. Domain-Specific LLMs
   5. New Architectures
   6. Personalized reading list
   0. Quit
   ```

3. For each area, shows sub-topics as a submenu with details for each.

4. For any sub-topic, calls `opencode run -m <model>` with: "Explain this concept in 3 simple sentences for someone learning about LLMs: {subtopic_details}". Prints the "ELI5" explanation.

5. **Personalized reading list** (option 6):
   - Ask the user: "Which areas interest you most? (comma-separated numbers)"
   - Ask: "How much time do you have? (15min / 30min / 1hr)"
   - For the selected areas, generate a prioritized reading list using opencode CLI: "Given these LLM research topics: {topics}, and the user has {time}, recommend 3-5 papers or articles to read, prioritized by impact. Return a numbered list with title and one-line reason."

6. **Comparison mode**: if the user selects two areas, call opencode CLI to: "Compare and contrast {area1} and {area2} in LLM research. What do they have in common? How do they differ? Which is more impactful? Answer in 4 sentences."

> Bonus: add a **trend timeline** that shows when each major model/paper was released (hardcode 10+ entries with dates) and prints a chronological ASCII timeline. Also add a **quiz mode** that asks the user 5 multiple-choice questions about the research areas.

### How to start

Tell me one of:
- *"Scaffold research_explorer.py in Python"*
- *"Start with just the data structure and menu, no LLM calls yet"*
- *"Use opencode CLI for ELI5 explanations"*
- *"Let me fill in the subtopic details myself"*
