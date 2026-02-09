---
description: Create an isolated workspace (worktree) for implementing a specific work package.
---


## ⚠️ CRITICAL: Working Directory Requirement

**After running `spec-kitty implement WP##`, you MUST:**

1. **Run the cd command shown in the output** - e.g., `cd .worktrees/###-feature-WP##/`
2. **ALL file operations happen in this directory** - Read, Write, Edit tools must target files in the workspace
3. **NEVER write deliverable files to the main repository** - This is a critical workflow error

**Why this matters:**
- Each WP has an isolated worktree with its own branch
- Changes in main repository will NOT be seen by reviewers looking at the WP worktree
- Writing to main instead of the workspace causes review failures and merge conflicts

---

**IMPORTANT**: After running the command below, you'll see a LONG work package prompt (~1000+ lines).

**You MUST scroll to the BOTTOM** to see the completion command!

Run this command to get the work package prompt and implementation instructions:

```bash
spec-kitty agent workflow implement $ARGUMENTS --agent <your-name>
```

**CRITICAL**: You MUST provide `--agent <your-name>` to track who is implementing!

If no WP ID is provided, it will automatically find the first work package with `lane: "planned"` and move it to "doing" for you.

---

## Commit Workflow

**BEFORE moving to for_review**, you MUST commit your implementation:

```bash
cd .worktrees/###-feature-WP##/
git add -A
git commit -m "feat(WP##): <describe your implementation>"
```

## Backup to Origin (Recommended)

**Push your work to a remote feature branch for safety:**

```bash
git push origin <branch-name>
# Example: git push origin 002-screener-ui-improvements-WP07
```

> ⚠️ **NEVER push to origin/main** - main has branch protection!
> 
> Always push to the feature branch. The merge to main happens via PR.

**Then move to review:**
```bash
spec-kitty agent tasks move-task WP## --to for_review --note "Ready for review: <summary>"
```

**Why this matters:**
- `move-task` validates that your worktree has commits beyond main
- Uncommitted changes will block the move to for_review
- This prevents lost work and ensures reviewers see complete implementations

---

## Naming Conventions

### Worktree Directory:
```
.worktrees/<feature-number>-<feature-slug>-<WP-ID>/
```
Example: `.worktrees/002-screener-ui-improvements-WP07/`

### Branch Name:
```
<feature-number>-<feature-slug>-<WP-ID>
```
Example: `002-screener-ui-improvements-WP07`

---

**The Python script handles all file updates automatically - no manual editing required!**

**NOTE**: If `/spec-kitty.status` shows your WP in "doing" after you moved it to "for_review", don't panic - a reviewer may have moved it back (changes requested), or there's a sync delay. Focus on your WP.

## Quick Reference

See [Agent Worktree Reference](/Users/richardfremmerlid/Projects/InvestmentToolkit/.agent/docs/kittify/agent-worktree-reference.md) for common mistakes and troubleshooting.
