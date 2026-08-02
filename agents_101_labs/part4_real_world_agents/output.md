# Part 4 — Agents in the Real World: Agent Archetype Classifier Output

```
================================================================================
  AGENT ARCHETYPE CLASSIFIER
  Classify tasks -> agent type -> harness requirements
================================================================================

================================================================================
  AGENT ARCHETYPE CLASSIFIER — Results
================================================================================

   #  Archetype            Match  Task
   —  ————————————————————  —————  —————————————————————————————————————
   1  coding                  OK  Fix the failing unit test in auth.py and refa...
   2  deep_research           OK  Research the top 5 AI agent frameworks and wr...
   3  computer_use            OK  Fill out the vendor registration form on the ...
   4  enterprise_workflow     OK  Route this support ticket to the billing team...
   5  coding                  OK  Write a Python script to parse CSV files and ...
   6  enterprise_workflow   MISS  Search for recent papers on multi-agent syste...
   7  enterprise_workflow   MISS  Book a flight on the travel portal and update...
   8  enterprise_workflow     OK  Onboard the new hire by creating accounts and...
   9  coding                  OK  Debug the memory leak in the production serve...
  10  deep_research           OK  Analyze customer feedback from the last quart...

  Accuracy: 8/10 (80%)

================================================================================
  HARNESS REQUIREMENTS BY ARCHETYPE
================================================================================

  [CODING] (3 tasks)
    Description:  Plans, edits files, runs code, and verifies
    Tools:        file_system, code_execution, terminal, git
    Memory:       session
    Planning:     iterative with reflection
    Safety:       sandbox, no_network_by_default

  [COMPUTER_USE] (1 tasks)
    Description:  Operates a screen or browser to complete tasks across apps
    Tools:        browser_control, screenshot, keyboard, mouse
    Memory:       short-term
    Planning:     visual_step_by_step
    Safety:       rate_limiting, confirm_before_actions

  [DEEP_RESEARCH] (2 tasks)
    Description:  Plans a research question, searches the web, synthesizes a cited report
    Tools:        web_search, page_fetch, summarization, citation
    Memory:       session_with_citations
    Planning:     multi_step_with_reflection
    Safety:       source_verification, no_executable_output

  [ENTERPRISE_WORKFLOW] (4 tasks)
    Description:  Customer support, operations, and analysis in production
    Tools:        api_calls, database_query, email, ticketing
    Memory:       persistent
    Planning:     rule_based_with_escalation
    Safety:       human_in_loop, audit_logging, guardrails

================================================================================
  STATISTICS
================================================================================

  Tasks per archetype:
    enterprise_workflow   4  ################
    coding                3  ############
    deep_research         2  ########
    computer_use          1  ####

  Most common tools needed:
    api_calls             4x
    database_query        4x
    email                 4x
    ticketing             4x
    file_system           3x

================================================================================
  HYBRID ARCHETYPE DETECTION
================================================================================
  Task 5: coding + deep_research (scores: {'coding': 2, 'computer_use': 0, 'deep_research': 1, 'enterprise_workflow': 0})
  Task 10: deep_research + enterprise_workflow (scores: {'coding': 0, 'computer_use': 0, 'deep_research': 1, 'enterprise_workflow': 1})
```
