#!/usr/bin/env python3
"""
Temporary script to find and report legacy command references.
This helps identify what build.py's sanitize_content will fix during build.

Usage:
    python3 scripts/dev/fix_command_refs.py [--fix]
    
    --fix: Actually modify source files (optional, default is report-only)
"""

import os
import re
import sys
import glob

# Commands that need speckit- prefix
COMMANDS = [
    "analyze", "specify", "plan", "tasks", "implement", 
    "constitution", "clarify", "checklist", "tasks-to-issues"
]

# Directories to scan
SCAN_DIRS = ["workflows", "templates", "memory", "docs"]
EXTENSIONS = [".md", ".py", ".sh", ".ps1"]

# Files to exclude (build artifacts, etc.)
EXCLUDE_PATTERNS = ["dist_", ".agent/", "__pycache__", ".git/"]

def should_exclude(filepath):
    return any(ex in filepath for ex in EXCLUDE_PATTERNS)

def find_legacy_refs(content, filepath):
    """Find legacy command references in content."""
    findings = []
    
    for cmd in COMMANDS:
        # Pattern for slash commands: /cmd (not already prefixed)
        # Negative lookbehind for speckit- to avoid double-matching
        slash_pattern = rf'(?<!/speckit-)/({cmd})(?!\w)'
        
        for match in re.finditer(slash_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                'file': filepath,
                'line': line_num,
                'type': 'slash_command',
                'old': f'/{cmd}',
                'new': f'/speckit-{cmd}',
                'context': content[max(0, match.start()-20):match.end()+20]
            })
        
        # Pattern for workflow file refs: cmd.md (not in artifact paths like specs/)
        # This is trickier - we want workflow refs but not artifact refs
        md_pattern = rf'\.agent/workflows/(?!templates/)({cmd})\.md'
        for match in re.finditer(md_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                'file': filepath,
                'line': line_num,
                'type': 'workflow_file_ref',
                'old': f'{cmd}.md',
                'new': f'speckit-{cmd}.md',
                'context': content[max(0, match.start()-20):match.end()+20]
            })
    
    return findings

def apply_fixes(content):
    """Apply fixes to content (for --fix mode)."""
    for cmd in COMMANDS:
        # Fix slash commands
        content = re.sub(rf'(?<!/speckit-)/({cmd})(?!\w)', f'/speckit-{cmd}', content)
        # Fix workflow file refs
        content = re.sub(rf'(\.agent/workflows/)(?!templates/)({cmd})(\.md)', rf'\1speckit-{cmd}\3', content)
    return content

def main():
    fix_mode = '--fix' in sys.argv
    
    print("🔍 Scanning for legacy command references...")
    print(f"   Mode: {'FIX' if fix_mode else 'REPORT ONLY'}\n")
    
    all_findings = []
    
    for scan_dir in SCAN_DIRS:
        if not os.path.exists(scan_dir):
            continue
        
        for ext in EXTENSIONS:
            for filepath in glob.glob(f"{scan_dir}/**/*{ext}", recursive=True):
                if should_exclude(filepath):
                    continue
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    findings = find_legacy_refs(content, filepath)
                    all_findings.extend(findings)
                    
                    if fix_mode and findings:
                        fixed_content = apply_fixes(content)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        print(f"  ✓ Fixed {len(findings)} refs in {filepath}")
                        
                except Exception as e:
                    print(f"  ⚠ Error processing {filepath}: {e}")
    
    # Report
    print("\n" + "="*60)
    if not all_findings:
        print("✅ No legacy command references found!")
    else:
        print(f"📋 Found {len(all_findings)} legacy references:\n")
        
        # Group by file
        by_file = {}
        for f in all_findings:
            by_file.setdefault(f['file'], []).append(f)
        
        for filepath, findings in by_file.items():
            print(f"  {filepath}:")
            for f in findings:
                print(f"    L{f['line']}: {f['old']} → {f['new']}")
        
        if not fix_mode:
            print("\n💡 Run with --fix to apply changes to source files.")
            print("   OR rely on build.py to fix them in the .agent/ output.")
    
    print("="*60)
    return 0 if not all_findings else 1

if __name__ == "__main__":
    sys.exit(main())
