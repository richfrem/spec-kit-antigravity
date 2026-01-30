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
    memory/         -> .agent/rules/       (Passive Guardrails)
    templates/      -> .agent/workflows/templates/   (Project templates, if present)

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
    "memory": "rules",
    # Scripts are kept in root scripts/ dir, not copied to .agent
    # "scripts": "scripts",
    # If templates (root) exists, sync it.
    "templates": "workflows/templates"
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
    
    base_cmds = [
        "analyze", "specify", "plan", "tasks", "implement", "constitution", 
        "clarify", "checklist", "tasks-to-issues"
    ]
    
    all_files = glob.glob(os.path.join(DIST_DIR, "**", "*"), recursive=True)
    count = 0
    
    for filepath in all_files:
        if not os.path.isfile(filepath): continue
        if filepath.endswith((".png", ".zip", ".jpg", ".pyc")): continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. Path Normalization
            content = content.replace(".specify/", ".agent/")
            content = content.replace(".gemini/", ".agent/")
            
            # 2. Workflow / Command Normalization
            for cmd in base_cmds:
                # Enforce /speckit-cmd
                content = re.sub(f"/(?!speckit-){cmd}", f"/speckit-{cmd}", content)
                content = re.sub(f"/speckit\.{cmd}", f"/speckit-{cmd}", content)
                
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1
                
        except Exception as e:
            # Likely binary file
            pass
            
    print(f"  • Updated content in {count} files.")

def rename_workflows():
    """
    Renames workflow files to include 'speckit-' prefix.
    """
    print("Renaming workflow files...")
    workflows_dir = os.path.join(DIST_DIR, "workflows")
    if not os.path.exists(workflows_dir): return
    
    base_cmds = [
        "analyze", "specify", "plan", "tasks", "implement", "constitution", 
        "clarify", "checklist", "tasks-to-issues"
    ]
    
    count = 0
    for fname in os.listdir(workflows_dir):
        if fname.endswith(".md") and not fname.startswith("speckit-"):
            name_root = fname.replace(".md", "")
            if name_root in base_cmds:
                old_p = os.path.join(workflows_dir, fname)
                new_p = os.path.join(workflows_dir, f"speckit-{fname}")
                os.rename(old_p, new_p)
                count += 1
    print(f"  • Renamed {count} workflows.")

def main():
    parser = argparse.ArgumentParser(description="Antigravity Agent Builder")
    parser.add_argument("--clean", action="store_true", help="Remove existing .agent folder first")
    args = parser.parse_args()
    
    if args.clean:
        clean_dist()
    
    ensure_dirs()
    copy_sources()
    # Note: Source workflow files are already prefixed with speckit-
    # No renaming needed, just sanitize content for any legacy refs
    sanitize_content()
    
    print(f"\n✅ Build Complete. Distribution is ready in '{DIST_DIR}/'")

if __name__ == "__main__":
    main()
