"""
Part 9 — Advanced Features & LLMOps: Monitoring Dashboard

Generates synthetic production logs for 100 mock LLM API calls, computes
dashboard metrics, detects anomalies and drift, applies alert rules, exports
logs to CSV, and optionally asks an LLM for optimization recommendations.

Run:  python llm_ops_dashboard.py
      python llm_ops_dashboard.py --skip-llm
      python llm_ops_dashboard.py --html
"""

import argparse
import csv
import datetime
import html
import json
import math
import os
import random
import re
import subprocess
import sys
from typing import Sequence, TypedDict

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")

MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/deepseek-v4-flash")
LLM_TIMEOUT_SECONDS = 60

N_CALLS = 100
MINUTE_SPACING = 1
START_TIME = datetime.datetime(2026, 8, 2, 0, 0, 0)
BUCKET_SIZE = 10
INFO_COST_THRESHOLD_USD = 1.5

Log = dict[str, float | int | str | bool]

Metrics = TypedDict(
    "Metrics",
    {
        "latency_p50": float,
        "latency_p95": float,
        "latency_p99": float,
        "avg_latency": float,
        "total_cost": float,
        "avg_cost_per_call": float,
        "cost_per_1k_tokens": float,
        "avg_quality": float,
        "quality_dist": dict[int, int],
        "total_errors": int,
        "error_rate": float,
        "throughput_calls_per_min": float,
    },
)

# ---------- Log Generation ----------


def generate_logs(n: int = N_CALLS) -> list[Log]:
    """Create n synthetic one-minute-spaced API call logs."""
    random.seed(42)
    logs: list[Log] = []
    for i in range(n):
        latency = max(50, int(random.gauss(800, 400)))
        tokens_input = random.randint(50, 2000)
        tokens_output = random.randint(20, 500)
        cost = tokens_input * 0.00001 + tokens_output * 0.00003
        quality = random.choices([1, 2, 3, 4, 5], weights=[4, 10, 40, 40, 6])[0]
        error = random.random() < 0.06
        timestamp = (
            START_TIME + datetime.timedelta(minutes=i * MINUTE_SPACING)
        ).isoformat()
        logs.append(
            {
                "timestamp": timestamp,
                "latency_ms": latency,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "cost_usd": round(cost, 6),
                "quality_score": quality,
                "error": error,
            }
        )
    return logs


def inject_anomalies(logs: list[Log]) -> None:
    """Plant latency, quality, and error-spike anomalies into the logs."""
    for i in [4, 6, 23, 47, 71, 92]:
        logs[i]["latency_ms"] = random.randint(2800, 5000)
    for i in [12, 33, 64]:
        logs[i]["quality_score"] = 1
    for i in [40, 42, 44, 46, 48, 80, 82, 84, 86, 88]:
        logs[i]["error"] = True


# ---------- Metrics ----------


def percentile(values: list[float], pct: float) -> float:
    """Return the nearest-rank percentile of a sorted value list."""
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(math.ceil(pct / 100 * len(ordered))) - 1))
    return ordered[index]


def mean(values: Sequence[float]) -> float:
    """Return the arithmetic mean of a value sequence."""
    return sum(values) / len(values)


def compute_metrics(logs: list[Log]) -> Metrics:
    """Aggregate latency, cost, quality, error, and throughput metrics."""
    latencies = [float(log["latency_ms"]) for log in logs]
    costs = [float(log["cost_usd"]) for log in logs]
    total_tokens = sum(
        int(log["tokens_input"]) + int(log["tokens_output"]) for log in logs
    )
    quality_scores = [int(log["quality_score"]) for log in logs]
    errors = [log for log in logs if log["error"]]
    minutes = (N_CALLS - 1) * MINUTE_SPACING
    return {
        "latency_p50": percentile(latencies, 50),
        "latency_p95": percentile(latencies, 95),
        "latency_p99": percentile(latencies, 99),
        "avg_latency": round(mean(latencies), 1),
        "total_cost": round(sum(costs), 4),
        "avg_cost_per_call": round(sum(costs) / len(logs), 5),
        "cost_per_1k_tokens": round(sum(costs) / total_tokens * 1000, 6),
        "avg_quality": round(mean(quality_scores), 2),
        "quality_dist": {score: quality_scores.count(score) for score in range(1, 6)},
        "total_errors": len(errors),
        "error_rate": round(len(errors) / len(logs) * 100, 2),
        "throughput_calls_per_min": round(len(logs) / minutes, 2),
    }


# ---------- Anomaly Detection ----------


def bucketize(logs: list[Log], size: int = BUCKET_SIZE) -> list[list[Log]]:
    """Split logs into contiguous fixed-size buckets."""
    return [logs[i : i + size] for i in range(0, len(logs), size)]


def detect_anomalies(
    logs: list[Log], metrics: Metrics
) -> list[dict[str, str | float | int]]:
    """Flag slow calls, low-quality calls, and high-error time buckets."""
    p95 = float(metrics["latency_p95"])
    anomalies: list[dict[str, str | float | int]] = []
    for log in logs:
        if float(log["latency_ms"]) > p95:
            anomalies.append(
                {
                    "timestamp": str(log["timestamp"]),
                    "type": "latency",
                    "detail": f"latency={log['latency_ms']}ms > p95={p95:.0f}ms",
                }
            )
        if int(log["quality_score"]) < 2:
            anomalies.append(
                {
                    "timestamp": str(log["timestamp"]),
                    "type": "quality",
                    "detail": f"quality_score={log['quality_score']} < 2",
                }
            )
    for bucket_index, bucket in enumerate(bucketize(logs)):
        errors_in_bucket = sum(1 for log in bucket if log["error"])
        bucket_rate = errors_in_bucket / len(bucket) * 100
        if bucket_rate > 10:
            start_minute = bucket_index * BUCKET_SIZE
            end_minute = start_minute + len(bucket) - 1
            anomalies.append(
                {
                    "timestamp": str(bucket[0]["timestamp"]),
                    "type": "window",
                    "detail": (
                        f"minutes {start_minute}-{end_minute} error_rate="
                        f"{bucket_rate:.0f}% > 10%"
                    ),
                }
            )
    return anomalies


# ---------- Drift Detection ----------


def drift_detection(logs: list[Log]) -> dict[str, str | float]:
    """Compare first-half and second-half quality and latency."""
    half = len(logs) // 2
    first = logs[:half]
    second = logs[half:]
    first_quality = mean([float(log["quality_score"]) for log in first])
    second_quality = mean([float(log["quality_score"]) for log in second])
    first_latency = mean([float(log["latency_ms"]) for log in first])
    second_latency = mean([float(log["latency_ms"]) for log in second])
    quality_delta = round(second_quality - first_quality, 3)
    latency_delta_pct = round((second_latency - first_latency) / first_latency * 100, 2)
    quality_status = "DRIFT DETECTED" if abs(quality_delta) >= 0.2 else "STABLE"
    latency_status = "DRIFT DETECTED" if abs(latency_delta_pct) >= 15 else "STABLE"
    return {
        "first_quality": round(first_quality, 2),
        "second_quality": round(second_quality, 2),
        "quality_delta": quality_delta,
        "first_latency": round(first_latency, 1),
        "second_latency": round(second_latency, 1),
        "latency_delta_pct": latency_delta_pct,
        "quality_status": quality_status,
        "latency_status": latency_status,
    }


# ---------- Alert Rules ----------


def alert_rules(
    metrics: Metrics,
) -> list[dict[str, str | float]]:
    """Evaluate CRITICAL, WARNING, and INFO alert rules."""
    alerts: list[dict[str, str | float]] = []
    if float(metrics["error_rate"]) > 15:
        alerts.append(
            {
                "severity": "CRITICAL",
                "metric": "error_rate",
                "value": float(metrics["error_rate"]),
                "threshold": "> 15%",
            }
        )
    if float(metrics["latency_p95"]) > 2000 or float(metrics["avg_quality"]) < 3:
        alerts.append(
            {
                "severity": "WARNING",
                "metric": (
                    f"latency_p95={float(metrics['latency_p95']):.0f}ms / "
                    f"avg_quality={float(metrics['avg_quality'])}"
                ),
                "value": max(
                    float(metrics["latency_p95"]), float(metrics["avg_quality"])
                ),
                "threshold": "p95 > 2000ms OR avg quality < 3",
            }
        )
    if float(metrics["total_cost"]) > INFO_COST_THRESHOLD_USD:
        alerts.append(
            {
                "severity": "INFO",
                "metric": "total_cost_usd",
                "value": float(metrics["total_cost"]),
                "threshold": f"> ${INFO_COST_THRESHOLD_USD}",
            }
        )
    return alerts


# ---------- Trend Analysis ----------


def trend_analysis(logs: list[Log]) -> list[dict[str, float | int | str]]:
    """Summarize latency, quality, and error rate per 10-minute bucket."""
    trends: list[dict[str, float | int | str]] = []
    for bucket_index, bucket in enumerate(bucketize(logs)):
        start_minute = bucket_index * BUCKET_SIZE
        end_minute = start_minute + len(bucket) - 1
        trends.append(
            {
                "bucket": bucket_index + 1,
                "minutes": f"{start_minute}-{end_minute}",
                "avg_latency": round(
                    mean([float(log["latency_ms"]) for log in bucket]), 1
                ),
                "avg_quality": round(
                    mean([float(log["quality_score"]) for log in bucket]), 2
                ),
                "error_rate": round(
                    sum(1 for log in bucket if log["error"]) / len(bucket) * 100, 1
                ),
            }
        )
    return trends


# ---------- LLM Recommendation Engine ----------


def ask_llm(prompt: str) -> str:
    """Send a prompt to opencode and return text or a bracketed error."""
    try:
        result = subprocess.run(
            ["opencode", "run", "-m", MODEL, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=LLM_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"[opencode timeout after {LLM_TIMEOUT_SECONDS}s]"
    except OSError as error:
        return f"[opencode error] {error}"
    if result.returncode != 0:
        return f"[opencode error] {result.stderr.strip()}"
    return result.stdout.strip()


FALLBACK_RECOMMENDATIONS: list[str] = [
    "Cache frequent queries to reduce cost and latency.",
    "Route low-confidence outputs to human review with a quality guardrail.",
    "Right-size the model choice per request tier to balance quality and spend.",
]


def build_dashboard_summary(
    metrics: Metrics,
    anomalies: list[dict[str, str | float | int]],
    drift: dict[str, str | float],
    trends: list[dict[str, float | int | str]],
) -> str:
    """Render a compact text summary of the dashboard for the LLM."""
    lines = [
        f"- Calls: {N_CALLS}, error rate: {metrics['error_rate']}%",
        f"- Latency p50/p95/p99: {metrics['latency_p50']}/{metrics['latency_p95']}/{metrics['latency_p99']} ms",
        f"- Total cost: ${metrics['total_cost']}, cost per 1K tokens: ${metrics['cost_per_1k_tokens']}",
        f"- Average quality: {metrics['avg_quality']}, quality distribution: {metrics['quality_dist']}",
        f"- Drift: quality {drift['quality_status']} (delta {drift['quality_delta']}), "
        f"latency {drift['latency_status']} (delta {drift['latency_delta_pct']}%)",
    ]
    if anomalies:
        lines.append(f"- Anomalies: {len(anomalies)} flagged")
    worst_trend = max(trends, key=lambda t: float(t["error_rate"]))
    lines.append(
        f"- Worst bucket: minutes {worst_trend['minutes']} "
        f"error rate {worst_trend['error_rate']}%"
    )
    return "\n".join(lines)


RECOMMEND_PROMPT = (
    "You are an LLMOps engineer reviewing a monitoring dashboard. "
    "Given the summary below, suggest exactly 3 concrete optimizations as a "
    'JSON array of strings: ["...", "...", "..."].\n\n'
    "DASHBOARD SUMMARY:\n{summary}\n\nJSON:"
)


def get_recommendations(summary: str) -> list[str]:
    """Ask the LLM for three optimizations and fall back deterministically."""
    raw = ask_llm(RECOMMEND_PROMPT.format(summary=summary))
    if raw.startswith("["):
        return FALLBACK_RECOMMENDATIONS
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return FALLBACK_RECOMMENDATIONS
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return FALLBACK_RECOMMENDATIONS
    if not isinstance(data, list):
        return FALLBACK_RECOMMENDATIONS
    items = [str(item) for item in data if isinstance(item, str)]
    return items[:3] or FALLBACK_RECOMMENDATIONS


# ---------- Display ----------


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def print_metrics(metrics: Metrics) -> None:
    print("\nDASHBOARD METRICS")
    print(
        f"  Latency p50 / p95 / p99:  {metrics['latency_p50']} / {metrics['latency_p95']} / {metrics['latency_p99']} ms"
    )
    print(f"  Average latency:          {metrics['avg_latency']} ms")
    print(f"  Total cost:               ${metrics['total_cost']}")
    print(f"  Avg cost per call:        ${metrics['avg_cost_per_call']}")
    print(f"  Cost per 1K tokens:       ${metrics['cost_per_1k_tokens']}")
    print(f"  Average quality:          {metrics['avg_quality']}")
    dist = metrics["quality_dist"]
    print(f"  Quality distribution:     {dist}")
    print(
        f"  Errors:                   {metrics['total_errors']} ({metrics['error_rate']}%)"
    )
    print(
        f"  Throughput:               {metrics['throughput_calls_per_min']} calls/min"
    )


def print_anomalies(anomalies: list[dict[str, str | float | int]]) -> None:
    print(f"\nANOMALIES ({len(anomalies)} flagged)")
    if not anomalies:
        print("  None")
        return
    for anomaly in anomalies:
        print(f"  [{anomaly['type']:<8}] {anomaly['timestamp']}  {anomaly['detail']}")


def print_drift(drift: dict[str, str | float]) -> None:
    print("\nDRIFT DETECTION")
    print(
        f"  Quality:  {drift['quality_status']}  "
        f"first={drift['first_quality']} second={drift['second_quality']} "
        f"delta={drift['quality_delta']}"
    )
    print(
        f"  Latency:  {drift['latency_status']}  "
        f"first={drift['first_latency']}ms second={drift['second_latency']}ms "
        f"delta={drift['latency_delta_pct']}%"
    )


def print_alerts(alerts: list[dict[str, str | float]]) -> None:
    print(f"\nALERTS ({len(alerts)})")
    if not alerts:
        print("  No alerts")
        return
    for alert in alerts:
        print(
            f"  [{alert['severity']:<8}] {alert['metric']} "
            f"(current={alert['value']}, rule={alert['threshold']})"
        )


def print_trends(trends: list[dict[str, float | int | str]]) -> None:
    print("\nTREND ANALYSIS (10-minute buckets)")
    header = "Bucket  Minutes  AvgLatency  AvgQuality  ErrorRate"
    print("  " + header)
    for trend in trends:
        print(
            f"  {trend['bucket']!s:<7}{trend['minutes']:<9}"
            f"{trend['avg_latency']!s:<12}{trend['avg_quality']!s:<12}"
            f"{trend['error_rate']}%"
        )


def print_recommendations(recommendations: list[str]) -> None:
    print("\nRECOMMENDATIONS")
    for i, recommendation in enumerate(recommendations, 1):
        print(f"  {i}. {recommendation}")


# ---------- Export ----------


def save_csv(logs: list[Log], path: str) -> None:
    """Write the logs to a CSV file."""
    fieldnames = [
        "timestamp",
        "latency_ms",
        "tokens_input",
        "tokens_output",
        "cost_usd",
        "quality_score",
        "error",
    ]
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for log in logs:
            writer.writerow({name: log[name] for name in fieldnames})


def save_results(
    metrics: Metrics,
    anomalies: list[dict[str, str | float | int]],
    drift: dict[str, str | float],
    alerts: list[dict[str, str | float]],
    trends: list[dict[str, float | int | str]],
    recommendations: list[str],
    path: str,
) -> None:
    """Write the dashboard report to a Markdown file."""
    lines = [
        "# Part 9 — LLMOps Dashboard Results",
        "",
        f"> **Model:** `{MODEL}`  ",
        f"> **Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> **Calls:** {N_CALLS} (one per minute)",
        "",
        "## Dashboard Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Latency p50 / p95 / p99 | {metrics['latency_p50']} / {metrics['latency_p95']} / {metrics['latency_p99']} ms |",
        f"| Average latency | {metrics['avg_latency']} ms |",
        f"| Total cost | ${metrics['total_cost']} |",
        f"| Avg cost per call | ${metrics['avg_cost_per_call']} |",
        f"| Cost per 1K tokens | ${metrics['cost_per_1k_tokens']} |",
        f"| Average quality | {metrics['avg_quality']} |",
        f"| Quality distribution | {metrics['quality_dist']} |",
        f"| Errors | {metrics['total_errors']} ({metrics['error_rate']}%) |",
        f"| Throughput | {metrics['throughput_calls_per_min']} calls/min |",
        "",
        "## Anomalies",
        "",
    ]
    if anomalies:
        for anomaly in anomalies:
            lines.append(
                f"- `{anomaly['type']}` {anomaly['timestamp']} — {anomaly['detail']}"
            )
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Drift Detection",
            "",
            f"- Quality: **{drift['quality_status']}** — "
            f"first={drift['first_quality']}, second={drift['second_quality']}, "
            f"delta={drift['quality_delta']}",
            f"- Latency: **{drift['latency_status']}** — "
            f"first={drift['first_latency']}ms, second={drift['second_latency']}ms, "
            f"delta={drift['latency_delta_pct']}%",
            "",
            "## Alerts",
            "",
        ]
    )
    if alerts:
        for alert in alerts:
            lines.append(
                f"- `{alert['severity']}` {alert['metric']} "
                f"(current={alert['value']}, rule={alert['threshold']})"
            )
    else:
        lines.append("- No alerts.")
    lines.extend(
        [
            "",
            "## Trend Analysis",
            "",
            "| Bucket | Minutes | Avg latency | Avg quality | Error rate |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for trend in trends:
        lines.append(
            f"| {trend['bucket']} | {trend['minutes']} | {trend['avg_latency']} ms | "
            f"{trend['avg_quality']} | {trend['error_rate']}% |"
        )
    lines.extend(
        [
            "",
            "## Recommendations",
            "",
        ]
    )
    for i, recommendation in enumerate(recommendations, 1):
        lines.append(f"{i}. {recommendation}")
    lines.extend(
        [
            "",
            "## Takeaway",
            "",
            "Monitoring turns logs into decisions: percentile latency surfaces "
            "slow tails, per-bucket error rates catch localized spikes, drift "
            "checks catch slow degradation, and alert rules make the response "
            "automatable. You cannot improve what you do not measure.",
        ]
    )
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


# ---------- HTML Dashboard ----------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LLMOps Monitoring Dashboard</title>
<style>
  :root {
    --green: #22c55e; --green-bg: #f0fdf4;
    --blue: #3b82f6;  --blue-bg: #eff6ff;
    --purple: #8b5cf6; --purple-bg: #f5f3ff;
    --orange: #f97316; --orange-bg: #fff7ed;
    --red: #ef4444;    --red-bg: #fef2f2;
    --amber: #f59e0b;
    --gray: #94a3b8;  --gray-bg: #f8fafc;
    --text: #1e293b;  --muted: #64748b;
    --border: #e2e8f0; --card-bg: #ffffff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: var(--text); background: #f1f5f9; line-height: 1.6; }
  .container { max-width: 1040px; margin: 0 auto; padding: 24px 16px 48px; }
  h1 { font-size: 1.8rem; margin-bottom: 4px; }
  .subtitle { color: var(--muted); font-size: 0.95rem; margin-bottom: 22px; }
  h2 { font-size: 1.25rem; margin: 28px 0 12px; }

  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
  .kpi { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
  .kpi .label { font-size: 0.78rem; color: var(--muted); text-transform: uppercase; letter-spacing: .03em; }
  .kpi .value { font-size: 1.35rem; font-weight: 700; margin-top: 4px; }
  .kpi.ok { border-left: 4px solid var(--green); }
  .kpi.warn { border-left: 4px solid var(--amber); }
  .kpi.crit { border-left: 4px solid var(--red); }

  .alerts-strip { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
  .chip { border-radius: 999px; padding: 5px 14px; font-size: 0.82rem; font-weight: 600; }
  .chip.critical { background: var(--red-bg); color: var(--red); border: 1px solid var(--red); }
  .chip.warning { background: var(--orange-bg); color: #c2410c; border: 1px solid var(--orange); }
  .chip.info { background: var(--blue-bg); color: #1d4ed8; border: 1px solid var(--blue); }
  .chip.ok { background: var(--green-bg); color: #166534; border: 1px solid var(--green); }

  .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .chart-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
  .chart-card h3 { font-size: 0.95rem; margin-bottom: 8px; }
  .chart-card svg { width: 100%; height: auto; display: block; }
  @media (max-width: 820px) { .charts-grid { grid-template-columns: 1fr; } }

  .drift-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .drift-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 14px 18px; }
  .drift-card .badge { display: inline-block; border-radius: 6px; padding: 2px 10px; font-size: 0.78rem; font-weight: 700; margin-bottom: 8px; }
  .badge.drift { background: var(--red-bg); color: var(--red); }
  .badge.stable { background: var(--green-bg); color: #166534; }

  .filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
  .filters button { background: var(--gray-bg); border: 1px solid var(--border); border-radius: 6px; padding: 5px 12px; font-size: 0.82rem; cursor: pointer; }
  .filters button.active { background: var(--blue); color: #fff; border-color: var(--blue); }

  table.data { width: 100%; border-collapse: collapse; background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; font-size: 0.85rem; }
  table.data th { text-align: left; padding: 9px 12px; border-bottom: 2px solid var(--border); background: var(--gray-bg); font-weight: 600; cursor: pointer; user-select: none; }
  table.data td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
  .scroll { max-height: 420px; overflow: auto; border-radius: 10px; border: 1px solid var(--border); }
  .scroll table.data { border: none; }

  .badge-tag { display: inline-block; border-radius: 6px; padding: 1px 8px; font-size: 0.75rem; font-weight: 700; }
  .tag-latency { background: var(--red-bg); color: var(--red); }
  .tag-quality { background: var(--orange-bg); color: #c2410c; }
  .tag-window { background: var(--purple-bg); color: #6d28d9; }

  .err { color: var(--red); font-weight: 700; }
  .low { color: var(--red); font-weight: 700; }

  .tooltip { position: fixed; display: none; background: #0f172a; color: #f8fafc; font-size: 0.75rem; padding: 6px 10px; border-radius: 6px; pointer-events: none; z-index: 50; max-width: 320px; white-space: pre; }

  .legend { display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.75rem; color: var(--muted); margin-top: 6px; }
  .legend .dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 4px; }

  ol.recs { margin-left: 20px; }
  ol.recs li { margin-bottom: 6px; }
  .takeaway { margin-top: 24px; background: var(--blue-bg); border: 1px solid var(--blue); border-radius: 10px; padding: 14px 18px; font-size: 0.9rem; }
</style>
</head>
<body>
<div class="container">
  <h1>LLMOps Monitoring Dashboard</h1>
  <p class="subtitle">Model: __MODEL__ &middot; Generated __DATE__ &middot; 100 calls (one per minute)</p>

  <h2>Key Metrics</h2>
  <div class="kpi-grid" id="kpis"></div>

  <div class="alerts-strip" id="alerts"></div>

  <h2>Charts</h2>
  <div class="charts-grid">
    <div class="chart-card"><h3>Latency over time (ms)</h3><svg id="latency-chart"></svg><div class="legend"><span><span class="dot" style="background:var(--blue)"></span>Latency</span><span><span class="dot" style="background:var(--red)"></span>Slow (&gt; p95)</span><span><span class="dot" style="background:var(--gray)"></span>p95 line</span></div></div>
    <div class="chart-card"><h3>Error rate by 10-min bucket</h3><svg id="error-chart"></svg><div class="legend"><span><span class="dot" style="background:#cbd5e1"></span>&le;10%</span><span><span class="dot" style="background:var(--red)"></span>&gt;10% (flagged)</span></div></div>
    <div class="chart-card"><h3>Quality score distribution</h3><svg id="quality-chart"></svg><div class="legend"><span><span class="dot" style="background:var(--red)"></span>1-2 low</span><span><span class="dot" style="background:var(--amber)"></span>3 ok</span><span><span class="dot" style="background:var(--green)"></span>4-5 good</span></div></div>
    <div class="chart-card"><h3>Cumulative cost</h3><svg id="cost-chart"></svg></div>
  </div>

  <h2>Drift Detection</h2>
  <div class="drift-grid" id="drift"></div>

  <h2>Anomalies</h2>
  <div class="filters" id="anomaly-filters"></div>
  <table class="data" id="anomaly-table"></table>

  <h2>Logs</h2>
  <div class="filters" id="log-filters"></div>
  <div class="scroll"><table class="data" id="log-table"></table></div>

  <h2>Recommendations</h2>
  <ol class="recs" id="recs"></ol>

  <div class="takeaway">Monitoring turns logs into decisions: percentile latency surfaces slow tails, per-bucket error rates catch localized spikes, drift checks catch slow degradation, and alert rules make the response automatable. You cannot improve what you do not measure.</div>
</div>
<div class="tooltip" id="tip"></div>
<script>
__DATA_SCRIPT__

const $ = id => document.getElementById(id);
let tipEl = null;
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function showTip(ev, text){ tipEl.style.display='block'; tipEl.style.left=(ev.clientX+12)+'px'; tipEl.style.top=(ev.clientY+8)+'px'; tipEl.textContent=text; }
function hideTip(){ if(tipEl) tipEl.style.display='none'; }

function renderKpis(){
  const m = METRICS;
  const cards = [
    {label:'Latency p95', value: m.latency_p95 + ' ms', cls: m.latency_p95 > 2000 ? 'crit' : (m.latency_p95 > 1500 ? 'warn' : 'ok')},
    {label:'Error rate', value: m.error_rate + '%', cls: m.error_rate > 15 ? 'crit' : (m.error_rate > 10 ? 'warn' : 'ok')},
    {label:'Avg quality', value: m.avg_quality, cls: m.avg_quality < 3 ? 'crit' : (m.avg_quality < 3.4 ? 'warn' : 'ok')},
    {label:'Total cost', value: '$' + m.total_cost, cls:'ok'},
    {label:'Throughput', value: m.throughput_calls_per_min + ' calls/min', cls:'ok'},
    {label:'Latency p50 / p99', value: m.latency_p50 + ' / ' + m.latency_p99 + ' ms', cls:'ok'},
  ];
  $('kpis').innerHTML = cards.map(c => '<div class="kpi '+c.cls+'"><div class="label">'+c.label+'</div><div class="value">'+esc(c.value)+'</div></div>').join('');
}

function renderAlerts(){
  const chips = ALERTS.map(a => '<span class="chip '+a.severity.toLowerCase()+'">'+esc(a.severity)+' &middot; '+esc(a.metric)+' = '+esc(a.value)+'</span>');
  if(!ALERTS.length) chips.push('<span class="chip ok">No active alerts</span>');
  $('alerts').innerHTML = chips.join('');
}

function lineChart(){
  const data = LOGS, p95 = METRICS.latency_p95;
  const svg = $('latency-chart'), W=760, H=220, pl=52, pr=16, pt=14, pb=30;
  const iw=W-pl-pr, ih=H-pt-pb;
  const maxY = Math.max(...data.map(d=>d.latency_ms)) * 1.1;
  const x = i => pl + iw * i / (data.length - 1 || 1);
  const y = v => pt + ih - ih * v / maxY;
  let g='';
  for(let s=0;s<=4;s++){ const v=maxY*s/4, gy=y(v); g+='<line x1="'+pl+'" y1="'+gy+'" x2="'+(W-pr)+'" y2="'+gy+'" stroke="#eef2f7"/><text x="'+(pl-6)+'" y="'+(gy+4)+'" text-anchor="end" font-size="10" fill="#94a3b8">'+Math.round(v)+'</text>'; }
  g+='<text x="'+pl+'" y="'+(H-12)+'" font-size="10" fill="#94a3b8">call 0</text>';
  g+='<text x="'+(W-pr)+'" y="'+(H-12)+'" text-anchor="end" font-size="10" fill="#94a3b8">call '+(data.length-1)+'</text>';
  const py=y(p95);
  g+='<line x1="'+pl+'" y1="'+py+'" x2="'+(W-pr)+'" y2="'+py+'" stroke="#94a3b8" stroke-dasharray="4 3" stroke-width="1.5"/>';
  g+='<text x="'+(W-pr)+'" y="'+(py-4)+'" text-anchor="end" font-size="10" fill="#64748b">p95 '+Math.round(p95)+'</text>';
  let line='', area='';
  data.forEach((p,i)=>{ const cx=x(i), cy=y(p.latency_ms); line+=(i?'L':'M')+cx.toFixed(1)+' '+cy.toFixed(1)+' '; area+=(i?'L':'M')+cx.toFixed(1)+' '+cy.toFixed(1)+' '; });
  area+='L '+x(data.length-1).toFixed(1)+' '+(pt+ih)+' L '+pl+' '+(pt+ih)+' Z';
  g+='<path d="'+area+'" fill="#3b82f6" fill-opacity="0.08"/>';
  g+='<path d="'+line+'" fill="none" stroke="#3b82f6" stroke-width="2"/>';
  data.forEach((p,i)=>{ const cx=x(i), cy=y(p.latency_ms); const slow=p.latency_ms>p95; const col=slow?'#ef4444':'#3b82f6'; g+='<circle class="pt" data-i="'+i+'" cx="'+cx.toFixed(1)+'" cy="'+cy.toFixed(1)+'" r="'+(slow?4:2.5)+'" fill="'+col+'" stroke="#fff" stroke-width="1"/>'; });
  svg.setAttribute('viewBox','0 0 '+W+' '+H);
  svg.innerHTML = g;
  svg.querySelectorAll('.pt').forEach(c=>{ const p=data[+c.dataset.i]; c.addEventListener('mousemove', ev=>showTip(ev, (+c.dataset.i+1)+'. '+p.timestamp+' - '+p.latency_ms+'ms')); c.addEventListener('mouseleave', hideTip); });
}

function errorChart(){
  const svg=$('error-chart'), W=760, H=220, pl=40, pr=16, pt=14, pb=30;
  const iw=W-pl-pr, ih=H-pt-pb;
  const maxE = Math.max(10, ...TRENDS.map(t=>t.error_rate)) * 1.1;
  const y = v => pt + ih - ih * v / maxE;
  const bw = iw / TRENDS.length * 0.7;
  let g='';
  for(let s=0;s<=4;s++){ const v=maxE*s/4, gy=y(v); g+='<line x1="'+pl+'" y1="'+gy+'" x2="'+(W-pr)+'" y2="'+gy+'" stroke="#eef2f7"/><text x="'+(pl-6)+'" y="'+(gy+4)+'" text-anchor="end" font-size="10" fill="#94a3b8">'+Math.round(v)+'</text>'; }
  const th=y(10);
  g+='<line x1="'+pl+'" y1="'+th+'" x2="'+(W-pr)+'" y2="'+th+'" stroke="#94a3b8" stroke-dasharray="4 3"/><text x="'+(W-pr)+'" y="'+(th-4)+'" text-anchor="end" font-size="10" fill="#64748b">10% threshold</text>';
  TRENDS.forEach((t,i)=>{ const cx=pl+iw*(i+0.5)/TRENDS.length; const h=ih*t.error_rate/maxE; const col=t.error_rate>10?'#ef4444':'#cbd5e1'; g+='<rect class="pb" data-b="'+i+'" x="'+(cx-bw/2)+'" y="'+(pt+ih-h)+'" width="'+bw+'" height="'+h+'" rx="2" fill="'+col+'"/>'; g+='<text x="'+cx+'" y="'+(pt+ih+14)+'" text-anchor="middle" font-size="10" fill="#64748b">'+t.minutes+'</text>'; });
  svg.setAttribute('viewBox','0 0 '+W+' '+H);
  svg.innerHTML = g;
  svg.querySelectorAll('.pb').forEach(r=>{ const t=TRENDS[+r.dataset.b]; r.addEventListener('mousemove', ev=>showTip(ev, 'minutes '+t.minutes+' - '+t.error_rate+'% errors, avg quality '+t.avg_quality)); r.addEventListener('mouseleave', hideTip); });
}

function qualityChart(){
  const svg=$('quality-chart'), W=760, H=220, pl=36, pr=44, pt=14, pb=30;
  const iw=W-pl-pr, ih=H-pt-pb;
  const dist = METRICS.quality_dist;
  const maxC = Math.max(...Object.values(dist), 1);
  let g='';
  for(let s=1;s<=5;s++){ const c=dist[s]||0; const col=s<=2?'#ef4444':(s===3?'#f59e0b':'#22c55e'); const rowY=pt+(s-1)*((ih-6)/5); g+='<text x="'+(pl-6)+'" y="'+(rowY+15)+'" text-anchor="end" font-size="11" fill="#334155">'+s+'</text>'; g+='<rect x="'+pl+'" y="'+(rowY+2)+'" width="'+(iw*c/maxC)+'" height="18" rx="3" fill="'+col+'"/>'; g+='<text x="'+(pl+iw*c/maxC+6)+'" y="'+(rowY+15)+'" font-size="11" fill="#334155">'+c+'</text>'; }
  svg.setAttribute('viewBox','0 0 '+W+' '+H);
  svg.innerHTML = g;
}

function costChart(){
  const svg=$('cost-chart'), W=760, H=220, pl=56, pr=16, pt=14, pb=30;
  const iw=W-pl-pr, ih=H-pt-pb;
  let cum=0; const series=LOGS.map(l=>{ cum+=l.cost_usd; return {v:cum}; });
  const maxV=cum*1.05;
  const x=i=>pl+iw*i/(series.length-1||1); const y=v=>pt+ih-ih*v/maxV;
  let g='';
  for(let s=0;s<=4;s++){ const v=maxV*s/4, gy=y(v); g+='<line x1="'+pl+'" y1="'+gy+'" x2="'+(W-pr)+'" y2="'+gy+'" stroke="#eef2f7"/><text x="'+(pl-6)+'" y="'+(gy+4)+'" text-anchor="end" font-size="10" fill="#94a3b8">$'+v.toFixed(2)+'</text>'; }
  let line='', area='';
  series.forEach((p,i)=>{ const cx=x(i), cy=y(p.v); line+=(i?'L':'M')+cx.toFixed(1)+' '+cy.toFixed(1)+' '; area+=(i?'L':'M')+cx.toFixed(1)+' '+cy.toFixed(1)+' '; });
  area+='L '+x(series.length-1).toFixed(1)+' '+(pt+ih)+' L '+pl+' '+(pt+ih)+' Z';
  g+='<path d="'+area+'" fill="#8b5cf6" fill-opacity="0.1"/>';
  g+='<path d="'+line+'" fill="none" stroke="#8b5cf6" stroke-width="2"/>';
  g+='<text x="'+(W-pr)+'" y="'+(H-12)+'" text-anchor="end" font-size="10" fill="#94a3b8">$'+cum.toFixed(2)+' total</text>';
  svg.setAttribute('viewBox','0 0 '+W+' '+H);
  svg.innerHTML = g;
}

function renderDrift(){
  const d=DRIFT;
  const q=d.quality_status==='DRIFT DETECTED'?'drift':'stable';
  const l=d.latency_status==='DRIFT DETECTED'?'drift':'stable';
  $('drift').innerHTML =
    '<div class="drift-card"><span class="badge '+q+'">'+esc(d.quality_status)+'</span><p>Avg quality: first half <b>'+d.first_quality+'</b> &rarr; second half <b>'+d.second_quality+'</b> (delta '+d.quality_delta+')</p></div>'+
    '<div class="drift-card"><span class="badge '+l+'">'+esc(d.latency_status)+'</span><p>Avg latency: first half <b>'+d.first_latency+' ms</b> &rarr; second half <b>'+d.second_latency+' ms</b> (delta '+d.latency_delta_pct+'%)</p></div>';
}

let aFilter='all';
const A_TYPES=['all','latency','quality','window'];
function renderAnomalyFilters(){
  $('anomaly-filters').innerHTML=A_TYPES.map(t=>'<button data-t="'+t+'" class="'+(aFilter===t?'active':'')+'">'+t[0].toUpperCase()+t.slice(1)+'</button>').join('');
  $('anomaly-filters').querySelectorAll('button').forEach(b=> b.addEventListener('click', ()=>setAFilter(b.dataset.t)));
}
function setAFilter(t){ aFilter=t; renderAnomalyFilters(); renderAnomalies(); }
function renderAnomalies(){
  let rows=ANOMALIES;
  if(aFilter!=='all') rows=rows.filter(a=>a.type===aFilter);
  let h='<thead><tr><th>Time</th><th>Type</th><th>Detail</th></tr></thead><tbody>';
  rows.forEach(a=>{ h+='<tr><td>'+esc(a.timestamp)+'</td><td><span class="badge-tag tag-'+a.type+'">'+esc(a.type)+'</span></td><td>'+esc(a.detail)+'</td></tr>'; });
  h+='</tbody>';
  $('anomaly-table').innerHTML=h;
}

let lFilter='all', lSort={key:'idx', dir:1};
const L_FILTERS=['all','errors','slow','low'];
const L_LABELS={all:'All',errors:'Errors only',slow:'Slow (latency > p95)',low:'Low quality (<2)'};
function renderLogFilters(){
  $('log-filters').innerHTML=L_FILTERS.map(f=>'<button data-f="'+f+'" class="'+(lFilter===f?'active':'')+'">'+L_LABELS[f]+'</button>').join('');
  $('log-filters').querySelectorAll('button').forEach(b=> b.addEventListener('click', ()=>setLFilter(b.dataset.f)));
}
function setLFilter(f){ lFilter=f; renderLogFilters(); renderLogs(); }
function setSort(key){ if(lSort.key===key){ lSort.dir*=-1; } else { lSort.key=key; lSort.dir=1; } renderLogs(); }
function arrow(key){ return lSort.key===key?(lSort.dir>0?'&darr;':'&uarr;'):''; }
function renderLogs(){
  let rows=LOGS.map((l,i)=>({idx:i+1, ...l}));
  if(lFilter==='errors') rows=rows.filter(r=>r.error);
  if(lFilter==='slow') rows=rows.filter(r=>r.latency_ms>METRICS.latency_p95);
  if(lFilter==='low') rows=rows.filter(r=>r.quality_score<2);
  const key=lSort.key;
  rows.sort((a,b)=>{ const va=a[key], vb=b[key]; if(typeof va==='string'&&typeof vb==='string') return va.localeCompare(vb)*lSort.dir; return (va-vb)*lSort.dir; });
  const head=['idx','timestamp','latency_ms','tokens_input','tokens_output','cost_usd','quality_score','error'];
  const labels={idx:'#',timestamp:'Timestamp',latency_ms:'Latency ms',tokens_input:'In tokens',tokens_output:'Out tokens',cost_usd:'Cost $',quality_score:'Quality',error:'Error'};
  let h='<thead><tr>'+head.map(k=>'<th data-key="'+k+'">'+labels[k]+' '+arrow(k)+'</th>').join('')+'</tr></thead><tbody>';
  rows.forEach(r=>{
    const slow=r.latency_ms>METRICS.latency_p95;
    const low=r.quality_score<2;
    h+='<tr><td>'+r.idx+'</td><td>'+esc(r.timestamp)+'</td><td class="'+(slow?'err':'')+'">'+r.latency_ms+'</td><td>'+r.tokens_input+'</td><td>'+r.tokens_output+'</td><td>'+r.cost_usd.toFixed(5)+'</td><td class="'+(low?'low':'')+'">'+r.quality_score+'</td><td>'+(r.error?'<span class="err">YES</span>':'no')+'</td></tr>';
  });
  h+='</tbody>';
  $('log-table').innerHTML=h;
  $('log-table').querySelectorAll('th[data-key]').forEach(th=> th.addEventListener('click', ()=>setSort(th.dataset.key)));
}

function renderRecs(){ $('recs').innerHTML=RECS.map(r=>'<li>'+esc(r)+'</li>').join(''); }

function init(){
  tipEl=$('tip');
  renderKpis(); renderAlerts(); renderDrift(); renderAnomalyFilters(); renderAnomalies(); renderLogFilters(); renderLogs(); renderRecs();
  lineChart(); errorChart(); qualityChart(); costChart();
}
window.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
"""


def build_html(
    logs: list[Log],
    metrics: Metrics,
    anomalies: list[dict[str, str | float | int]],
    drift: dict[str, str | float],
    alerts: list[dict[str, str | float]],
    trends: list[dict[str, float | int | str]],
    recommendations: list[str],
    model: str,
) -> str:
    """Assemble a self-contained HTML dashboard with embedded data."""
    data_script = "".join(
        [
            "const LOGS = " + json.dumps(logs) + ";\n",
            "const METRICS = " + json.dumps(metrics) + ";\n",
            "const ANOMALIES = " + json.dumps(anomalies) + ";\n",
            "const DRIFT = " + json.dumps(drift) + ";\n",
            "const ALERTS = " + json.dumps(alerts) + ";\n",
            "const TRENDS = " + json.dumps(trends) + ";\n",
            "const RECS = " + json.dumps(recommendations) + ";\n",
        ]
    )
    page = HTML_TEMPLATE
    page = page.replace("__MODEL__", html.escape(model))
    page = page.replace(
        "__DATE__", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    page = page.replace("__DATA_SCRIPT__", data_script)
    return page


# ---------- Main ----------


def main() -> None:
    """Generate logs, analyze them, and export the dashboard."""
    parser = argparse.ArgumentParser(description="Part 9 LLMOps dashboard lab")
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="skip the opencode recommendation engine and use fallbacks",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="also write an interactive self-contained HTML dashboard",
    )
    args = parser.parse_args()

    print(f"Model: {MODEL}")
    logs = generate_logs()
    inject_anomalies(logs)
    print(f"Generated {len(logs)} synthetic logs")

    metrics = compute_metrics(logs)
    anomalies = detect_anomalies(logs, metrics)
    drift = drift_detection(logs)
    alerts = alert_rules(metrics)
    trends = trend_analysis(logs)

    banner("LLMOPS MONITORING DASHBOARD")
    print_metrics(metrics)
    print_anomalies(anomalies)
    print_drift(drift)
    print_alerts(alerts)
    print_trends(trends)

    if args.skip_llm:
        recommendations = FALLBACK_RECOMMENDATIONS
        print("\nRecommendation engine: skipped (using fallbacks)")
    else:
        print("\nAsking LLM for optimization recommendations...")
        summary = build_dashboard_summary(metrics, anomalies, drift, trends)
        recommendations = get_recommendations(summary)
    print_recommendations(recommendations)

    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, "dashboard_logs.csv")
    results_path = os.path.join(base_dir, "part9_results.md")
    save_csv(logs, csv_path)
    save_results(
        metrics, anomalies, drift, alerts, trends, recommendations, results_path
    )
    print(f"\nCSV exported to: {csv_path}")
    print(f"Results saved to: {results_path}")

    if args.html:
        html_path = os.path.join(base_dir, "llm_ops_dashboard.html")
        page = build_html(
            logs,
            metrics,
            anomalies,
            drift,
            alerts,
            trends,
            recommendations,
            MODEL,
        )
        with open(html_path, "w", encoding="utf-8") as file:
            file.write(page)
        print(f"HTML dashboard written to: {html_path}")

    print("DONE — Part 9 complete. Next: Part 10 (Challenges with LLMs)")


if __name__ == "__main__":
    main()
