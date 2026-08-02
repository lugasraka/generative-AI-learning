# Part 2 — Attack Vectors in Agentic Systems

> Source: [../securing_agentic_ai_systems/part2_attack_vectors.md](../../securing_agentic_ai_systems/part2_attack_vectors.md)

## Concept in 10 lines

- **Five attack vectors:** prompt injection, memory poisoning, supply chain, tool misuse, goal hijacking.
- **Prompt injection** = manipulating inputs to alter behavior. 94.4% of agents vulnerable.
- **Memory poisoning** = injecting malicious entries that persist across sessions. 95%+ success rate.
- **Supply chain** = compromised frameworks, packages, models (NX breach, LangGrinch CVE).
- **Tool misuse** = redirecting legitimate tool access for unauthorized purposes.
- **Goal hijacking** = gradually shifting agent objectives toward attacker goals.
- Attacks combine vectors: injection for access, memory for persistence, tools for exfiltration.
- Multi-agent systems face 100% vulnerability to inter-agent trust exploits.

## Vibe-coding challenge

**Attack vector catalog.** Build a structured catalog of attack vectors for a sample agent system:

1. Define 2 agent system profiles (e.g., email assistant, database analyst).
2. For each system, map all 5 attack vectors with:
   - **Attack description:** How would an attacker exploit this vector?
   - **Severity:** Critical / High / Medium / Low
   - **Likelihood:** How easy is this to execute?
   - **Impact:** What damage could result?
   - **Entry point:** Where does the attack enter the system?
3. Output a JSON catalog for each system with all attack vectors.
4. Print a summary table: system, vector, severity, likelihood, impact.
5. Identify which vector is most dangerous for each system and explain why.

> Bonus: add a "combined attack" scenario where an attacker chains 2+ vectors together.

### How to start

Tell me one of:
- *"Scaffold the system profiles and catalog structure"*
- *"Use specific real-world attack examples"*
- *"Show me the JSON schema first"*
- *"I want to catalog my own agent system"*
