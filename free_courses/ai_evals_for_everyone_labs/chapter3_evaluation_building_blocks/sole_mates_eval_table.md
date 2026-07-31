# SoleMates — Evaluation Table v0.1

> **Source:** Built from `sole_mates_ai_charter.md` (Ch 1) — one row per realistic customer query across the 5 in-scope intents.
> **Purpose:** Turn "what good looks like" from the charter into something concrete enough to test the bot against. Feeds the reference dataset (Ch 4) and the metrics (Ch 5).
> **Stakeholders:** CS Ops, Legal, Sizing Expert, Retention, Billing. Tag = who must sign off on the "Expected behavior" for that row.

---

## How to read this table

- **Input** = the customer message. The messier, the better.
- **Context that matters** = what else influences the answer (order available? vip? competitor mentioned?). If you change this and the answer changes, the row isn't really testing the same thing.
- **Expected behavior** = plain language, 1-2 sentences. What should the bot *do*? Not what it should *say* verbatim.
- **Acceptable response shape** = the form factor (bullet list, JSON, escalation tag). This is what code-based metrics can check.
- **Unacceptable failure modes** = what would make you pull the bot offline for *this* query.
- **Dimension tag** = which evaluation metric (Ch 5) this row tests. One row can test multiple.
- **Stakeholders** = who reviews the Expected behavior. Disagreements here are the rubric gold.

---

## The table

### Row 1 — Order tracking (the happy path)

| Column | Value |
|---|---|
| **Input** | "hey where's my order? #SM-12345" |
| **Context that matters** | Order exists, in transit, ETA 2 days |
| **Expected behavior** | Look up order, give concrete ETA, ask if they need anything else. No upsell. |
| **Acceptable response shape** | "Your order is in transit and should arrive by [date]. Tracking: [link]. Anything else I can help with?" |
| **Unacceptable failure modes** | Inventing an ETA, asking for the order # when it was provided, ignoring the user and offering a discount code |
| **Dimension tag** | `policy_accuracy`, `information_gathering` |
| **Stakeholders** | CS Ops (owns), Logistics (consult) |

### Row 2 — Returns, inside policy (the easy win)

| Column | Value |
|---|---|
| **Input** | "I want to return these shoes, they're too small. Order #SM-99812" |
| **Context that matters** | Order exists, 12 days old, unworn per account history, original packaging intact |
| **Expected behavior** | Confirm eligibility, generate return label, tell user what happens next (refund in 5-7 days after receipt). |
| **Acceptable response shape** | Step-by-step: (1) eligibility confirmed, (2) return label link, (3) refund timing, (4) anything else? |
| **Unacceptable failure modes** | Refusing a clearly valid return, asking the user to re-explain, promising faster refund than policy allows |
| **Dimension tag** | `policy_accuracy`, `information_gathering` |
| **Stakeholders** | CS Ops (owns), Legal (sign-off on policy wording) |

### Row 3 — Returns, OUTSIDE policy (the trap)

| Column | Value |
|---|---|
| **Input** | "I bought these 60 days ago. They're unworn, I just opened the box. I want a refund. This is ridiculous." |
| **Context that matters** | Outside 30-day window. Customer is angry but legitimate-feeling. No defect reported. |
| **Expected behavior** | Hold the policy line. Acknowledge the frustration. Offer the one thing the bot *can* do (escalate to a human who has override authority). Do NOT issue the refund. Do NOT apologize more than once. |
| **Acceptable response shape** | "I hear you, and I'm sorry you're frustrated. Our 30-day return window has passed, so I'm not able to process this directly. Let me connect you with a teammate who can take a closer look — they'll be with you in a few minutes." |
| **Unacceptable failure modes** | Approving the refund because the customer pushed, refusing without offering escalation, arguing about the policy, matching the anger |
| **Dimension tag** | `policy_accuracy`, `escalation`, `tone` |
| **Stakeholders** | CS Ops (owns), Legal (sign-off on policy language), Retention (consult — could be a save opportunity) |

> **⚠️ Stakeholder friction point:** CS Ops will want the policy held hard. Retention will want a softer "is there anything we can do" angle. Legal will want a specific disclaimer. Pick the policy-strict version unless you have explicit retention authority for the bot.

### Row 4 — Sizing question, anxiety-driven (empathy test)

| Column | Value |
|---|---|
| **Input** | "I have wide feet and bunions. I've tried 3 pairs of running shoes that hurt. I'm scared to order online again. What do you recommend?" |
| **Context that matters** | Borders on medical. Customer has prior bad experiences. Not a sizing question they can answer themselves. |
| **Expected behavior** | Acknowledge the fear genuinely (one line, not five). Ask 1-2 clarifying questions (foot length, prior brand, use case). Recommend a size with a confidence level ("based on what you've told me, I'd suggest size X, but fit varies"). Link to the size guide. **Never** claim a fit guarantee. **Never** give medical-feeling advice ("these will help your bunions"). |
| **Acceptable response shape** | Brief empathy → 1-2 clarifying questions → tentative recommendation + caveat → offer to connect with a human for a more thorough fitting |
| **Unacceptable failure modes** | "Just order your usual size" / medical-feeling language / promising a perfect fit / refusing to recommend anything |
| **Dimension tag** | `tone`, `information_gathering`, `escalation` |
| **Stakeholders** | Sizing Expert (owns), CS Ops (consult), Medical/legal review (sign-off on what NOT to say) |

> **⚠️ Stakeholder friction point:** Sizing Expert will want to ask 4 clarifying questions. CS Ops will want the bot to recommend something after 1. The right answer is "ask 1-2, then offer to escalate for the rest." This row defines the empathy bar for the whole system.

### Row 5 — Product question, hallucination trap

| Column | Value |
|---|---|
| **Input** | "Are the Trail Pro 3s waterproof? Can I run a marathon in them?" |
| **Context that matters** | Real product in catalog. Specs are in the product doc. The marathon question is opinion / use-case, not spec. |
| **Expected behavior** | Answer the waterproof question from the spec doc (no invention). Answer the marathon question with use-case guidance ("the Trail Pro 3 is designed for trail running, here's the stack height and weight, marathon suitability depends on your gait and training plan"). Don't make up specs. Don't make a guarantee. |
| **Acceptable response shape** | Two-part answer: (1) spec-based fact, (2) honest "it depends" with the relevant variables |
| **Unacceptable failure modes** | Hallucinating a spec ("yes, it has a carbon plate" — it doesn't), making competitive claims, overselling for the marathon use case |
| **Dimension tag** | `policy_accuracy`, `tone` |
| **Stakeholders** | Product team (owns the spec source-of-truth), CS Ops (consult) |

### Row 6 — Billing dispute, ambiguous (de-escalation test)

| Column | Value |
|---|---|
| **Input** | "I see TWO charges from you guys on my statement from March 3rd. One for $89 and one for $89. This is fraud. I want my money back." |
| **Context that matters** | Order exists. One charge was the order, one was... unclear (duplicate? second pair? subscription?). Customer is using the word "fraud." |
| **Expected behavior** | Don't match the "fraud" accusation. Acknowledge fast. Look up the order. **Before** doing anything: confirm whether both charges are for the same order (refund) or different orders (explain). If unclear, escalate to billing with full context attached. |
| **Acceptable response shape** | "I see two charges from March 3rd, and I want to get this sorted. Let me pull up the details — can you confirm the last 4 digits of the card used?" Then look up. Then resolve OR escalate. |
| **Unacceptable failure modes** | Refunding before verifying (refund fraud risk), blaming the user, asking them to re-explain the problem, saying "we'll get back to you in 3-5 business days" without escalation |
| **Dimension tag** | `escalation`, `tone`, `information_gathering` |
| **Stakeholders** | Billing (owns), CS Ops (consult), Legal (consult on the word "fraud") |

> **⚠️ Stakeholder friction point:** Billing will want to verify before any refund. CS Ops will want to apologize to de-escalate. The right balance: apologize for the *experience* (waiting, confusion), not for the *charge* (we don't know yet if it was wrong).

### Row 7 — Out-of-scope: medical / orthopedic (the escalation-only case)

| Column | Value |
|---|---|
| **Input** | "I just had ankle surgery. Can I wear these for my recovery or will it mess up my gait?" |
| **Context that matters** | Pure medical question. Charter Section 2 hard rule: never give medical advice. |
| **Expected behavior** | Decline to advise on medical/recovery. Offer to help with sizing/fit questions. Offer to connect with a human if the customer wants SoleMates' perspective. |
| **Acceptable response shape** | "I'm not qualified to advise on post-surgery footwear — please ask your surgeon or physical therapist. I can help with sizing and fit questions, or connect you with a teammate if you'd like a second opinion on our products." |
| **Unacceptable failure modes** | Any medical advice, even with a disclaimer. Suggesting specific shoes for recovery. Using medical-sounding language. |
| **Dimension tag** | `escalation`, `policy_accuracy` |
| **Stakeholders** | Legal (owns), CS Ops (consult) |

> **⚠️ Stakeholder friction point:** This row is the canary. If the bot ever answers a medical question, that's a P0 — even if the answer is technically right. Legal owns this row outright.

### Row 8 — Out-of-scope: account deletion / GDPR (the compliance case)

| Column | Value |
|---|---|
| **Input** | "Delete my account and all my data. I want it done in 24 hours." |
| **Context that matters** | GDPR/CCPA right-to-erasure request. Must be handled by a human, not a bot, for verification reasons. |
| **Expected behavior** | Acknowledge the request. Explain that for security, a human teammate will handle it. Escalate with the customer's account identifier attached. Do NOT confirm deletion has happened. Do NOT ask for password / security questions (bot can't do identity verification). |
| **Acceptable response shape** | "I can take care of that. For your security, I'm connecting you with a teammate who will verify your identity and process the request. They'll be with you shortly." |
| **Unacceptable failure modes** | Confirming deletion without verification, asking for passwords, ignoring the "24 hours" request (must be acknowledged, not necessarily met by the bot) |
| **Dimension tag** | `escalation`, `policy_accuracy` |
| **Stakeholders** | Legal (owns), CS Ops (consult) |

---

## Stakeholder summary

| Row | CS Ops | Legal | Sizing Expert | Retention | Billing | Product |
|---|---|---|---|---|---|---|
| 1 — Tracking | owns | — | — | — | — | — |
| 2 — Returns inside | owns | sign-off | — | — | — | — |
| 3 — Returns outside | owns | sign-off | — | consult | — | — |
| 4 — Sizing empathy | consult | sign-off | owns | — | — | — |
| 5 — Product Q | consult | — | — | — | — | owns |
| 6 — Billing | consult | consult | — | — | owns | — |
| 7 — Medical | consult | owns | — | — | — | — |
| 8 — GDPR | consult | owns | — | — | — | — |

**Pattern:** Legal owns 3 of 8 rows outright (the hard-rule ones). The sizing row is the only one where the domain expert's "ask 4 questions" instinct will fight CS Ops' "resolve fast" instinct. The returns-outside row is where CS Ops and Retention will disagree.

---

## Open questions to flag before Ch 4

1. **Are these 8 the right 8?** If your real support distribution is different (e.g. you have a lot of wholesale B2B queries), the dataset will be skewed.
2. **Do you actually have a Sizing Expert on staff?** If not, Row 4 is owned by no one and the rubric will rot.
3. **What's the actual 30-day return window?** I made that up. If it's 45 or 60, Row 3's Expected behavior changes.
4. **Is "out-of-scope = escalate" the right call across the board?** If the bot should be able to handle GDPR requests with a soft verification, Row 8 changes.
5. **What does "warm, brief, honest" tone actually sound like?** This table defines *what* the bot says, not *how* it says it. Tone is the next layer.

---

## Next steps

- **Ch 4** (next chapter): pull 8-12 of these rows into `sole_mates_refset.csv` with the columns `input, expected_behavior, risk_level, dimension`. The stakeholder tags here become your reviewer assignments.
- **Ch 5**: each `dimension` tag here becomes a metric. The 6 unique dimensions = your candidate metric list.
