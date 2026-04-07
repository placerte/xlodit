# AGENTS

## Current Reality (high signal)
- This repository is mostly a scaffold: `src/` is empty, there are no `*.py` files, no `tests/`, and no CI/workflow config.
- `README.md` is empty; do not assume setup/run commands exist yet.
- `pyproject.toml` is minimal and currently authoritative for runtime constraints: project name `xlodit`, version `0.1.0`, Python `>=3.13`, and no declared dependencies.

## Where Requirements Live
- Product/spec intent currently lives in `docs/handoff_260407_1.md` (not in code yet). Treat it as planning input, not proof of implementation.
- If implementing from that handoff, preserve requirement IDs exactly (`S-*`, `I-*`, `T-*`, `DoD-*`) so traceability remains searchable.

## Instruction Sources Already In-Repo
- `llm/agent_executor_instructions_v_1.md` and `llm/general_executor_instructions_v1.md` are marked `status: active` and define strict artifact-driven execution.
- Several `llm/` docs are marked `status: deprecated` (for example `llm/code_style.md`, `llm/progress_tracker.md`, `llm/sessions_logger.md`, `llm/gotchas.md`, `llm/user-persona.md`); do not treat them as default policy unless a task explicitly asks for them.

## Practical Guardrails For Future Sessions
- Verify commands from repo config before running them; most common commands are not wired yet.
- When bootstrapping implementation, establish missing source-of-truth files first (real `README.md`, package under `src/`, test config, and CI) so later agents can rely on executable config instead of prose docs.
