# network-automation

Network automation project for Example Inc — IOS-XE devices across two sites (Dallas, New York).

## Commands

```bash
pip install -r requirements.txt          # Install Python dependencies
python .claude/skills/yang-fetch/fetch_yang_data.py --filter interfaces  # Fetch live YANG data
```

## Architecture

- `devices.yml` — device inventory (4 devices, 2 sites, role-specific params)
- `templates/` — Jinja2 config templates (`base-config.j2`)
- `configs/` — rendered configuration output directory
- `.claude/skills/` — agent skills (yang-fetch, bgp-best-practices, wan-cpe-troubleshooting)
- `.claude/commands/` — slash commands (fetch-interfaces, review-bgp-config, troubleshoot-wan-cpe)

## Conventions

- IOS-XE is the primary target platform
- All configs must include service timestamps, SSH v2, and banner motd
- BGP configs follow RFC 7454 best practices (see bgp-best-practices skill)
- Use `devices.yml` as the single source of truth for device parameters
- Generated configs go in `configs/` — never edit them by hand
