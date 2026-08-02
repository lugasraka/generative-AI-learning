# Part 6 — Implementation Guide

> Source: [../securing_agentic_ai_systems/part6_implementation_guide.md](../../securing_agentic_ai_systems/part6_implementation_guide.md)

## Concept in 10 lines

- **Identity:** unique agent IDs, short-lived certificates, HSMs, workload identity federation.
- **Authorization:** RBAC (roles), ABAC (attributes), OBO flow (delegated permissions).
- **Containment:** purpose binding (signed configs), kill-switch (immediate termination), resource caps (quotas), circuit breakers (auto-suspend).
- **Logging:** structured format, log everything (inputs, reasoning, tool calls, permissions, safety events).
- **Tamper-resistance:** cryptographic signing, immutable storage, separate security context, real-time replication.
- **Testing:** red team exercises, automated vulnerability scanning in CI/CD, adversarial prompt libraries.
- **Continuous validation:** quarterly minimum for production agents.
- Enforcement must be external to the agent — don't rely on self-policing.
- Kill-switch system must be separate from agent infrastructure.

## Vibe-coding challenge

**Pre-deployment security checklist tracker.** Build a tool that tracks security implementation status:

1. Create a checklist of 20+ security controls from the implementation guide (identity, permissions, containment, logging, testing).
2. For each control, define:
   - Control name and description
   - Category (identity / permissions / containment / logging / testing)
   - Priority (must-have / should-have / nice-to-have)
   - Status (not started / in progress / done / verified)
   - Owner (role or team)
   - Due date
3. Implement functions to: add controls, update status, calculate completion percentage per category, identify overdue items.
4. Output a dashboard showing: overall progress, per-category breakdown, overdue items, next actions.
5. Export the checklist as a formatted report.

> Bonus: add a "readiness score" — is this system ready for production deployment?

### How to start

Tell me one of:
- *"Scaffold the 20 controls and tracker structure"*
- *"I want to track my own system's controls"*
- *"Show me the control categories first"*
- *"Make it a CLI tool I can interact with"*
