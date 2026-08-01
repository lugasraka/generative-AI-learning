# Part 1 — LLM Foundations & Real-World Use Cases

> Source: [week1_part1_foundations.md](../../Applied_LLMs_Mastery_2024/week1_part1_foundations.md)

## Concept in 10 lines

- **Generative AI** is a subset of AI that creates new content. **LLMs** are the most prominent type — large neural networks trained on massive text corpora.
- "Large" refers to three things: scale of architecture (billions of parameters), scale of training data (trillions of tokens), and scale of compute.
- LLMs learn by predicting the next token. Their "intelligence" emerges from pattern recognition at scale.
- **Zero-shot** = no examples. **Few-shot** = a few examples in the prompt. **Domain adaptation** = specialized training for a field.
- LLMs are not databases — they encode statistical patterns, not facts. This is why they hallucinate.
- There are 7 core use cases: content generation, translation, summarization, Q&A/chatbots, content moderation, information retrieval, educational tools.
- Each use case has different requirements for accuracy, latency, and creativity — which determines which model and approach to use.
- The biggest challenges are data quality, ethical concerns, technical limitations (context length, hallucination), and deployment costs.

## Vibe-coding challenge

**Build a use-case classifier.** Create a Python script called `use_case_classifier.py` that:

1. Defines 7 use-case categories with descriptions:
   - `content_generation` — writing, drafting, creative text
   - `translation` — language-to-language conversion
   - `summarization` — condensing long text
   - `qa_chatbot` — question answering, conversational
   - `content_moderation` — detecting harmful/inappropriate content
   - `information_retrieval` — extracting facts from documents
   - `educational_tools` — tutoring, explaining, teaching

2. Hardcodes 10 sample business problems as test cases, e.g.:
   - "We need to automatically reply to customer support tickets" → `qa_chatbot`
   - "Our legal team needs to review 500 contracts for key clauses" → `information_retrieval`
   - "We want to generate product descriptions from specifications" → `content_generation`

3. Implements a **rule-based classifier** that uses keyword matching to assign each problem to a category. Define keyword lists for each category (e.g., `qa_chatbot` keywords: "answer", "reply", "support", "chat", "conversation").

4. Implements an **LLM-based classifier** that sends each problem to `opencode run -m <model>` and asks it to classify into one of the 7 categories.

5. Prints a **side-by-side comparison table** showing: problem text, rule-based prediction, LLM prediction, and whether they agree.

6. Prints a **summary**: how many agreements, how many disagreements, which problems the LLM classified differently.

> Bonus: add a `custom` mode where the user types a business problem and both classifiers predict its use case. Also add a confidence score (0-1) to the rule-based classifier based on how many keywords matched.

### How to start

Tell me one of:
- *"Scaffold use_case_classifier.py in Python"*
- *"I want to start with just the rule-based classifier, no LLM yet"*
- *"Use opencode CLI for the LLM classifier"*
- *"Walk me through the keyword design first, no code"*
