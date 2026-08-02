# Part 12 — Neural Network Foundations Results

> **Model:** `opencode-go/deepseek-v4-flash`  
> **Date:** 2026-08-02 12:40:31

## Tokenization

- Word vocab sizes: [9, 5, 5]
- Char vocab sizes: [28, 20, 13]

## Attention

- 4 tokens, d_k=3, Q/K/V hardcoded
- Softmax normalization + weighted sum over values

## Positional Encoding

- 8 positions, d_model=4, sine/cosine waves

## Transformer Block

- Self-attention -> residual + layer norm -> FFN -> residual + layer norm

## Multi-Head Attention

- 2 heads, d_k=2, concatenated and projected back to d_model=4

## BPE

- 10-word corpus, 5 merge iterations

## Architecture Evolution

RNN -> LSTM -> Seq2Seq -> Attention -> Transformer -> BERT -> GPT -> T5 -> Modern LLMs

## Takeaway

Every modern LLM is built from these foundational blocks: tokenization converts text to tokens, attention lets tokens talk to each other, positional encoding adds order, and transformer layers stack these operations to learn deep language patterns.
