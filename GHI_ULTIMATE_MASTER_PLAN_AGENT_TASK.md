### Objective

This issue commissions the GitHub Copilot agent to execute the full `ULTIMATE_MASTER_PLAN.md`. The final goal is to reconcile the `wkpup` and `wkpup2` simulation systems by implementing all 11 deliverables outlined in the master plan.

### Guiding Principles

- **Unerring Accuracy**: Every action must be cross-referenced with `COMPREHENSIVE_ANALYSIS.md` to ensure it aligns with the validated, ground-truth implementation.
- **Persistent Execution**: The agent must work through the plan systematically, part-by-part, without stopping, until all 11 deliverables are complete.
- **Structured Workflow**: All work must be committed to the `experimental` branch of the `wkpup-paiho-implementation` repository.

### Reference Documents

1.  **Primary Task List**: [`ULTIMATE_MASTER_PLAN.md`](./ULTIMATE_MASTER_PLAN.md) - This document contains the 11 deliverables to be completed. It is the source of truth for WHAT to do.
2.  **Verification & Ground Truth**: [`COMPREHENSIVE_ANALYSIS.md`](./COMPREHENSIVE_ANALYSIS.md) - This document contains the detailed analysis of the existing, correct `wkpup2` implementation. Use it to verify correctness and understand the "why" behind each task.

### Execution Workflow (Mandatory Loop)

The agent must follow this iterative process for EACH of the 11 deliverables:

1.  **PLAN**:
    - Read the `ULTIMATE_MASTER_PLAN.md` and identify the next "not-started" deliverable.
    - Read the corresponding sections in `COMPREHENSIVE_ANALYSIS.md` to build a complete and accurate context for the task.

2.  **EXECUTE**:
    - Perform the work required for the deliverable. This may involve creating files, writing analysis, or modifying scripts.
    - All new files for a deliverable (e.g., `INCONSISTENCY_ANALYSIS.md`) should be created within a new `deliverables/` directory in the `wkpup-paiho-implementation` repository.

3.  **VERIFY**:
    - Before committing, re-read the relevant sections of `COMPREHENSIVE_ANALYSIS.md` one last time to ensure the work is accurate and complete.

4.  **COMMIT**:
    - Commit the completed work to the `experimental` branch.
    - The commit message must be descriptive, e.g., `feat: Complete Deliverable 1 - Inconsistency Analysis`.

5.  **UPDATE & REPEAT**:
    - Modify the `ULTIMATE_MASTER_PLAN.md` to mark the completed deliverable as "completed".
    - Commit this status update.
    - Loop back to step 1 for the next deliverable.

### Initial Setup

- **Repository**: `seb917intel/wkpup-paiho-implementation`
- **Branch**: `experimental`

The agent's first action should be to ensure it is operating on the `experimental` branch.

This structured process ensures that the master plan is followed precisely, with a high degree of accuracy, leading to the successful reconciliation of the two systems.
