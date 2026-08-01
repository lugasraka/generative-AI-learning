# Part 9 — Advanced Features & LLMOps

> Source: [week8_advanced_features.md](../../Applied_LLMs_Mastery_2024/week8_advanced_features.md)

## Concept in 10 lines

- **LLMOps** = the specialized practices for deploying, monitoring, and maintaining LLMs in production. Think MLOps, but specifically for language models.
- LLM apps go through 7 stages: pre-development, data preparation, model development, optimization, deployment, monitoring, and continuous improvement.
- **Deployment considerations**: external providers (OpenAI API) vs. self-hosting (open-source models), system design for scalability, cost management, data privacy, and infrastructure as code.
- **Monitoring** tracks: user-facing metrics (latency, availability, error rates), model outputs (accuracy, confidence), data inputs (logging, traceability), and resource utilization.
- **Data drift** = the distribution of incoming data changes over time, degrading model performance. Detection requires comparing current inputs against a baseline.
- **Model drift** = the model's performance degrades even without data changes (e.g., user expectations evolve, new edge cases appear).
- **Security** involves data security (encryption, access controls), model security (validation, checksums), infrastructure security (firewalls, network isolation), and ethical considerations.
- **Compliance** means following regulations like GDPR (data privacy), EU AI Act (AI-specific rules), and industry-specific requirements.
- The key LLMOps principle: **you can't improve what you don't measure**. Start logging everything from day one.

## Vibe-coding challenge

**Build an LLMOps monitoring dashboard.** Create a Python script called `llm_ops_dashboard.py` that:

1. **Generates synthetic production logs** — 100 mock LLM API calls with:
   - `timestamp` (sequential, one per minute)
   - `latency_ms` (normally distributed, mean=800, stddev=400, min=50)
   - `tokens_input` (random 50-2000)
   - `tokens_output` (random 20-500)
   - `cost_usd` (computed: `tokens_input * 0.00001 + tokens_output * 0.00003`)
   - `quality_score` (1-5, mostly 3-4, some 1-2 for "bad" calls)
   - `error` (True/False, ~5% error rate)
   - Inject anomalies: 5 calls with latency > 3000ms, 3 calls with quality_score=1, 2 error spikes

2. **Computes dashboard metrics**:
   - Latency: p50, p95, p99
   - Cost: total, average per call, cost per 1K tokens
   - Quality: average, distribution (how many 1s, 2s, 3s, 4s, 5s)
   - Errors: total errors, error rate
   - Throughput: calls per minute

3. **Anomaly detection**:
   - Flag calls where latency > p95
   - Flag calls where quality_score < 2
   - Flag time windows with error rate > 10%
   - Print each anomaly with timestamp and details

4. **Drift detection**:
   - Split logs into first-half and second-half
   - Compare average quality scores (is quality degrading?)
   - Compare average latencies (is the model getting slower?)
   - Print "DRIFT DETECTED" or "STABLE" with the comparison

5. **Alert rules**:
   - `CRITICAL`: error rate > 15%
   - `WARNING`: p95 latency > 2000ms OR average quality < 3
   - `INFO`: cost exceeds $X threshold
   - Print alerts with severity, metric, and current value

6. **Export**: write all logs to a CSV file (`dashboard_logs.csv`) and print a summary table to the console.

> Bonus: add a **trend analysis** that groups logs by 10-minute windows and shows how metrics change over time. Also add a **recommendation engine** that uses opencode CLI to analyze the dashboard data and suggest 3 optimizations (e.g., "Consider caching frequent queries to reduce cost").

### How to start

Tell me one of:
- *"Scaffold llm_ops_dashboard.py in Python"*
- *"Start with just log generation and basic metrics"*
- *"I want to focus on the anomaly and drift detection"*
- *"Show me the alert rules design first"*
