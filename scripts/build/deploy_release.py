#!/usr/bin/env python3
"""
Antigravity Release Deployer.

Uploads the packaged artifacts (ZIPs) to GitHub Releases.
Requires 'gh' CLI tool to be installed and authenticated.

Usage:
    python3 scripts/build/deploy_release.py --tag v1.0.0 --title "Release v1.0.0" [options]

Options:
    --tag       Git tag for the release (required)
    --title     Title for the release (required)
    --draft     Create as a draft release
    --prerelease Mark as prerelease
    --dist-dir  Directory containing artifacts (default: dist_output/)

Dependencies:
    - scripts/build/package_release.py (Must be run first to generate artifacts)
    - scripts/build/build.py (Triggered by package_release.py)

Examples:
    python3 scripts/build/deploy_release.py --tag v0.0.1 --title "Initial Antigravity Release"
"""

import os
import sys
import glob
import argparse
import subprocess

DIST_DIR = "dist_output"

def check_gh_cli():
    """Checks if gh CLI is installed."""
    try:
        subprocess.run(["gh", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def deploy(tag, title, draft=False, prerelease=False, dist_dir=DIST_DIR):
    if not check_gh_cli():
        print("Error: 'gh' CLI tool not found. Please install GitHub CLI.")
        sys.exit(1)

    # Gather artifacts
    artifacts = glob.glob(os.path.join(dist_dir, "*.zip"))
    if not artifacts:
        print(f"Error: No .zip artifacts found in {dist_dir}. Run package_release.py first.")
        sys.exit(1)

    print(f"Deploying {len(artifacts)} artifacts to release '{tag}'...")
    for art in artifacts:
        print(f"  • {os.path.basename(art)}")

    # Construct gh command
    cmd = ["gh", "release", "create", tag, "--title", title]
    if draft:
        cmd.append("--draft")
    if prerelease:
        cmd.append("--prerelease")
    
    # Append artifact paths
    cmd.extend(artifacts)
    
    print("\nRunning command:")
    print(" ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Release {tag} created/updated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Release failed with error code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Release Deployer")
    parser.add_argument("--tag", required=True, help="Git tag for the release")
    parser.add_argument("--title", required=True, help="Release title")
    parser.add_argument("--draft", action="store_true", help="Create as draft")
    parser.add_argument("--prerelease", action="store_true", help="Mark as prerelease")
    parser.add_argument("--dist-dir", default=DIST_DIR, help="Artifact directory")
    
    args = parser.parse_args()
    
    deploy(args.tag, args.title, args.draft, args.prerelease, args.dist_dir)
