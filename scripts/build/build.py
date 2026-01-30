#!/usr/bin/env python3
"""
Antigravity Agent Builder script.

This script assembles the .agent distribution folder from the source directories in the repository root.
It acts as the build step for the project, ensuring that the distributed artifacts (ZIP files) 
are clean, consistent, and free of development environment artifacts.

Usage:
    python3 scripts/build/build.py [options]

Options:
    --clean         Remove existing .agent folder before building
    --verbose       Show detailed output

Source Directories:
    workflows/      -> .agent/workflows/   (Agent behaviors)
    memory/         -> .agent/memory/      (Constitution & Context)
    scripts/        -> .agent/scripts/     (Bash/PS scripts)
    templates/      -> .agent/templates/   (Project templates, if present)

Outputs:
    .agent/         The fully assembled agent configuration folder ready for distribution.

Examples:
    # Standard build
    python3 scripts/build/build.py

    # Clean build (delete .agent first)
    python3 scripts/build/build.py --clean
"""

import os
import shutil
import sys
import argparse
import glob
import re

# --- Configuration ---
DIST_DIR = ".agent"

# Source Mapping: (Source Path -> Destination Path relative to DIST_DIR)
SOURCES = {
    "workflows": "workflows",
    "memory": "memory",
    # Scripts are kept in root scripts/ dir, not copied to .agent
    # "scripts": "scripts",
    # If templates (root) exists, sync it.
    "templates": "templates"
}

# --- Logic ---

def clean_dist():
    """Removes the existing distribution directory."""
    if os.path.exists(DIST_DIR):
        print(f"Cleaning {DIST_DIR}...")
        shutil.rmtree(DIST_DIR)

def ensure_dirs():
    """Ensures all destination directories exist."""
    os.makedirs(DIST_DIR, exist_ok=True)
    for dest_sub in SOURCES.values():
        os.makedirs(os.path.join(DIST_DIR, dest_sub), exist_ok=True)

def copy_sources():
    """Copies files from source directories to distribution directory."""
    print("Copying sources...")
    
    for src_name, dest_sub in SOURCES.items():
        if not os.path.exists(src_name):
            print(f"Warning: Source '{src_name}/' not found. Skipping.")
            continue
            
        print(f"  • {src_name}/ -> {DIST_DIR}/{dest_sub}/")
        
        # We walk the source to copy fully recursive
        dest_root = os.path.join(DIST_DIR, dest_sub)
        
        # If destination exists and we are not cleaning, better to sync explicitly
        if os.path.exists(dest_root):
            # shutil.copytree requires dest NOT to exist usually, so we use dirs_exist_ok
            # For scripts, exclude the build tooling
            if src_name == "scripts":
                shutil.copytree(src_name, dest_root, dirs_exist_ok=True, ignore=shutil.ignore_patterns('build', 'dev', '__pycache__', '*.py'))
            else:
                shutil.copytree(src_name, dest_root, dirs_exist_ok=True)
        else:
            if src_name == "scripts":
                shutil.copytree(src_name, dest_root, ignore=shutil.ignore_patterns('build', 'dev', '__pycache__', '*.py'))
            else:
                shutil.copytree(src_name, dest_root)

def sanitize_content():
    """
    Scans all text files in the distribution folder and applies
    normalization rules (e.g. converting legacy paths).
    """
    print("Sanitizing content...")
    
    all_files = glob.glob(os.path.join(DIST_DIR, "**", "*"), recursive=True)
    count = 0
    
    for filepath in all_files:
        if not os.path.isfile(filepath): continue
        if filepath.endswith((".png", ".zip", ".jpg", ".pyc")): continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # --- Transformations ---
            
            # 1. Path Normalization
            # Ensure any references to .specify or .gemini refer to .agent
            content = content.replace(".specify/", ".agent/")
            content = content.replace(".gemini/", ".agent/")
            
            # 2. Workflow / Command Normalization
            # Ensure we use standard names (e.g. /plan instead of /speckit.plan)
            # This handles cases where source templates might still have legacy refs
            legacy_cmds = [
                ("speckit-analyze", "analyze"),
                ("speckit-specify", "specify"),
                ("speckit-plan", "plan"),
                ("speckit-tasks", "tasks"),
                ("speckit-implement", "implement"),
                ("speckit-constitution", "constitution"),
                ("speckit-clarify", "clarify"),
                ("speckit-checklist", "checklist"),
                ("speckit-taskstoissues", "tasks-to-issues")
            ]
            
            for old, new in legacy_cmds:
                # Replace slash commands
                content = re.sub(f"/speckit\.{new}", f"/{new}", content)
                content = re.sub(f"/{old}", f"/{new}", content)
                
                # Replace file references
                content = content.replace(f"{old}.md", f"{new}.md")
                
            # 3. Agent Folder Structure checks
            # (Adding .agent/ prefix if missing for known internal paths?)
            # content = content.replace("workflows/", ".agent/workflows/") 
            # ^ Too risky to do globally without context match.
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1
                
        except Exception as e:
            # Likely binary file
            pass
            
    print(f"  • Updated content in {count} files.")

def main():
    parser = argparse.ArgumentParser(description="Antigravity Agent Builder")
    parser.add_argument("--clean", action="store_true", help="Remove existing .agent folder first")
    args = parser.parse_args()
    
    if args.clean:
        clean_dist()
    
    ensure_dirs()
    copy_sources()
    sanitize_content()
    
    print(f"\n✅ Build Complete. Distribution is ready in '{DIST_DIR}/'")

if __name__ == "__main__":
    main()
