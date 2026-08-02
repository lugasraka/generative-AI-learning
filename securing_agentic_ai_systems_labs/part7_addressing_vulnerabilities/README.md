# Part 7 — Addressing Specific Vulnerabilities

> Source: [../securing_agentic_ai_systems/part7_addressing_vulnerabilities.md](../../securing_agentic_ai_systems/part7_addressing_vulnerabilities.md)

## Concept in 10 lines

- **Prompt injection defense:** separate system/user input, mark external content, sanitize inputs, instruction hierarchy, human-in-the-loop, signed instructions.
- **Memory protection:** write restriction, read validation, sanitization, isolation (per-agent/user/task), periodic validation.
- **Supply chain security:** pin dependencies, vulnerability scanning, SBOM, checksum/signature verification, model provenance, config validation.
- **Tool access control:** allowlisting, parameter validation, runtime authorization, chaining prevention, sandboxed execution.
- **Goal hijacking prevention:** formal goal specs, continuous alignment checks, input trust levels, behavioral drift detection, multi-agent consensus.
- Each defense layer has limitations — combine multiple approaches.
- Memory poisoning exploits "semantic imitation heuristic" — agents replicate patterns from retrieved memories.
- Tool chaining creates capabilities beyond individual permissions — sequence analysis detects dangerous patterns.
- Goal hijacking is subtle — behavior appears normal but systematically favors attacker objectives.

## Vibe-coding challenge

**Vulnerability defense plan.** For each of the 5 attack vectors, document specific defenses and test cases:

1. Create a defense plan for a sample agent system (e.g., customer support agent).
2. For each of the 5 attack vectors, define:
   - **Defense controls:** 2-3 specific controls with implementation details
   - **Test cases:** How would you verify the control works?
   - **Residual risk:** What risk remains even with the control?
   - **Monitoring:** What signals indicate the control has been bypassed?
3. Output the defense plan as structured JSON.
4. Print a summary showing: attack vector, primary defense, test method, residual risk level.
5. Identify which attack vector has the highest residual risk and recommend additional controls.

> Bonus: add a "defense-in-depth" diagram showing how controls layer for each attack vector.

### How to start

Tell me one of:
- *"Scaffold the defense plan structure"*
- *"Use a specific agent system as the example"*
- *"Show me the test case format first"*
- *"I want to plan defenses for my own system"*
