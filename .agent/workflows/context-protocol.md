---
description: Protocol for maintaining AI_CONTEXT.md and project documentation
---

# 🧠 AI Context Maintenance Protocol

## Philosophy
**Context is Currency.** To work efficiently across sessions and agents, we must maintain a high-fidelity "external brain". We do not rely on implicit chat history; we rely on explicit, structured documentation.

## The Documentation Stack (Token Efficiency Strategy)

1.  **`AI_CONTEXT.md` (The Brain)**
    *   **Role**: Narrative history, current state, architectural decisions, and "gotchas".
    *   **Update Frequency**: End of every significant task or session.
    *   **Content**: High-level summaries. *Links* to other docs.

2.  **`docs/architecture.md` (The Skeleton)**
    *   **Role**: Static structural reference.
    *   **Update Frequency**: ONLY when the code structure or patterns change.
    *   **Content**: Diagrams, file organization, core logic explanations.

3.  **`task.md` (The Notepad)**
    *   **Role**: Short-term execution tracking.
    *   **Update Frequency**: Constant.
    *   **Lifecycle**:
        *   *Start of Session*: Fresh or carried over.
        *   *During Session*: Mark items as `[x]`.
        *   *End of Session*: **Summarize** completed items into `AI_CONTEXT.md` -> **Clear/Archive** completed items.

## The "Definition of Done"
A task or session is NOT done until:
1.  [ ] Code is implemented and verified.
2.  [ ] `task.md` is updated (items marked `[x]`).
3.  [ ] **Context Update Triggered**: The `/update-context` workflow has been run.
    *   This moves `task.md` completions to `AI_CONTEXT.md` history.
    *   This updates `docs/architecture.md` if needed.

## Rules
*   **No Duplication**: Do not copy-paste code into `AI_CONTEXT.md`. Use file links.
*   **Honesty**: If a hack was used, document it in "Risks & Gotchas".
*   **Progressive Updates**: Don't wait until the very last second. If a major sub-task is done, update the context.
