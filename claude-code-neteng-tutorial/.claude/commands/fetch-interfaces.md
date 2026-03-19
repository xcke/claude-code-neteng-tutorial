Fetch live YANG/NETCONF data from the Cisco DevNet always-on IOS-XE sandbox.

Run the following command with the filter set to: $ARGUMENTS

```bash
python .claude/skills/yang-fetch/fetch_yang_data.py --filter $ARGUMENTS
```

If no argument is provided, default to `interfaces`.

Present the output as a clean table. If the connection fails, explain that the
Cisco DevNet sandbox may be down and link to https://devnetsandbox.cisco.com/.
