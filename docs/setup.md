# Setup

This project follows the Hekton reproducible setup standard:

```text
documented -> scripted -> idempotent-ish -> logged -> reproducible on a blank machine
```

## Intended Flow

```bash
./scripts/check-prereqs.sh
./scripts/bootstrap-project.sh --dry-run
./scripts/bootstrap-project.sh
./scripts/verify-project.sh
```

## Project-Specific Steps

1. **Python package, editable, with dev extras:**
   ```bash
   pip install -e ".[dev]"
   ```
   Zero runtime dependencies otherwise (ADR: "Stack" in `docs/decisions.md`) — `pytest` is the
   only thing the `dev` extra adds.

2. **`hekton_llm` (the local-LLM executor Kriterion calls through) — not a declared
   `pyproject.toml` dependency, by design**, so "zero runtime dependencies" stays honest for
   Kriterion's own package. Install it separately, editable, from its own repo:
   ```bash
   pip install -e ../../platform/hekton-local-llm
   ```
   Distribution name is `local-llm-lab`; the import namespace is `hekton_llm` (mismatch is
   upstream, not a typo here — see `docs/decisions.md`, Task 7). Path is relative to this repo's
   location inside the Hekton monorepo; adjust if you've checked `kriterion` out elsewhere.

3. **A local Ollama server with the target model pulled:**
   ```bash
   ollama pull qwen2.5:14b-instruct
   ```
   `src/kriterion/executors/hekton_local.py` binds to `hekton_llm/ollama_client.py`'s
   `OllamaClient`, which expects Ollama reachable at `http://localhost:11434` by default.

4. **Verify the whole chain is live**, not just installed:
   ```bash
   kriterion doctor
   ```
   Expect `kriterion doctor: READY` plus a schema-valid smoke completion. A `NOT READY` result
   here names the exact failure (Ollama unreachable, vs. model not pulled) rather than a bare
   connection error.

5. **Run the test suite** (no live model calls — `kriterion doctor`/`kriterion run` are the only
   commands that touch Ollama):
   ```bash
   pytest
   ```

