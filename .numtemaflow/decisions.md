# Decision Log

## DEC-001 — Initial project memory convention
- Date:
- Context: ProjectFlow local memory is used to keep project state across agent sessions.
- Decision: Store local project memory in `.numtemaflow/`.
- Why: Keeps the global skill separate from project-specific state.
- Impact: Agents must read and update `.numtemaflow/` during substantial work.
