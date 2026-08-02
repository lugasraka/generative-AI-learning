# Part 4 — Types of Agentic RAG: Results

- **Generated:** 2026-08-02 23:37:11
- **Total tasks:** 10

## Classification Results

| # | Task | Architecture | Complexity | Agents | Why |
|---|------|-------------|------------|--------|-----|
| 1 | Find the latest stock price of Apple | Single-Agent | low | 1 | Matched keywords: find |
| 2 | Compare AI regulation policies across US, EU, and ... | Multi-Agent | medium | 2-3 | Matched keywords: compare, across |
| 3 | Audit our vendor contracts for compliance risks | Hierarchical | medium | 3-5 | Matched keywords: audit, compliance |
| 4 | What is our company's travel policy? | Single-Agent | low | 1 | Matched keywords: what is |
| 5 | Research all competitors' pricing strategies | Single-Agent | medium | 1 | Matched keywords: search |
| 6 | Prioritize security vulnerabilities by criticality | Hierarchical | medium | 3-5 | Matched keywords: prioritize, critical |
| 7 | Look up employee handbook section on remote work | Single-Agent | low | 1 | Matched keywords: look up |
| 8 | Analyze customer sentiment across all review platf... | Multi-Agent | medium | 2-3 | Matched keywords: analyze, across |
| 9 | Enterprise-wide compliance report for Q2 | Hierarchical | medium | 3-5 | Matched keywords: enterprise, compliance |
| 10 | Get the current weather in New York | Single-Agent | low | 1 | Matched keywords: get |

## Statistics

### By Architecture

| Architecture | Count | Percentage |
|-------------|-------|------------|
| Single-Agent | 5 | 50% |
| Multi-Agent | 2 | 20% |
| Hierarchical | 3 | 30% |

### By Complexity

| Complexity | Count |
|-----------|-------|
| Low | 4 |
| Medium | 6 |
| High | 0 |

## Hybrid Recommendations

- **Research all competitors' pricing strategies**
  - Primary: Single-Agent, Secondary: Multi-Agent
  - Strong signals for both Single-Agent (1 matches) and Multi-Agent (1 matches). Could use Single-Agent for initial query, Multi-Agent for follow-up analysis.
