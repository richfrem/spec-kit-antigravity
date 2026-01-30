#!/usr/bin/env python3
"""
Antigravity Release Packager.

This script packages the current state of the .agent configuration into deployable ZIP artifacts.
It automatically triggers a clean build before packaging to ensure artifacts are up-to-date
with the source directories.

Usage:
    python3 scripts/build/package_release.py [options]

Options:
    --no-build      Skip the build step (package current .agent folder as-is)
    --output-dir    Directory to save ZIP files (default: dist_output/)

Artifacts Produced:
    spec-kit-template-antigravity-sh.zip (Bash version)
    spec-kit-template-antigravity-ps.zip (Powershell version - legacy)

Workflow:
    1. Run build.py (clean) -> Generates .agent/
    2. Stage .agent/ content + README marker
    3. Zip content into artifacts

Examples:
    # Build and package
    python3 scripts/dev/package_release.py

    # Package existing .agent only
    python3 scripts/build/package_release.py --no-build
"""

import os
import zipfile
import shutil
import argparse
from build import main as run_build

def package_release(skip_build=False, output_dir="dist_output"):
    print("📦 Packaging Antigravity Release...")
    
    # 1. Run Build (ensure .agent is fresh)
    if not skip_build:
        print(">> Triggering Clean Build...")
        # Since we are calling build.main(), we need to mock sys.argv or just rely on defaults
        # build.main parses args, so let's call the functions directly if possible or simulate args
        # Easier to just rely on build.py being in the same dir
        try:
            # We invoke the build modules clean & build functions
            import build
            build.clean_dist()
            build.ensure_dirs()
            build.copy_sources()
            build.sanitize_content()
        except ImportError:
            print("Error: Could not import build.py. Make sure it is in scripts/build/")
            return
    
    if not os.path.exists(".agent"):
        print("Error: .agent directory not found. Build failed or was skipped incorrectly.")
        return

    # 2. Prepare Staging Area
    staging_dir = "dist_staging"
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    os.makedirs(staging_dir)
    
    # 3. Copy .agent folder to staging
    # IMPORTANT: We want .agent to be the top level folder in the zip
    print(f"  • Staging .agent/ -> {staging_dir}/.agent/")
    shutil.copytree(".agent", os.path.join(staging_dir, ".agent"))
    
    # 3b. Copy scripts/ (Root) -> staging/scripts/
    # Exclude build tooling
    print(f"  • Staging scripts/ -> {staging_dir}/scripts/")
    shutil.copytree("scripts", os.path.join(staging_dir, "scripts"), 
                    ignore=shutil.ignore_patterns('build', 'dev', '__pycache__', '*.py'))

    # 3c. Copy README.md (Root) -> staging/README.md
    print(f"  • Staging README.md -> {staging_dir}/README.md")
    shutil.copy2("README.md", os.path.join(staging_dir, "README.md"))

    # 4. Create README marker (Anti-flattening hack for CLI)
    with open(os.path.join(staging_dir, "README_antigravity.txt"), "w") as f:
        f.write("Spec-Kit for Antigravity\nInitialized successfully.\n")
        
    # 5. Create ZIPs
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_name = "spec-kit-template-antigravity"
    sh_zip = os.path.join(output_dir, f"{base_name}-sh.zip")
    ps_zip = os.path.join(output_dir, f"{base_name}-ps.zip")
    
    # Zip the CONTENTS of staging_dir
    print(f"  • Creating {sh_zip}...")
    with zipfile.ZipFile(sh_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(staging_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Arcname should be relative to staging_dir
                # e.g. .agent/workflows/plan.md or README_antigravity.txt
                arcname = os.path.relpath(file_path, staging_dir)
                zf.write(file_path, arcname)
                
    # Copy for PowerShell variant
    print(f"  • Creating {ps_zip}...")
    shutil.copy2(sh_zip, ps_zip)
    
    # 6. Cleanup
    shutil.rmtree(staging_dir)
    print(f"\n✅ Packaging Complete. Artifacts available in '{output_dir}/'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Release Packager")
    parser.add_argument("--no-build", action="store_true", help="Skip build step")
    parser.add_argument("--output-dir", default="dist_output", help="Output directory")
    args = parser.parse_args()
    
    package_release(skip_build=args.no_build, output_dir=args.output_dir)
