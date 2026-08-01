# Part 4 — Fine-Tuning LLMs

> Source: [week3_finetuning_llms.md](../../Applied_LLMs_Mastery_2024/week3_finetuning_llms.md)

## Concept in 10 lines

- **Fine-tuning** = take a pre-trained model and continue training on your specific data. Transforms a generalist into a specialist.
- **Full fine-tuning** updates all model parameters. Best performance but requires massive GPU memory and risks catastrophic forgetting.
- **Instruction fine-tuning** trains the model to follow instructions (input-output pairs with explicit instructions). Uses datasets like "Natural Instructions" (193K examples).
- **RLHF (Reinforcement Learning from Human Feedback)**: 3 steps — pretrain → train a reward model on human preferences → fine-tune with PPO. This is how ChatGPT became "helpful."
- **DPO (Direct Preference Optimization)**: simpler than RLHF. No separate reward model — directly optimizes for human preferences. Comparison: DPO is faster and simpler; RLHF is more flexible.
- **PEFT (Parameter-Efficient Fine-Tuning)** = only update a small subset of parameters (1-10%). Keeps the rest frozen. Dramatically reduces cost and memory.
- **LoRA** is the most popular PEFT method: adds small trainable matrices to each layer, freezes the original weights. Trains in hours on a single GPU.
- **Prompt tuning** = prepend learnable "soft tokens" to the input. The cheapest method — you're only learning a few hundred parameters.
- The choice depends on: how much data you have, how different your domain is from the training data, your compute budget, and how much control you need over the model's behavior.

## Vibe-coding challenge

**Build a fine-tuning comparison simulator.** Create a Python script called `finetuning_comparison.py` that:

1. Defines 3 fine-tuning methods with their properties:
   - `full_finetuning` — updates: "100%", gpu_memory: "very high", speed: "slow", risk_of_forgetting: "high"
   - `lora_peft` — updates: "~1-5%", gpu_memory: "moderate", speed: "fast", risk_of_forgetting: "low"
   - `prompt_tuning` — updates: "<1%", gpu_memory: "minimal", speed: "very fast", risk_of_forgetting: "none"

2. Asks the user for input parameters:
   - "Dataset size (number of examples):" (default: 1000)
   - "Model size (billions of parameters):" (default: 7)
   - "Number of training epochs:" (default: 3)
   - "Learning rate:" (default: 0.0001)
   - "Which method to simulate?" (full / lora / prompt / all)

3. Implements a **mock training simulator** that generates realistic-looking metrics:
   - For each epoch, compute a simulated loss that decreases (with some noise)
   - Estimate training time based on: method, model size, dataset size, epochs
   - Estimate GPU memory usage based on: method, model size
   - Estimate final accuracy based on: dataset size, epochs, learning rate, method
   - Use formulas like: `loss(epoch) = initial_loss * exp(-learning_rate * epoch * data_factor) + noise`

4. If "all" is selected, runs the simulation for all 3 methods and prints a **side-by-side comparison table** with columns: method, final_loss, final_accuracy, training_time, gpu_memory, cost_estimate.

5. Prints a **verdict**: which method is best for the user's specific parameters, with a 1-line explanation.

6. Sends the comparison summary to `opencode run -m <model>` and asks: "Given these results, which fine-tuning method would you recommend and why? Answer in 2 sentences."

> Bonus: add a "budget optimizer" that takes a dollar budget (e.g., $500) and tells you the maximum model size, dataset size, and epochs you can afford with each method. Also generate a simple ASCII loss curve showing training progression.

### How to start

Tell me one of:
- *"Scaffold finetuning_comparison.py in Python"*
- *"Start with just the simulation formulas, make them realistic"*
- *"I want to compare all 3 methods side by side"*
- *"Show me the math behind the simulation first"*
