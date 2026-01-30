#!/usr/bin/env python3
"""
Temporary script to update template path references.
Changes .agent/templates -> .agent/templates
"""

import os
import glob

OLD_PATH = ".agent/templates"
NEW_PATH = ".agent/templates"

# Directories to scan
SCAN_DIRS = ["workflows", "templates", "memory", "docs", "scripts", "README.md", "CHANGELOG.md"]
EXTENSIONS = [".md", ".py", ".sh", ".ps1"]

def main():
    print(f"🔄 Updating template path references...")
    print(f"   {OLD_PATH} -> {NEW_PATH}\n")
    
    files_updated = 0
    
    for scan_path in SCAN_DIRS:
        if os.path.isfile(scan_path):
            files = [scan_path]
        elif os.path.isdir(scan_path):
            files = []
            for ext in EXTENSIONS:
                files.extend(glob.glob(f"{scan_path}/**/*{ext}", recursive=True))
        else:
            continue
        
        for filepath in files:
            if ".git" in filepath or "dist_" in filepath:
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if OLD_PATH in content:
                    new_content = content.replace(OLD_PATH, NEW_PATH)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    count = content.count(OLD_PATH)
                    print(f"  ✓ {filepath}: {count} refs updated")
                    files_updated += 1
            except Exception as e:
                print(f"  ⚠ {filepath}: {e}")
    
    print(f"\n✅ Updated {files_updated} files.")

if __name__ == "__main__":
    main()
