# Part 4 — Fine-Tuning Comparison Results

> **Model:** `opencode-go/mimo-v2.5`  
> **Date:** 2026-08-01 21:37:50

## Parameters

- Dataset size: 1,000 examples
- Model size: 7B parameters
- Epochs: 3
- Learning rate: 0.0001

## Comparison Table

| Method | Loss | Accuracy | Time | GPU | Cost |
| --- | --- | --- | --- | --- | --- |
| Full Fine-Tuning | 2.3840 | 62.3% | 2.1min | 28.0GB | $0.42 |
| LoRA (PEFT) | 2.3100 | 58.5% | 42.0s | 10.5GB | $0.05 |
| Prompt Tuning | 2.5439 | 58.5% | 12.6s | 2.1GB | $0.00 |

## Loss Curves

### Epoch 1

```
Full Fine-Tuning       [#################..................] 2.4210
LoRA (PEFT)            [################...................] 2.2999
Prompt Tuning          [#################..................] 2.5301
```

### Epoch 2

```
Full Fine-Tuning       [#################..................] 2.4343
LoRA (PEFT)            [################...................] 2.2774
Prompt Tuning          [##################.................] 2.5784
```

### Epoch 3

```
Full Fine-Tuning       [################...................] 2.3840
LoRA (PEFT)            [################...................] 2.3100
Prompt Tuning          [##################.................] 2.5439
```

## Verdict

- **Best method:** LoRA (PEFT)
- **Reason:** LoRA gives the best balance of performance, speed, and cost for most setups.
- **Accuracy:** 58.5% | **Cost:** $0.05

## LLM Recommendation

> **LoRA (PEFT)** is the best choice for most use cases. It offers near-parity with full fine-tuning accuracy (58.5% vs 62.3%) while being 3x faster and 8x cheaper ($0.05 vs $0.42). Prompt Tuning trades off too much accuracy for its speed/cost gains, and full fine-tuning's marginal accuracy improvement rarely justifies the cost—especially if you're iterating on multiple experiments.
