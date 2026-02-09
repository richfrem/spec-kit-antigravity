This project was initialized with the Antigravity Spec-Kit.

## Quick Setup

After cloning or syncing this project, run the bridge sync scripts:

```bash
python3 tools/bridge/speckit_system_bridge.py
python3 tools/bridge/sync_rules.py --all
python3 tools/bridge/sync_skills.py --all
```

⚠️ **Restart Required**: After running these commands, restart the IDE for slash commands (e.g., `/spec-kitty.specify`) to appear.

## Documentation

- See [README.md](./README.md) for full documentation
- See [tools/bridge/README.md](./tools/bridge/README.md) for bridge system details
