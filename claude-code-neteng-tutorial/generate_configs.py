#!/usr/bin/env python3
"""Generate device configs from devices.yml and Jinja2 templates."""

import ipaddress
import os
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


def prefix_to_network_mask(prefix: str) -> tuple[str, str]:
    """Convert a CIDR prefix (e.g. '10.10.0.0/16') to (network, wildcard-mask) tuple."""
    net = ipaddress.ip_network(prefix, strict=False)
    return str(net.network_address), str(net.netmask)


def render_bgp_section(bgp: dict) -> str:
    """Render the IOS-XE BGP config block for a wan-edge device."""
    lines = []
    lines.append(f"router bgp {bgp['asn']}")
    lines.append(f" bgp router-id {bgp['router_id']}")
    lines.append(" bgp log-neighbor-changes")
    lines.append(f" neighbor {bgp['peer_ip']} remote-as {bgp['peer_asn']}")
    lines.append(" !")
    lines.append(" address-family ipv4 unicast")
    for prefix in bgp["advertised_prefixes"]:
        network, mask = prefix_to_network_mask(prefix)
        lines.append(f"  network {network} mask {mask}")
    lines.append(f"  neighbor {bgp['peer_ip']} activate")
    lines.append(" exit-address-family")
    return "\n".join(lines) + "\n"


def render_vlan_section(vlans: list[dict]) -> str:
    """Render the IOS-XE VLAN definitions for an access-switch device."""
    lines = []
    for vlan in vlans:
        lines.append(f"vlan {vlan['id']}")
        lines.append(f" name {vlan['name']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    configs_dir = base_dir / "configs"
    configs_dir.mkdir(exist_ok=True)

    # Load inventory
    with open(base_dir / "devices.yml") as f:
        inventory = yaml.safe_load(f)

    sites = inventory["sites"]
    devices = inventory["devices"]

    # Set up Jinja2
    env = Environment(
        loader=FileSystemLoader(str(base_dir / "templates")),
        keep_trailing_newline=True,
    )
    base_template = env.get_template("base-config.j2")

    for device in devices:
        site = sites[device["site"]]

        # Render the base config
        config = base_template.render(device=device, site=site)

        # Strip the trailing "end\n" so we can append role-specific sections
        # before re-adding it.
        if config.rstrip().endswith("end"):
            config = config.rstrip()[: -len("end")].rstrip() + "\n"

        # Append role-specific sections
        role_detail = ""
        if device["role"] == "wan-edge" and "bgp" in device:
            config += "!\n"
            config += render_bgp_section(device["bgp"])
            role_detail = f"BGP AS {device['bgp']['asn']}"
        elif device["role"] == "access-switch" and "vlans" in device:
            config += "!\n"
            config += render_vlan_section(device["vlans"])
            vlan_count = len(device["vlans"])
            role_detail = f"{vlan_count} VLANs"

        # Re-add the end marker
        config += "!\nend\n"

        # Write to file
        out_path = configs_dir / f"{device['hostname']}.cfg"
        with open(out_path, "w") as f:
            f.write(config)

        print(f"Generated: configs/{device['hostname']}.cfg  ({device['role']}, {role_detail})")


if __name__ == "__main__":
    main()
