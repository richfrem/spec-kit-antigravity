# Gemini CLI Instructions
Managed by Spec Kitty Bridge.



<!-- RULES_SYNC_START -->
# SHARED RULES FROM .agent/rules/


--- RULE: constitution.md ---

# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### [PRINCIPLE_1_NAME]
<!-- Example: I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### [PRINCIPLE_2_NAME]
<!-- Example: II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### [PRINCIPLE_3_NAME]
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### [PRINCIPLE_4_NAME]
<!-- Example: IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### [PRINCIPLE_5_NAME]
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

## [SECTION_2_NAME]
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

[SECTION_2_CONTENT]
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## [SECTION_3_NAME]
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

[SECTION_3_CONTENT]
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->


--- RULE: standard-workflow-rules.md ---

# Git Worktree & Branch Lifecycle Protocol

> **Status:** MANDATORY
> **Enforcement:** Strict
> **Visual Guide:** [Standard Workflow Diagram](../docs/kittify/standard-spec-kitty-workflow.mmd)

## Context
This project utilizes a **Spec-Work-Package (WP)** workflow powered by `spec-kitty`. The "Standard Workflow" relies on **Worktree Isolation** and **Automated Batch Merging**.

## The Golden Rules

1.  **NEVER Merge Manually.** Spec-Kitty handles the merge.
2.  **NEVER Delete Worktrees Manually.** Spec-Kitty handles the cleanup.
    - **safe:** `git push origin WP-xx` (Backup feature branch)
    - **unsafe:** `git push origin main` (Never push directly to main)
3.  **NEVER Commit to Main directly.** Always working in a `.worktrees/WP-xx` folder.

## The Protocol

### Phase 1: The WP Execution Loop (Repeated)
For each Work Package (WP01, WP02...):

1.  **Initialize:**
    - Command: `spec-kitty implement WP-xx`
    - Action: `cd .worktrees/WP-xx`
    - **CRITICAL:** Do NOT proceed unless `pwd` confirms you are in the worktree.

2.  **Implement:**
    - Edit files **ONLY** inside the worktree.
    - Verify/Test inside the worktree.

3.  **Commit (Local Feature Branch):**
    - Command: `git add .`
    - Command: `git commit -m "feat(WP-xx): ..."`
    - **Note:** This commits to the LOCAL feature branch. Do **NOT** push to origin unless explicitly instructed for backup. Do **NOT** merge to main.

4.  **Submit for Review:**
    - Command: `spec-kitty agent tasks move-task WP-xx --to for_review`
    - Result: The CLI automatically updates `tasks.md` and the prompt file. You are done with this WP.

### Phase 2: Feature Completion (Once All WPs Done)
When **ALL** WPs in `tasks.md` are marked `[x]`:

1.  **Verify Readiness:**
    - Command: `spec-kitty accept`
    - Action: Run from **Main Repo Root**.

2.  **The Automated Merge:**
    - Command: `spec-kitty merge`
    - Context: **Main Repo Root**.
    - **System Action:** It automates the merge of ALL feature worktrees into `main` and cleans them up.
    - **Optional:** `spec-kitty merge --push` (if remote backup is required).

## Common Agent Failures (DO NOT DO THIS)
*   ❌ **Merging early:** Merging WP01 before WP02 is done. (Breaks the batch).
*   ❌ **Deleting worktrees:** Removing `.worktrees/WP01` manually. (Breaks `spec-kitty merge`).
*   ❌ **Drifting:** Editing files in `./` (Root) instead of `.worktrees/`. (Pollutes main).
*   ❌ **Relative Paths:** Agents using relative paths often get lost. **ALWAYS use Absolute Paths** for `view_file` and edits.
*   ❌ **Pushing to main:** `git push origin main` will fail with branch protection. Push feature branches only.
*   ❌ **Forgetting cd:** After `spec-kitty implement`, you MUST `cd .worktrees/<WP>/` before any file operations.
*   ❌ **Wrong branch commits:** Committing doc updates while in main repo instead of worktree.

## Naming Convention Reference

| Item | Pattern | Example |
|------|---------|---------|
| Worktree Dir | `.worktrees/<feature-num>-<slug>-<WP>` | `.worktrees/002-screener-ui-WP07` |
| Branch Name | `<feature-num>-<slug>-<WP>` | `002-screener-ui-WP07` |
| Remote Push | `git push origin <branch>` | `git push origin 002-screener-ui-WP07` |

## Additional Resources

- [Agent Worktree Reference](../docs/kittify/agent-worktree-reference.md) - Quick reference for common worktree operations

<!-- RULES_SYNC_END -->

<!-- SKILLS_SYNC_START -->
# SHARED SKILLS FROM .agent/skills/


--- SKILL: spec_kitty_workflow ---

---
name: Spec Kitty Workflow
description: Standard operating procedures for the Spec Kitty agentic workflow (Plan -> Implement -> Review -> Merge).
---

# Spec Kitty Workflow

This skill documents the standard lifecycle for implementing features using Spec Kitty.

## 1. Start a Work Package (WP)
Always start by creating an isolated worktree for the task.

```bash
# syntax: spec-kitty implement <WP-ID>
spec-kitty implement WP06
```

**Note**: If the previous WP was merged to main, use `--base main` if the tool doesn't auto-detect it.
```bash
spec-kitty implement WP06 --base main
```

## 2. Implementation Loop
1.  **Navigate**: `cd .worktrees/<WP-ID>`
2.  **Install**: `npm install` (backend/frontend)
3.  **Code**: Implement the feature.
4.  **Verify**: Run tests or manual verification.
5.  **Commit**: `git add . && git commit -m "feat(WPxx): description"` (Local worktree commit)

## 3. Review & Handover
Once functionality is complete and verified:

1.  **Mark Complete**: Update `kitty-specs/.../tasks.md` marking subtasks `[x]`.
2.  **Sync Specs**: Commit the spec changes in the **Main Repo** (not worktree).
    ```bash
    cd <PROJECT_ROOT>
    git add kitty-specs
    git commit -m "docs(specs): mark WPxx complete"
    ```
3.  **Move Task**:
    ```bash
    spec-kitty agent tasks move-task WPxx --to for_review
    ```

## 4. Merge & Cleanup
After approval (or self-approval in agentic mode):

1.  **Accept**: Validate readiness.
    ```bash
    spec-kitty accept
    ```
2.  **Merge**: Auto-merge worktree into main.
    ```bash
    spec-kitty merge
    ```
    *If this fails (e.g., due to worktree detection issues), use the manual fallback:*
    ```bash
    # Fallback Manual Merge
    git merge <WP-BRANCH-NAME>
    git worktree remove .worktrees/<WP-FOLDER>
    git branch -d <WP-BRANCH-NAME>
    ```

## Common Issues
-   **"Base workspace not found"**:
    -   If the WP depends on a previous WP that is **already merged**, Spec Kitty might block you.
    -   **Solution**: Manually create the worktree off `main`.
        ```bash
        git worktree add .worktrees/<FULL-WP-FOLDER-NAME> main
        cd .worktrees/<FULL-WP-FOLDER-NAME>
        git checkout -b <WP-BRANCH-NAME>
        ```

-   **"Already on main"**: Merge commands must be run from the project root, not inside a worktree.

<!-- SKILLS_SYNC_END -->