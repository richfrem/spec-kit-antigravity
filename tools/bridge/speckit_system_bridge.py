#!/usr/bin/env python3
"""
speckit_system_bridge.py
=====================================
Purpose:
    The "Universal Bridge" Synchronization Engine.
    Reads Spec Kitty definitions (Windsurf + Memory) and projects them into native
    configurations for:
    1.  Antigravity (.agent/)
    2.  Claude (.claude/)
    3.  Gemini (.gemini/)
    4.  GitHub Copilot (.github/)

    Philosophy:
    "Bring Your Own Agent" (BYOA). Maintain a Single Source of Truth in Spec Kitty,
    and auto-generate the necessary config files for any supported agent.

Usage:
    python tools/bridge/speckit_system_bridge.py
"""
import os
import shutil
from pathlib import Path
import re
import sys
import toml
import yaml

# Force UTF-8 for Windows Consoles
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WINDSURF_DIR = PROJECT_ROOT / ".windsurf"
KITTIFY_DIR = PROJECT_ROOT / ".kittify"

# Targets
AGENT_DIR = PROJECT_ROOT / ".agent"
CLAUDE_DIR = PROJECT_ROOT / ".claude"
GEMINI_DIR = PROJECT_ROOT / ".gemini"
GITHUB_DIR = PROJECT_ROOT / ".github"


def setup_directories():
    """Ensure all target directory structures exist and are clean (Idempotency)."""
    print(f"🔧 Initializing & Cleaning Target Directories...")
    
    # helper to clean
    def clean_dir(path: Path):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    # 1. Antigravity
    (AGENT_DIR / "rules").mkdir(parents=True, exist_ok=True) # Rules might be partial, keep dir
    clean_dir(AGENT_DIR / "workflows")
    
    # 2. Claude
    clean_dir(CLAUDE_DIR / "commands")
    
    # 3. Gemini
    clean_dir(GEMINI_DIR / "commands")
    
    # 4. Copilot
    clean_dir(GITHUB_DIR / "prompts")


def ingest_rules():
    """Read rules from .kittify/memory (Source of Truth)."""
    rules = {}
    memory_dir = KITTIFY_DIR / "memory"
    
    if not memory_dir.exists():
        print("⚠️  No .kittify/memory directory found. Rules will be empty.")
        return rules
        
    for rule_file in sorted(memory_dir.rglob("*.md")):
        try:
            content = rule_file.read_text(encoding="utf-8")
            rules[rule_file.stem] = content
        except Exception as e:
            print(f"⚠️  Failed to read rule {rule_file.name}: {e}")
            
    return rules

def ingest_workflows():
    """Read workflows from .windsurf/workflows (Source of Truth)."""
    workflows = {}
    source_dir = WINDSURF_DIR / "workflows"
    
    if not source_dir.exists():
        print("⚠️  No .windsurf/workflows directory found. Workflows will be empty.")
        return workflows
        
    for wf_file in sorted(source_dir.rglob("*.md")):
        try:
            content = wf_file.read_text(encoding="utf-8")
            workflows[wf_file.name] = content # Key is full filename (spec-kitty.accept.md)
        except Exception as e:
            print(f"⚠️  Failed to read workflow {wf_file.name}: {e}")
            
    return workflows

def sync_antigravity(workflows, rules):
    """Sync to .agent/ (Antigravity)."""
    print("\n🔵 Syncing Antigravity (.agent)...")
    
    # Rules (e.g., constitution.md)
    # Note: We didn't clean rules dir above to avoid wiping constitution if manual?
    # Actually, BYOA says .agent is an artifact. We should probably clean it too.
    # But let's stick to overwriting for now.
    for name, content in rules.items():
        (AGENT_DIR / "rules" / f"{name}.md").write_text(content, encoding="utf-8")
        
    for filename, content in workflows.items():
        fixed_content = content.replace('--actor "windsurf"', '--actor "antigravity"')
        fixed_content = fixed_content.replace('(Missing script command for sh)', 'spec-kitty')
        (AGENT_DIR / "workflows" / filename).write_text(fixed_content, encoding="utf-8")
        
    print(f"   ✅ Synced {len(rules)} rules and {len(workflows)} workflows.")

def sync_claude(workflows, rules):
    """Sync to .claude/."""
    print("\n🟠 Syncing Claude (.claude)...")
    
    # 1. Context (CLAUDE.md)
    claude_md = CLAUDE_DIR / "CLAUDE.md"
    content = ["# Claude Assistant Instructions\n"]
    content.append("Managed by Spec Kitty Bridge.\n\n")
    
    for name, rule_text in rules.items():
        content.append(f"## {name}\n\n{rule_text}\n\n---\n\n")
        
    claude_md.write_text("".join(content), encoding="utf-8")
    
    # 2. Commands/Prompts (.claude/commands/*.md)
    count = 0
    for filename, text in workflows.items():
        fixed_text = text.replace('--actor "windsurf"', '--actor "claude"')
        fixed_text = fixed_text.replace('(Missing script command for sh)', 'spec-kitty')
        (CLAUDE_DIR / "commands" / filename).write_text(fixed_text, encoding="utf-8")
        count += 1
        
    print(f"   ✅ Generated CLAUDE.md and {count} commands.")

def sync_gemini(workflows, rules):
    """Sync to .gemini/."""
    print("\n✨ Syncing Gemini (.gemini)...")
    
    # 1. Context (GEMINI.md)
    gemini_md = GEMINI_DIR / "GEMINI.md"
    root_gemini_md = PROJECT_ROOT / "GEMINI.md"
    
    content = ["# Gemini CLI Instructions\n"]
    content.append("Managed by Spec Kitty Bridge.\n\n")
    
    for name, rule_text in rules.items():
        content.append(f"## {name}\n\n{rule_text}\n\n---\n\n")
        
    root_gemini_md.write_text("".join(content), encoding="utf-8")
    
    # 2. Commands (.gemini/commands/*.toml)
    count = 0
    for filename, text in workflows.items():
        stem = filename.replace(".md", "") 
        
        description = f"Executes {stem}"
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                fm = text[3:end]
                for line in fm.split("\n"):
                    if line.startswith("description:"):
                        description = line.split(":", 1)[1].strip().strip('"')
                        break
                        
        description = description.replace('"', '\\"')
        fixed_text = text.replace('--actor "windsurf"', '--actor "gemini"')
        fixed_text = fixed_text.replace('$ARGUMENTS', '{{args}}')
        fixed_text = fixed_text.replace('(Missing script command for sh)', 'spec-kitty')
        
        toml_content = f'description = "{description}"\n\nprompt = """\n{fixed_text}\n"""\n'
        
        (GEMINI_DIR / "commands" / f"{stem}.toml").write_text(toml_content, encoding="utf-8")
        count += 1
        
    print(f"   ✅ Generated GEMINI.md and {count} commands.")

def sync_copilot(workflows, rules):
    """Sync to .github/ (Copilot)."""
    print("\n🤖 Syncing Copilot (.github)...")

    # 1. Instructions (copilot-instructions.md)
    instr_file = GITHUB_DIR / "copilot-instructions.md"

    content = ["# Copilot Instructions\n"]
    content.append("> Managed by Spec Kitty Bridge.\n\n")

    for name, rule_text in rules.items():
        content.append(f"## Rule: {name}\n\n{rule_text}\n\n---\n\n")

    # Index Workflows
    content.append("\n# Available Workflows\n")
    for filename in workflows.keys():
        stem = filename.replace(".md", "")
        content.append(f"- /prompts/{stem}.prompt.md\n")

    instr_file.write_text("".join(content), encoding="utf-8")

    # 2. Prompts (.github/prompts/*.prompt.md)
    count = 0
    for filename, text in workflows.items():
        stem = filename.replace(".md", "")
        fixed_text = text.replace('--actor "windsurf"', '--actor "copilot"')
        fixed_text = fixed_text.replace('(Missing script command for sh)', 'spec-kitty')

        target_file = GITHUB_DIR / "prompts" / f"{stem}.prompt.md"
        target_file.write_text(fixed_text, encoding="utf-8")
        count += 1

    print(f"   ✅ Generated copilot-instructions.md and {count} prompts.")

def update_kittify_config():
    """Update .kittify/config.yaml to register all synced agents."""
    print("\n⚙️  Updating .kittify/config.yaml...")

    config_file = KITTIFY_DIR / "config.yaml"

    # Define all agents that the bridge supports
    all_agents = ["windsurf", "claude", "antigravity", "gemini", "copilot"]

    try:
        # Read existing config
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}

        # Ensure agents section exists
        if 'agents' not in config:
            config['agents'] = {}

        # Update available agents list (preserve order, add new ones)
        current_agents = config['agents'].get('available', [])
        updated_agents = []

        # Keep existing agents in their order
        for agent in current_agents:
            if agent in all_agents:
                updated_agents.append(agent)

        # Add any missing agents
        for agent in all_agents:
            if agent not in updated_agents:
                updated_agents.append(agent)

        config['agents']['available'] = updated_agents

        # Ensure selection section exists with defaults if not present
        if 'selection' not in config['agents']:
            config['agents']['selection'] = {
                'strategy': 'preferred',
                'preferred_implementer': 'claude',
                'preferred_reviewer': 'claude'
            }

        # Write back to file
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"   ✅ Registered {len(updated_agents)} agents: {', '.join(updated_agents)}")

    except Exception as e:
        print(f"   ⚠️  Failed to update config.yaml: {e}")
        print(f"   💡 You may need to manually add agents to .kittify/config.yaml")

def main():
    print("🚀 Starting Spec Kitty Bridge Sync...")

    setup_directories()

    # 1. Ingest Source (Spec Kitty)
    rules = ingest_rules()
    workflows = ingest_workflows()

    if not workflows and not rules:
        print("❌ No source data found in .windsurf or .kittify. Run 'spec-kitty init' first.")
        return

    # 2. Project to All Agents
    sync_antigravity(workflows, rules)
    sync_claude(workflows, rules)
    sync_gemini(workflows, rules)
    sync_copilot(workflows, rules)

    # 3. Update Kittify Config to Register All Agents
    update_kittify_config()

    print("\n🎉 Bridge Sync Complete. All agents are configured.")

if __name__ == "__main__":
    main()
