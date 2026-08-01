# Part 12 — Neural Network Foundations

> Source: [week11_foundations.md](../../Applied_LLMs_Mastery_2024/week11_foundations.md)

## Concept in 10 lines

- **Generative models** create new data (text, images). **Discriminative models** classify or predict. LLMs are generative.
- **RNNs** process sequences step-by-step, maintaining a hidden state. Problem: vanishing gradients make them forget long-range dependencies.
- **LSTMs** fix this with a memory cell and 3 gates (input, forget, output). Better at long-range dependencies, but still sequential (slow).
- **Seq2Seq** models (encoder-decoder) handle variable-length input/output. Good for translation, summarization. But the encoder compresses everything into one vector — information bottleneck.
- **Attention** solves the bottleneck: the decoder looks at ALL encoder states (not just the last one), learning which parts of the input to focus on for each output token.
- **Transformers** replace recurrence entirely with self-attention. Every token attends to every other token in parallel. This enables massive parallelization and is why Transformers scale so well.
- **BERT** = bidirectional encoder (sees left + right context). Great for classification, extraction. Uses masked language modeling.
- **GPT** = autoregressive decoder (sees only left context). Great for generation. Uses next-token prediction.
- **T5** = encoder-decoder that frames every NLP task as text-to-text. Unified framework.
- Modern LLMs (LLaMA, ChatGPT) build on TransformerDecoder with improvements: better training data, RLHF alignment, longer context, multimodal capabilities.

## Vibe-coding challenge

**Build a neural network concept demonstrator.** Create a Python script called `nn_playground.py` that:

1. **Tokenization** — Implement two tokenizers:
   - `word_tokenize(text)` — splits on whitespace, returns list of words
   - `char_tokenize(text)` — splits into individual characters
   - `vocab_size(tokens)` — returns the number of unique tokens
   - Test on 3 sample sentences, print token lists and vocab sizes for both

2. **Scaled dot-product attention** — Implement:
   ```python
   def attention(Q, K, V):
       # Q, K, V are lists of lists (matrices)
       # score = Q * K^T / sqrt(d_k)
       # weights = softmax(score)
       # output = weights * V
       return output, weights
   ```
   - Create a 4x3 Q matrix and 4x3 K, V matrices (hardcoded, small values)
   - Compute attention scores, apply softmax, compute output
   - Print the attention weights as a 4x4 matrix (ASCII table)

3. **Positional encoding** — Implement sine/cosine positional encoding:
   ```python
   def positional_encoding(position, d_model):
       # PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
       # PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
   ```
   - Generate encodings for 8 positions with d_model=4
   - Print the encoding matrix as an ASCII table
   - Print a simple visualization (e.g., `+`, `-`, `.` for positive/negative/zero values)

4. **Simple transformer block** — Simulate a single attention head + feed-forward:
   - Input: 4 tokens, each with a 4-dimensional embedding (hardcoded)
   - Run through attention → add & normalize (residual connection + layer norm)
   - Run through a simple feed-forward (2 linear layers with ReLU)
   - Add & normalize again
   - Print the input and output embeddings side by side

5. Uses `opencode run -m <model>` to explain each computation: send the current step's input/output and ask "Explain what just happened in 2 sentences." Print the explanation alongside the math.

6. Prints a **summary** at the end showing the progression: RNN → LSTM → Seq2Seq → Attention → Transformer, with one-line descriptions.

> Bonus: implement a **multi-head attention** function that splits Q, K, V into 2 heads, runs attention on each, concatenates the outputs, and projects back. Also implement **byte-pair encoding (BPE)** tokenization on a small corpus (10 words) — show how it iteratively merges the most frequent pairs.

### How to start

Tell me one of:
- *"Scaffold nn_playground.py in Python"*
- *"Start with just tokenization and attention, skip the transformer block"*
- *"Use opencode CLI for the explanations"*
- *"Show me the attention math step by step first"*
