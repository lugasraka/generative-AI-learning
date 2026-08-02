# AGENTS.md — Coding Agent Instructions

## Project Overview

This is a learning-oriented Python lab companion repository forked from `awesome-generative-ai-guide`. It contains standalone Python scripts organized into three course tracks:

- `agentic_ai_crash_course_labs/` — 10 parts (complete)
- `ai_evals_for_everyone_labs/` — 11 chapters (complete)
- `applied_llms_mastery_labs/` — 12 parts (complete)

Sibling directories (`agentic_ai_crash_course/`, `ai_evals_for_everyone/`, `Applied_LLMs_Mastery_2024/`) contain the original course markdown — treat these as read-only reference material.

Scripts are standalone — no package structure, no `__init__.py`, no shared library. Each `.py` file is an independent, runnable demo.

---

## Build / Run / Lint / Test Commands

### Running Scripts

```bash
python <script>.py                  # Run any script directly
python use_case_classifier.py      # Example
```

Each script has a `Run:` line in its module docstring showing the exact command.

### Linting

Ruff is the linter (v0.15.22 observed in `.ruff_cache/`). No config file exists — it runs with defaults.

```bash
ruff check .                       # Lint entire repo
ruff check path/to/script.py       # Lint a single file
ruff format .                      # Auto-format
ruff format --check .              # Check formatting without writing
```

### Testing

There is **no test framework** (no pytest, unittest, etc.). Scripts self-test via `if __name__ == "__main__": main()`. To verify a script works, run it directly. Some scripts require interactive input; set values via stdin or modify the script for non-interactive testing.

### Type Checking

No mypy or pyright configuration. Type annotations are present on most function signatures but not enforced by tooling.

### No CI/CD

No GitHub Actions, no Makefile, no tox. All verification is manual.

---

## Code Style Guidelines

### Language & Runtime

- **Python 3.10+** — use PEP 604 union types (`str | None`) and PEP 585 generics (`list[str]`, `dict[str, int]`, `tuple[str, float]`).
- **Zero external dependencies** for most scripts. Only stdlib modules (`json`, `subprocess`, `sys`, `os`, `csv`, `re`, `argparse`, `pathlib`, `time`, `textwrap`). One exception: `reportlab` in `make_one_pager.py`.

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Functions | `snake_case` | `ask_llm()`, `classify_rules()` |
| Variables | `snake_case` | `final_acc`, `dataset_size` |
| Constants | `UPPER_SNAKE_CASE` | `MODEL`, `SYSTEM_PROMPT`, `TEST_CASES` |
| Files | `snake_case.py` | `metric_runner.py` |
| Directories | `snake_case/` | `part3_prompting_and_prompt_engineering/` |

No classes are used anywhere — the codebase is purely procedural/functional.

### Imports

- **Absolute imports only** — never use relative imports (`from . import`).
- **Stdlib first**, no blank line separation needed between groups.
- For local sibling imports, use `sys.path.insert`:
  ```python
  HERE = Path(__file__).parent
  sys.path.insert(0, str(HERE))
  from system_prompt import get_prompt, list_versions  # noqa: E402
  ```
- Use `# noqa: E402` on imports that follow non-import code.
- Use import aliasing when the same function name comes from different modules:
  ```python
  from metric_policy_accuracy import check as check_policy
  from metric_information_gathering import check as check_info
  ```

### Type Annotations

- Annotate **all function parameters and return types** on core logic functions.
- Use PEP 604 (`str | None`) not `Optional[str]`.
- Use PEP 585 builtins (`list`, `dict`, `tuple`) not `typing.List`, etc.
- Inline variable annotations are encouraged where helpful:
  ```python
  tf_map: dict[str, int] = {}
  warnings: list[str] = []
  ```

### Error Handling

- **LLM subprocess calls** return error strings, not exceptions. Callers detect errors by checking for `[` prefix:
  ```python
  def ask_llm(prompt: str) -> str:
      result = subprocess.run(
          ["opencode", "run", "-m", MODEL, prompt],
          capture_output=True, text=True, encoding="utf-8",
      )
      if result.returncode != 0:
          return f"[opencode error] {result.stderr.strip()}"
      return result.stdout.strip()
  ```
- **JSON parsing** uses `try/except json.JSONDecodeError` with a fallback string.
- **User input** catches `(ValueError, EOFError)` and `(EOFError, KeyboardInterrupt)` for non-interactive environments.
- **No custom exception classes** — use built-in exceptions only.

### Docstrings

- **Every file** must start with a module-level docstring:
  ```python
  """
  Part N — Title: Subtitle

  Brief description of what this script does.

  Run:  python script_name.py
  """
  ```
- Core functions get a one-line docstring. Display/helper functions may omit them.

### Formatting

- **4-space indentation**, no tabs.
- **Double quotes** for strings predominantly.
- **f-strings** for all string formatting.
- **Trailing commas** in multi-line structures.
- Line length ~88-100 chars (Black/Ruff defaults).
- Section separators use `# ---------- Section Name ----------`.
- ASCII progress bars: `[##.....]` pattern.

### Boilerplate Patterns

UTF-8 Windows fix (include at the top of scripts that print Unicode):
```python
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")
```

Model configuration:
```python
MODEL = os.environ.get("OPENCODE_MODEL", "opencode-go/deepseek-v4-flash")
```

Entry point:
```python
if __name__ == "__main__":
    main()
```

---

## Project Structure Conventions

- Each `*_labs/` directory has a `PROGRESS.md` checklist tracking completion.
- Data artifacts (CSV, JSON, markdown reports) are committed as first-class deliverables.
- Course material directories are read-only reference — do not modify files in `agentic_ai_crash_course/`, `ai_evals_for_everyone/`, or `Applied_LLMs_Mastery_2024/`.
- New lab scripts go in the appropriate part/chapter subdirectory under the matching `*_labs/` directory.
- Each part/chapter directory typically contains: the main script, a README or reflection markdown, and any generated results.

---

## Cursor / Copilot Rules

No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` files exist in this repository.
