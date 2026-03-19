#!/usr/bin/env python3
"""Fetch YANG data from a Cisco IOS-XE device via NETCONF.

Designed for the Cisco DevNet Catalyst 8000V sandbox. Launch a sandbox at:
https://developer.cisco.com/site/sandbox/

Set environment variables before running:
    export NETCONF_HOST="your-sandbox-host.cisco.com"
    export NETCONF_USER="your-username"
    export NETCONF_PASS="your-password"

Usage:
    python fetch_yang_data.py --filter interfaces   # default
    python fetch_yang_data.py --filter version
    python fetch_yang_data.py --filter all
"""

import argparse
import os
import sys

try:
    from ncclient import manager
    from ncclient.transport.errors import SSHError
except ImportError:
    print("Error: ncclient is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import xmltodict
except ImportError:
    print("Error: xmltodict is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def get_device_params():
    """Build connection params from environment variables."""
    host = os.environ.get("NETCONF_HOST")
    user = os.environ.get("NETCONF_USER")
    password = os.environ.get("NETCONF_PASS")

    if not all([host, user, password]):
        print("Error: set NETCONF_HOST, NETCONF_USER, and NETCONF_PASS environment variables.")
        print()
        print("Launch a Catalyst 8000V sandbox at:")
        print("  https://developer.cisco.com/site/sandbox/")
        print()
        print("Then export the credentials:")
        print('  export NETCONF_HOST="your-sandbox-host.cisco.com"')
        print('  export NETCONF_USER="your-username"')
        print('  export NETCONF_PASS="your-password"')
        sys.exit(1)

    return {
        "host": host,
        "port": int(os.environ.get("NETCONF_PORT", "830")),
        "username": user,
        "password": password,
        "hostkey_verify": False,
        "timeout": 30,
    }

INTF_FILTER = ("subtree", """
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
""")

VERSION_FILTER = ("subtree", """
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <version/>
  </native>
""")


def connect():
    """Establish a NETCONF session to the device."""
    params = get_device_params()
    try:
        return manager.connect(**params)
    except SSHError as e:
        print(f"Connection failed: {e}")
        print("The Cisco DevNet sandbox may be temporarily unavailable.")
        print("Check status: https://devnetsandbox.cisco.com/")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error connecting: {e}")
        sys.exit(1)


def fetch_interfaces(m):
    """Fetch interface data using the ietf-interfaces YANG model."""
    result = m.get(filter=INTF_FILTER)
    parsed = xmltodict.parse(result.xml)

    interfaces = parsed["rpc-reply"]["data"]["interfaces"]["interface"]
    if isinstance(interfaces, dict):
        interfaces = [interfaces]

    headers = ["Name", "IP Address", "Status"]
    widths = [28, 18, 10]

    print("\n" + "".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("\u2500" * sum(widths))

    for intf in interfaces:
        name = intf.get("name", "N/A")

        enabled = intf.get("enabled", "N/A")
        if enabled == "true":
            status = "up"
        elif enabled == "false":
            status = "down"
        else:
            status = enabled

        ipv4 = intf.get("ipv4", {})
        if isinstance(ipv4, dict):
            addr_info = ipv4.get("address", {})
            if isinstance(addr_info, list):
                addr_info = addr_info[0]
            ip = addr_info.get("ip", "\u2014") if isinstance(addr_info, dict) else "\u2014"
        else:
            ip = "\u2014"

        print(f"{name:<{widths[0]}}{ip:<{widths[1]}}{status:<{widths[2]}}")

    print()


def fetch_version(m):
    """Fetch software version using the Cisco-IOS-XE-native YANG model."""
    result = m.get_config(source="running", filter=VERSION_FILTER)
    parsed = xmltodict.parse(result.xml)

    version = parsed["rpc-reply"]["data"]["native"]["version"]
    print(f"\nIOS-XE Version: {version}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch YANG data from Cisco DevNet sandbox via NETCONF"
    )
    parser.add_argument(
        "--filter",
        choices=["interfaces", "version", "all"],
        default="interfaces",
        help="Data to fetch (default: interfaces)",
    )
    args = parser.parse_args()

    m = connect()

    try:
        if args.filter in ("interfaces", "all"):
            fetch_interfaces(m)
        if args.filter in ("version", "all"):
            fetch_version(m)
    finally:
        m.close_session()


if __name__ == "__main__":
    main()
