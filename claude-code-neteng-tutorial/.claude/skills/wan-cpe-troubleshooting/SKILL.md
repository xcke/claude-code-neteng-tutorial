---
name: "wan-cpe-troubleshooting"
description: "NOC runbook for troubleshooting Example Inc WAN CPE devices (ISR 4331, IOS-XE 17.9)."
---

## Environment

- **Platform**: Cisco ISR 4331
- **Software**: IOS-XE 17.9
- **WAN topology**: Hub-and-spoke DMVPN (NHRP over mGRE)
- **Primary uplink**: MPLS circuit with eBGP peering to provider (ASN 64999)
- **Backup uplink**: Broadband ISP with IPSec tunnel to hub
- **Failover**: IP SLA + track object, primary routes preferred via local-preference
- **Monitoring**: SNMP traps to LibreNMS, syslog to Graylog

## Troubleshooting workflow

Follow these steps in order. Stop when the root cause is identified and document findings.

### Step 1: Gather ticket context
- Read the ticket description, affected site code, and reported symptoms.
- Identify the device hostname from `devices.yml` or the CMDB.
- Note the time of the reported issue and any recent change windows.

### Step 2: Verify reachability
- Ping the device management IP and loopback0.
- If unreachable, check upstream devices and OOB (out-of-band) console access.
- Confirm the issue is not a monitoring false-positive (check LibreNMS alerts).

### Step 3: Check interfaces
```
show ip interface brief
show interface <wan-intf>
show interface <tunnel-intf>
```
- Look for: admin down, line protocol down, input/output errors, CRC errors, resets.
- Check for duplex mismatches or speed negotiation issues on physical interfaces.

### Step 4: Check routing and BGP
```
show ip route summary
show ip bgp summary
show ip bgp neighbor <peer-ip>
```
- Confirm BGP session is Established. If Idle/Active, check Step 5.
- Verify expected prefix count from provider. Compare against maximum-prefix limit.
- Check for missing routes to critical subnets (data center, DNS, etc.).

### Step 5: Check DMVPN and IPSec
```
show dmvpn
show crypto ipsec sa
show crypto isakmp sa
```
- DMVPN tunnel should show NHRP state as UP with correct NBMA addresses.
- IPSec SAs should show non-zero encaps/decaps counters (traffic flowing).
- If IPSec SA shows zero counters, check for ACL mismatches or NAT issues.

### Step 6: Check ISP circuit
```
show interface <wan-intf> | include rate
show ip sla statistics
```
- Compare actual throughput against circuit capacity.
- Check IP SLA probes — if the primary SLA is failing, failover should be active.
- Contact ISP NOC if physical layer errors or sustained packet loss are present.

### Step 7: Check failover state
```
show track
show ip route 0.0.0.0
show route-map PREFER-PRIMARY
```
- Determine whether the device is on primary (MPLS) or backup (broadband) path.
- If on backup, verify the primary SLA is genuinely failing before escalating.
- Check local-preference values to confirm correct path selection.

### Step 8: Check performance
```
show processes cpu sorted | head 20
show memory statistics
show platform hardware throughput level
```
- CPU above 80% sustained may indicate a control plane issue (route churn, SYN flood).
- Memory pressure may cause BGP session resets or DMVPN instability.

### Step 9: Document and escalate
- Summarize findings: root cause, affected services, current state.
- If hardware failure is suspected, open a Cisco TAC case with `show tech-support`.
- If ISP issue, open a ticket with the carrier and include traceroute output.
- Update the incident ticket with timeline and actions taken.

### Step 10: Verify resolution
- Confirm BGP session is Established and prefix counts are normal.
- Confirm DMVPN tunnels are UP with traffic flowing.
- Confirm IP SLA probes are passing and failover state is correct.
- Monitor for 15 minutes before closing the ticket.

## Appendix: common failure scenarios

### BGP stuck in Active state
- **Cause**: TCP session cannot establish. Usually ACL blocking TCP/179, MD5 mismatch,
  or ISP-side issue.
- **Quick check**: `show ip bgp neighbor <peer> | include state|last reset`
- **Fix**: Verify ACLs, check MD5 password, confirm ISP peer is configured.

### DMVPN tunnel flapping
- **Cause**: Unstable underlay (ISP packet loss), MTU issues (usually needs
  `ip tcp adjust-mss 1360`), or NHRP registration failures.
- **Quick check**: `show dmvpn | include Attrb` — look for state cycling.
- **Fix**: Check MTU end-to-end, verify NHRP authentication keys, check underlay stability.

### Asymmetric routing after failover
- **Cause**: Primary came back but not all routes reconverged. Often a local-preference
  or weight mismatch between primary and backup paths.
- **Quick check**: `show ip bgp <prefix>` — compare paths and attributes.
- **Fix**: Clear soft inbound on the BGP session, verify route-map applies correct
  local-preference on primary path.
