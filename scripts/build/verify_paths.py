#!/usr/bin/env python3
import os
import re
import sys

# Define expected patterns
# Key: Pattern to search for
# Value: What to check (e.g. "Should not exist", "Should be X")
CHECKS = {
    r"\.agent/templates/": "ERROR: Should be .agent/workflows/templates/",
    r"memory/": "ERROR: Should be rules/ (or .agent/rules/)",
    r"\.agent/memory/": "ERROR: Should be .agent/rules/",
    r"scripts/bash/": "INFO: Verifying script path context...", 
}

# Where to look
SCAN_DIRS = ["workflows", "templates", "scripts", "rules"]
IGNORE_DIRS = ["scripts/build", "scripts/dev", "__pycache__"]

def scan_file(filepath):
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
            
        for i, line in enumerate(lines):
            for pattern, msg in CHECKS.items():
                if re.search(pattern, line):
                    # Special Case: scripts/bash/
                    # If inside a workflow, it SHOULD be scripts/bash/ (Root)
                    # If inside a script, it uses $REPO_ROOT/scripts/bash
                    # If it says .agent/scripts/bash, that is WRONG (unless build.py changed again)
                    
                    if pattern == "scripts/bash/":
                        if ".agent/scripts/bash/" in line:
                             issues.append(f"Line {i+1}: Found '.agent/scripts/bash/' -> Should be 'scripts/bash/' (Root relative)")
                        continue # Plain scripts/bash/ is OK in root context

                    issues.append(f"Line {i+1}: Found '{pattern}' -> {msg}")
                    
        return issues
    except Exception as e:
        return [f"Could not read file: {e}"]

def main():
    print("🔍 Scanning for incorrect path references...")
    found_issues = False
    
    repo_root = os.getcwd()
    
    for d in SCAN_DIRS:
        root_path = os.path.join(repo_root, d)
        if not os.path.exists(root_path):
            print(f"⚠️  Directory not found: {d}")
            continue
            
        for root, dirs, files in os.walk(root_path):
            # Prune ignored
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in IGNORE_DIRS]
            
            for file in files:
                if not file.endswith(('.md', '.sh', '.py')) or file == "verify_paths.py":
                    continue
                    
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, repo_root)
                
                results = scan_file(path)
                if results:
                    print(f"\n📂 {rel_path}:")
                    for r in results:
                        print(f"  ❌ {r}")
                    found_issues = True

    if not found_issues:
        print("\n✅ No obvious path issues found!")
        sys.exit(0)
    else:
        print("\n🚫 Issues found. Please review.")
        sys.exit(1)

if __name__ == "__main__":
    main()
