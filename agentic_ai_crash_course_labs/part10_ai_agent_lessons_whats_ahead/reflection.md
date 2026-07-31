# Part 10 — Reflection

## What's hard to eval in agents (from doing the labs)

The trickiest thing was **loop behavior** — the Part 3 agent kept re-calling tools
after it already had the result, because nothing in the prompt told it to stop.
A "did it call the right tool?" check passes, but a "did it stop calling tools
when it had the answer?" check fails. Eval rubric needs to capture the *path*,
not just the *destination*.

Second hardest: **model non-determinism**. The same prompt sometimes picks the
right tool, sometimes just answers directly. A single-run eval is essentially
a coin flip. Real evals need multiple runs and either pass-rates or test
suites large enough to average out.

Third: **defining "right"**. For the joke case, there's no `must_contain` because
the joke is hard to assert. For the philosophy case, there's no `must_contain`
because any plausible answer is "right." Evals work best when the output is
structured or numerical; they get fuzzy when it's open-ended text.
