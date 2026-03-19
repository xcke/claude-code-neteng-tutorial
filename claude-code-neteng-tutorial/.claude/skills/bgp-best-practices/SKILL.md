---
name: "bgp-best-practices"
description: "Review or generate BGP configurations against industry best practices with RFC citations."
---

## Instructions

Use this skill when reviewing, auditing, or generating BGP configurations.
Check each configuration against the categories below and report compliance.

When generating new BGP config, apply all applicable best practices by default.
When reviewing existing config, list each category as **compliant**, **non-compliant**,
or **not applicable** with a brief explanation.

## Best practice categories

### 1. Peer groups and templates
Use `neighbor peer-group` or `template peer-policy` / `template peer-session` to reduce
configuration duplication and improve consistency.
**Reference**: [Cisco IOS XE BGP Configuration Guide](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_bgp/configuration/xe-16/irg-xe-16-book.html)

### 2. Route filtering with prefix-lists
Apply inbound and outbound prefix-lists on every eBGP session. Never accept or advertise
the full Internet table without explicit filtering. Block RFC 1918, default route, and
bogon prefixes inbound.
**Reference**: RFC 7454 — BGP Operations and Security, §6

### 3. Maximum prefix limits with restart
Configure `neighbor <x> maximum-prefix <limit> <threshold> restart <minutes>` on every
eBGP session to protect against route leaks and table explosions. Set the threshold at
80% for warning, with automatic restart after a cool-down period.
**Reference**: RFC 7454, §6.3

### 4. BFD (Bidirectional Forwarding Detection)
Enable BFD on all BGP sessions where sub-second failure detection is needed.
```
neighbor <x> fall-over bfd
```
**Reference**: RFC 5880 (BFD), RFC 5881 (BFD for IPv4/IPv6)

### 5. Authentication
Use TCP MD5 (`neighbor <x> password`) as a minimum. Prefer TCP-AO where supported.
Rotate keys on a schedule. Never run unauthenticated eBGP sessions.
**Reference**: RFC 5925 (TCP-AO), RFC 7454 §5

### 6. Graceful restart
Enable graceful restart to preserve forwarding state during BGP session resets:
```
bgp graceful-restart
```
Verify that both peers support it; mismatched GR capabilities cause unexpected behavior.
**Reference**: RFC 4724

### 7. Route dampening
Generally **discouraged** for modern eBGP deployments. Route dampening can suppress
legitimate prefixes and introduce reachability issues. If used, apply conservative
parameters only to specific problematic peers.
**Reference**: RIPE-580 — BGP Route Flap Damping

### 8. Logging
Always enable neighbor state change logging:
```
bgp log-neighbor-changes
```
This is on by default in modern IOS-XE but verify it has not been explicitly disabled.

### 9. TTL security / GTSM
For eBGP single-hop sessions, configure GTSM to reject packets with unexpected TTL values:
```
neighbor <x> ttl-security hops 1
```
This blocks remote spoofed BGP OPEN packets from non-adjacent sources.
**Reference**: RFC 5082

### 10. Communities
Use BGP communities to tag routes for policy decisions. Prefer large communities
(RFC 8092) for new deployments. Document community meanings in your CLAUDE.md or
operations wiki.
**Reference**: RFC 1997 (standard communities), RFC 8092 (large communities)

### 11. Default route origination
Never originate a default route without a route-map condition:
```
neighbor <x> default-originate route-map ADVERTISE-DEFAULT
```
The route-map should match a prefix or track an SLA object to prevent black-holing
traffic during upstream failures.
