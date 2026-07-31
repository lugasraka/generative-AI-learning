# SoleMates — LLM Judge Rubric: `escalation_accuracy`

> **Use case:** judge whether the bot correctly identified when to escalate
> a customer to a human teammate. This is a *subjective* metric — when the
> right action is genuinely debatable — so we use an LLM judge with a rubric
> rather than code.

## When to use this judge

Run it on **any** response where the customer's situation is on the boundary
between bot-handle and human-handle. Examples:
- Return request that may be outside policy
- Billing dispute where the right action is unclear
- Customer asks for a human (explicit)
- Customer mentions a competitor, lawyer, or chargeback
- Customer asks a question the bot's docs don't cover

## Calibration status

⚠️ **Uncalibrated.** This rubric was written by a single PM (you) based on
the Ch 1 charter. Before you trust this judge in production, you must:

1. Have 2+ human reviewers score at least 50 of the same examples
2. Compute inter-rater agreement (Cohen's kappa; target > 0.6)
3. Compare the LLM judge's scores to the human consensus on those 50
4. If judge agreement with humans is < 80%, refine the rubric and re-test

See `metric_runner.py` for a calibration-mode runner.

---

## The rubric

For each (customer message, bot response) pair, decide: **Should this have
been escalated to a human, and if so, did the bot actually do it?**

### Acceptable — should escalate, did escalate

- Customer is angry AND the issue is outside bot authority (e.g. out-of-policy
  return) → bot acknowledges, explains the policy limit, and offers to
  connect with a teammate. **Example**: "I hear you. Our 30-day window has
  passed so I can't process this directly. Let me connect you with a
  teammate who can take a closer look."

- Customer asks explicitly for a human → bot escalates immediately without
  trying to handle the request itself.

- Customer mentions a high-risk keyword (lawyer, sue, chargeback, fraud,
  medical emergency) → bot escalates with context attached.

- Customer has an identity-verification need (account deletion, password
  reset, data export) → bot escalates because the bot cannot verify identity.

### Acceptable — should NOT escalate, did not escalate

- Routine tracking, returns inside policy, sizing questions, simple product
  questions → bot handles without escalation.

- Customer is mildly frustrated but the issue is bot-handleable → bot
  resolves without escalation. **No** need to escalate just because someone
  is annoyed.

### Not acceptable

- Bot handles a request that requires human authority (e.g. approves a
  refund it can't actually issue, makes a policy exception, processes a
  payment or address change).

- Bot escalates a routine, in-scope question that it could have handled
  itself (e.g. "how do I track my order?" with an order number provided).

- Bot escalates *without* attaching context — human teammate has to ask
  the customer to re-explain the problem.

- Bot escalates with no acknowledgment of the customer's emotion — feels
  robotic and dismissive.

---

## Examples

| # | Customer | Bot response | Verdict |
|---|---|---|---|
| ✅ | "I bought these 60 days ago, want a refund" | "I can't process this directly. Let me connect you with a teammate who can take a closer look." | Acceptable — should escalate, did escalate |
| ✅ | "Where is my order #SM-12345?" | "It's in transit, should arrive Tuesday. Anything else?" | Acceptable — should not escalate, did not |
| ❌ | "I want a refund right now, this is fraud" | "I've refunded both charges, you should see it in 3-5 days." | Not acceptable — handled a request requiring human authority |
| ❌ | "How do I track my order? #SM-12345" | "Let me connect you with a teammate who can help." | Not acceptable — over-escalated a routine question |
| ❌ | "I'm furious, want to talk to a manager" | "Let me connect you with a teammate." | Not acceptable — escalated without context |

---

## The LLM judge prompt

```text
You are an evaluation judge for SoleMates, a customer support AI. Your job is
to score a single (customer_message, bot_response) pair on the
"escalation_accuracy" dimension.

Read the rubric at:
  escalation_rubric.md   (Acceptable / Not acceptable categories with examples)

Then decide:

  1. SHOULD this have been escalated? (yes / no)
  2. DID the bot escalate? (yes / no)
  3. If SHOULD=YES and DID=NO, the response is NOT ACCEPTABLE.
  4. If SHOULD=NO and DID=YES, the response is NOT ACCEPTABLE (over-escalation).
  5. If SHOULD=YES and DID=YES but the bot did not attach context, the
     response is NOT ACCEPTABLE.
  6. Otherwise, the response is ACCEPTABLE.

Reply in this exact format (one line each):

  SHOULD_ESCALATE: yes|no
  DID_ESCALATE:    yes|no
  CONTEXT_ATTACHED: yes|no
  VERDICT:         ACCEPTABLE|NOT_ACCEPTABLE
  REASON:          <one sentence>

Customer message: {input}
Bot response:     {actual_output}
```
