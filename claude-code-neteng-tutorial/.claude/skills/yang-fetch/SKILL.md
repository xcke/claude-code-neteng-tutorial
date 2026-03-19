---
name: "yang-fetch"
description: "Fetch live YANG/NETCONF data from a Cisco IOS-XE device via the DevNet sandbox."
---

## Instructions

Use this skill when the user wants to pull live YANG data from a network device via NETCONF.

1. Verify the sandbox environment variables are set. If not, prompt the user:

   ```bash
   export NETCONF_HOST="your-sandbox-host.cisco.com"
   export NETCONF_USER="your-username"
   export NETCONF_PASS="your-password"
   ```

   Users get credentials by launching the **Catalyst 8000V** sandbox at
   [developer.cisco.com/site/sandbox](https://developer.cisco.com/site/sandbox/).

2. Run the helper script:

   ```bash
   python .claude/skills/yang-fetch/fetch_yang_data.py --filter <filter>
   ```

   Supported `--filter` values:
   - `interfaces` (default) — fetch all interfaces using the `ietf-interfaces` YANG model
   - `version` — fetch the IOS-XE software version using `Cisco-IOS-XE-native`
   - `all` — run both queries and display combined output

3. Present the output as a formatted table. If the connection fails,
   report the error clearly and suggest the user verify their sandbox
   credentials and reservation status.

4. If the user asks about the YANG models being used, explain:
   - `ietf-interfaces` (RFC 8343) — vendor-neutral interface config and state
   - `Cisco-IOS-XE-native` — Cisco's native YANG model for full device config

## Prerequisites

```bash
pip install -r requirements.txt
```

Requires: `ncclient`, `xmltodict`
