# Part 9 — LLMOps Dashboard Results

> **Model:** `opencode-go/deepseek-v4-flash`  
> **Date:** 2026-08-02 10:57:04
> **Calls:** 100 (one per minute)

## Dashboard Metrics

| Metric | Value |
|---|---|
| Latency p50 / p95 / p99 | 790.0 / 3147.0 / 4172.0 ms |
| Average latency | 1008.0 ms |
| Total cost | $1.7962 |
| Avg cost per call | $0.01796 |
| Cost per 1K tokens | $0.013919 |
| Average quality | 3.12 |
| Quality distribution | {1: 11, 2: 12, 3: 36, 4: 36, 5: 5} |
| Errors | 14 (14.0%) |
| Throughput | 1.01 calls/min |

## Anomalies

- `latency` 2026-08-02T00:04:00 — latency=3495ms > p95=3147ms
- `quality` 2026-08-02T00:04:00 — quality_score=1 < 2
- `quality` 2026-08-02T00:12:00 — quality_score=1 < 2
- `quality` 2026-08-02T00:16:00 — quality_score=1 < 2
- `latency` 2026-08-02T00:23:00 — latency=3962ms > p95=3147ms
- `quality` 2026-08-02T00:26:00 — quality_score=1 < 2
- `quality` 2026-08-02T00:33:00 — quality_score=1 < 2
- `quality` 2026-08-02T00:38:00 — quality_score=1 < 2
- `quality` 2026-08-02T00:39:00 — quality_score=1 < 2
- `latency` 2026-08-02T00:47:00 — latency=4911ms > p95=3147ms
- `quality` 2026-08-02T00:49:00 — quality_score=1 < 2
- `quality` 2026-08-02T01:04:00 — quality_score=1 < 2
- `latency` 2026-08-02T01:11:00 — latency=4172ms > p95=3147ms
- `quality` 2026-08-02T01:13:00 — quality_score=1 < 2
- `quality` 2026-08-02T01:24:00 — quality_score=1 < 2
- `latency` 2026-08-02T01:32:00 — latency=3182ms > p95=3147ms
- `window` 2026-08-02T00:40:00 — minutes 40-49 error_rate=50% > 10%
- `window` 2026-08-02T01:20:00 — minutes 80-89 error_rate=50% > 10%

## Drift Detection

- Quality: **DRIFT DETECTED** — first=2.96, second=3.28, delta=0.32
- Latency: **STABLE** — first=1020.4ms, second=995.5ms, delta=-2.44%

## Alerts

- `WARNING` latency_p95=3147ms / avg_quality=3.12 (current=3147.0, rule=p95 > 2000ms OR avg quality < 3)
- `INFO` total_cost_usd (current=1.7962, rule=> $1.5)

## Trend Analysis

| Bucket | Minutes | Avg latency | Avg quality | Error rate |
|---|---:|---:|---:|---:|
| 1 | 0-9 | 1230.7 ms | 3.2 | 10.0% |
| 2 | 10-19 | 799.0 ms | 2.7 | 0.0% |
| 3 | 20-29 | 989.6 ms | 3.5 | 0.0% |
| 4 | 30-39 | 829.9 ms | 3.0 | 0.0% |
| 5 | 40-49 | 1252.8 ms | 2.4 | 50.0% |
| 6 | 50-59 | 943.0 ms | 3.3 | 10.0% |
| 7 | 60-69 | 920.2 ms | 3.3 | 0.0% |
| 8 | 70-79 | 1108.5 ms | 3.2 | 10.0% |
| 9 | 80-89 | 1088.0 ms | 3.2 | 50.0% |
| 10 | 90-99 | 917.8 ms | 3.4 | 10.0% |

## Recommendations

1. Cache frequent queries to reduce cost and latency.
2. Route low-confidence outputs to human review with a quality guardrail.
3. Right-size the model choice per request tier to balance quality and spend.

## Takeaway

Monitoring turns logs into decisions: percentile latency surfaces slow tails, per-bucket error rates catch localized spikes, drift checks catch slow degradation, and alert rules make the response automatable. You cannot improve what you do not measure.
