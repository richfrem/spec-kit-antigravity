#!/usr/bin/env python3
"""
Sync Skills Bridge
------------------
Synchronizes skill documentation from .agent/skills/ into the monolithic 
configuration files for other agents (Claude, Gemini, Copilot).

Usage:
    python3 tools/bridge/sync_skills.py --all

Target Files:
    - .claude/CLAUDE.md
    - .github/copilot-instructions.md
    - GEMINI.md
"""

import os
import sys
import argparse
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / ".agent" / "skills"
TARGETS = {
    "CLAUDE": PROJECT_ROOT / ".claude" / "CLAUDE.md",
    "COPILOT": PROJECT_ROOT / ".github" / "copilot-instructions.md",
    "GEMINI": PROJECT_ROOT / "GEMINI.md"
}

MARKER_START = "<!-- SKILLS_SYNC_START -->"
MARKER_END = "<!-- SKILLS_SYNC_END -->"

def get_all_skills_content():
    """Reads all SKILL.md files in the skills directory."""
    content = []
    if not SKILLS_DIR.exists():
        return ""
        
    # Walk through skill directories
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                content.append(f"\n\n--- SKILL: {skill_dir.name} ---\n\n")
                content.append(skill_file.read_text())
    return "".join(content)

def update_file(target_name, target_path, new_content):
    """Updates the target file between markers or appends if not present."""
    if not target_path.exists():
        print(f"[{target_name}] File not found: {target_path}, skipping.")
        return

    original_content = target_path.read_text()
    
    # Construct the block
    injection_block = f"{MARKER_START}\n# SHARED SKILLS FROM .agent/skills/\n{new_content}\n{MARKER_END}"

    if MARKER_START in original_content and MARKER_END in original_content:
        # Replace existing block
        pre = original_content.split(MARKER_START)[0]
        post = original_content.split(MARKER_END)[1]
        updated_content = pre + injection_block + post
        print(f"[{target_name}] Updating existing skills block.")
    else:
        # Append to end
        updated_content = original_content + "\n\n" + injection_block
        print(f"[{target_name}] Appending new skills block.")

    target_path.write_text(updated_content)

def main():
    parser = argparse.ArgumentParser(description="Sync agent skills to monolithic files.")
    parser.add_argument("--all", action="store_true", help="Sync ALL skills from .agent/skills/")
    args = parser.parse_args()

    if args.all:
        content = get_all_skills_content()
    else:
        print("Usage: provide --all")
        sys.exit(1)

    print(f"Syncing skills to: {list(TARGETS.keys())}")
    for name, path in TARGETS.items():
        update_file(name, path, content)
    print("Done.")

if __name__ == "__main__":
    main()
