---
description: Update AI_CONTEXT.md and architecture docs based on recent work
---

# 🔄 Update Context Workflow

This workflow consolidates session progress into the permanent context memory.

1.  **Review `task.md`**
    - Identify all items marked as completed `[x]`.
    - Formulate a concise summary of these achievements (e.g., "Implemented X, Fixed Y").

2.  **Update `AI_CONTEXT.md`**
    - **Append to "Session Log"**: Add a new entry with today's date and the summary from step 1.
    - **Update "Current State"**: Reflect any changes in what is working/broken.
    - **Update "Risks"**: If new risks were discovered, add them.

3.  **Check Architecture**
    - Did we add new modules, change core logic flow, or add major dependencies?
    - **If YES**: Update `docs/architecture.md` to reflect the new structure.
    - **If NO**: Skip this step.

4.  **Maintain `.gitignore`**
    - Check if any new temporary files, build artifacts, or sensitive data were generated.
    - Ensure they are properly excluded in `.gitignore`.

5.  **Clean Up `task.md`**
    - Remove the completed items `[x]` (or move them to an `## Archived` section at the bottom if preference dictates).
    - Ensure the "To Do" list is clean for the next session.

6.  **Notify User**
    - Confirm that context has been saved.
