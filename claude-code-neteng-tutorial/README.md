# Claude Code for Network Engineers — Tutorial Companion

Supporting materials for the [Getting started with Claude Code as a network engineer](https://internetworking.dev/blog/getting-started-with-claude-code-as-a-network-engineer) tutorial on internetworking.dev.

## What's in this repo

| Item | Path | Description |
|------|------|-------------|
| Project constitution | `CLAUDE.md` | Tells Claude Code about the project structure and conventions |
| YANG fetch skill | `.claude/skills/yang-fetch/` | Fetches live NETCONF data from the Cisco DevNet sandbox |
| YANG fetch script | `.claude/skills/yang-fetch/fetch_yang_data.py` | ncclient + xmltodict script for NETCONF queries |
| BGP best practices skill | `.claude/skills/bgp-best-practices/` | RFC-cited BGP configuration review checklist |
| WAN CPE troubleshooting skill | `.claude/skills/wan-cpe-troubleshooting/` | NOC runbook for Example Inc ISR 4331 CPE devices |
| Fetch interfaces command | `.claude/commands/fetch-interfaces.md` | `/project:fetch-interfaces [filter]` |
| Review BGP config command | `.claude/commands/review-bgp-config.md` | `/project:review-bgp-config <config>` |
| Troubleshoot WAN CPE command | `.claude/commands/troubleshoot-wan-cpe.md` | `/project:troubleshoot-wan-cpe <site>` |
| Device inventory | `devices.yml` | 4 devices across 2 sites with role-specific parameters |
| Config template | `templates/base-config.j2` | Jinja2 starter template for base device configs |
| Output directory | `configs/` | Rendered configuration files land here |

## Prerequisites

- [Claude Code](https://github.com/anthropics/claude-code) installed
- Python 3.8+
- Install dependencies:

```bash
pip install -r requirements.txt
```

This installs: `ncclient`, `xmltodict`, `pyyaml`, `jinja2`

## Quick start

```bash
git clone https://github.com/xcke/blog-examples.git
cd blog-examples/claude-code-neteng-tutorial
pip install -r requirements.txt
claude
```

Then try:

```text
/project:fetch-interfaces interfaces
/project:fetch-interfaces version
/project:review-bgp-config <paste a BGP config block>
/project:troubleshoot-wan-cpe dallas
```

Or try the build exercise:

```text
> Create a Python script called generate_configs.py that reads devices.yml
  and templates/base-config.j2, then renders a config for each device.
  For wan-edge devices, add a BGP section using the device's bgp params.
  For access-switch devices, add VLAN definitions.
  Save each config to configs/{hostname}.cfg.
```

## Related

- [Tutorial blog post](https://internetworking.dev/blog/getting-started-with-claude-code-as-a-network-engineer)
- [YANG deep dive](https://internetworking.dev/blog/yang-the-network-data-model)
- [Claude Code documentation](https://code.claude.com/docs/en/overview)
