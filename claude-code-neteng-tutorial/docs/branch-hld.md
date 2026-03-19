# [EXAMPLE ONLY]Branch Office High-Level Design — Austin, TX

**Document ID:** HLD-BRANCH-AUS-001
**Revision:** 0.1 (Draft)
**Author:** Network Engineering Team
**Date:** 2026-03-19
**Status:** Draft — Pending Stakeholder Review

---

## 1. Executive Summary

This document describes the high-level network design for a new branch office supporting approximately 200 users across four departments: Engineering, Sales, HR, and Guest. The site will connect back to the Dallas headquarters via an SD-WAN overlay running across dual ISP uplinks with automatic failover. The design prioritizes VLAN segmentation, PCI-DSS compliance for the Sales department (credit card processing), cost-effective hardware selection, and full wireless coverage throughout the facility.

---

## 2. Topology Overview

### 2.1 Physical Topology

The branch site uses a collapsed-core design appropriate for a ~200-user office. A single router/firewall appliance serves as the WAN edge, default gateway, and inter-VLAN routing engine. Two access-layer switches provide wired connectivity to all end devices, with uplinks aggregated to the router/firewall via a port-channel. Wireless access points connect to the access switches and are centrally managed via Meraki cloud dashboard.

```
                        ┌──────────────┐
           ISP-A (1G)   │              │  ISP-B (500M)
        ────────────────▶│  MX85        │◀────────────────
        (AT&T Fiber)     │  Router/FW   │  (Spectrum Cable)
                        │  SD-WAN Head │
                        └──────┬───────┘
                               │
                          Po1 (2x 1G LAG)
                               │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────┴─────┐         ┌─────┴─────┐
              │  MS225-48  │         │  MS225-48  │
              │  SW-AUS-01 │         │  SW-AUS-02 │
              │  (IDF-A)   │         │  (IDF-B)   │
              └─────┬──────┘         └──────┬─────┘
                    │                       │
        ┌───────┬───┴───┬──────┐   ┌───────┼───────┬──────┐
        │       │       │      │   │       │       │      │
       AP1     AP2     AP3   Wired AP4    AP5     AP6   Wired
      (MR46)  (MR46) (MR46) Ports (MR46) (MR46) (MR46) Ports
```

### 2.2 Logical Topology

All inter-VLAN routing is handled by the MX85 firewall appliance. Each department is assigned a dedicated VLAN and /24 subnet. Trunk links carry all VLANs from the access switches to the MX85. The Sales VLAN is isolated at Layer 3 with strict ACLs to satisfy PCI-DSS requirements. Guest traffic is tunneled directly to the firewall and NATed to the internet without access to internal VLANs.

---

## 3. VLAN Plan

### 3.1 VLAN Assignments

| VLAN ID | Name           | Subnet            | Usable Range            | Gateway         | Purpose                        |
|---------|----------------|--------------------|------------------------|-----------------|--------------------------------|
| 10      | MGMT           | 10.44.10.0/24      | 10.44.10.1–10.44.10.254 | 10.44.10.1      | Network infrastructure mgmt    |
| 20      | ENGINEERING    | 10.44.20.0/24      | 10.44.20.1–10.44.20.254 | 10.44.20.1      | Engineering workstations       |
| 30      | SALES          | 10.44.30.0/24      | 10.44.30.1–10.44.30.254 | 10.44.30.1      | Sales (PCI-DSS scope)          |
| 40      | HR             | 10.44.40.0/24      | 10.44.40.1–10.44.40.254 | 10.44.40.1      | Human Resources                |
| 50      | GUEST          | 10.44.50.0/24      | 10.44.50.1–10.44.50.254 | 10.44.50.1      | Guest/visitor wireless         |
| 99      | NATIVE         | —                  | —                       | —               | Native VLAN (untagged, unused) |

**Note:** The 10.44.x.0/24 scheme uses `44` as the site identifier for Austin. Dallas HQ uses `10.10.x.0/24`. This keeps the addressing predictable across the SD-WAN fabric and simplifies summarization.

### 3.2 DHCP Scopes

DHCP is served by the MX85 appliance for all user VLANs. The management VLAN uses static assignments for infrastructure devices.

| VLAN | DHCP Pool Range          | Exclusions (Static)      | Lease Time | DNS Servers              |
|------|--------------------------|--------------------------|------------|--------------------------|
| 20   | 10.44.20.100–10.44.20.240 | 10.44.20.1–10.44.20.99  | 8 hours    | 10.10.1.53, 10.10.1.54  |
| 30   | 10.44.30.100–10.44.30.200 | 10.44.30.1–10.44.30.99  | 8 hours    | 10.10.1.53, 10.10.1.54  |
| 40   | 10.44.40.100–10.44.40.200 | 10.44.40.1–10.44.40.99  | 8 hours    | 10.10.1.53, 10.10.1.54  |
| 50   | 10.44.50.10–10.44.50.240  | 10.44.50.1–10.44.50.9   | 2 hours    | 8.8.8.8, 8.8.4.4        |

**Design decisions:**
- Engineering gets a wider DHCP pool (141 addresses) to accommodate developer workstations, test devices, and lab equipment.
- Sales pool is deliberately smaller (101 addresses) to limit PCI-DSS scope.
- Guest VLAN uses public DNS resolvers and a shorter lease to reclaim addresses quickly.
- All corporate VLANs point to the Dallas HQ DNS servers (10.10.1.53/54) over the SD-WAN tunnel.

### 3.3 Department-to-VLAN User Mapping

| Department  | Estimated Users | VLAN | Wired Ports Needed | Wireless Devices |
|-------------|----------------|------|--------------------|--------------------|
| Engineering | 80             | 20   | 80                 | ~40 (laptops)      |
| Sales       | 60             | 30   | 40                 | ~60 (laptops/tablets) |
| HR          | 40             | 40   | 30                 | ~20                |
| Guest       | 20 (peak)      | 50   | 0                  | ~20                |
| **Total**   | **200**        |      | **150**            | **~140**           |

---

## 4. Hardware Bill of Materials

### 4.1 Network Equipment

| Qty | Model              | Role                    | Key Specs                                          | Est. Unit Cost | Est. Total  |
|-----|--------------------|-------------------------|----------------------------------------------------|----------------|-------------|
| 1   | Cisco Meraki MX85  | Router / Firewall / SD-WAN | 1 Gbps FW throughput, 500 Mbps VPN, 2x WAN, 10x LAN | $3,200         | $3,200      |
| 2   | Cisco Meraki MS225-48FP | Access Switch          | 48x 1GbE PoE+ ports, 4x 10G SFP+ uplinks, 740W PoE budget | $5,800 | $11,600     |
| 6   | Cisco Meraki MR46  | Wireless AP (Wi-Fi 6)  | 2x2:2 + 2x2:2 MIMO, 1.7 Gbps aggregate, 802.3at PoE | $750           | $4,500      |
| 2   | Cisco SFP-10G-SR   | 10G SFP+ optics        | For switch-to-MX uplinks (if using 10G)            | $150           | $300        |
| 1   | APC SMT1500RM2UC   | UPS                     | 1500VA / 1000W, 2U rackmount, network card         | $1,200         | $1,200      |
| 1   | 12U wall-mount rack | Data closet enclosure  | With cable management, PDU, fans                    | $600           | $600        |

**Subtotal (hardware):** ~$21,400

### 4.2 Licensing

| Item                          | Term    | Est. Annual Cost |
|-------------------------------|---------|------------------|
| Meraki MX85 Enterprise License | 3 year  | $1,100/yr        |
| Meraki MS225-48FP License (x2) | 3 year  | $900/yr each     |
| Meraki MR46 License (x6)      | 3 year  | $200/yr each     |
| **Total Licensing**           | **3 yr** | **$4,100/yr**   |

### 4.3 Model Selection Rationale

**Why Meraki over Catalyst:**
- Single-pane-of-glass management from Meraki Dashboard reduces need for on-site network staff at the branch.
- Built-in SD-WAN (Auto VPN) simplifies tunnel provisioning back to Dallas HQ.
- Integrated DHCP, firewall, and content filtering on the MX85 eliminates the need for separate appliances.
- Cloud-managed firmware updates align with the lean IT operations model for branch sites.

**Why MX85 specifically:**
- The MX85 supports up to 1 Gbps firewall throughput, which matches the primary ISP link.
- 500 Mbps site-to-site VPN throughput is adequate for the branch-to-HQ traffic profile.
- If VPN throughput requirements grow beyond 500 Mbps, the MX95 ($5,400) is the next step up.

**Why MS225-48FP:**
- Full PoE+ (740W budget) supports all 6 APs per switch without a power concern. Each MR46 draws ~25W under load, so 6 APs = 150W — well within budget of a single switch.
- 48 ports per switch provides 96 total wired ports. With 150 wired ports needed, some users will be wireless-primary (especially Sales and Guest). If wired port demand exceeds 96, a third MS225-48 can be added.
- 4x 10G SFP+ uplinks future-proof the switch stack for higher-bandwidth uplinks.

**Alternative (budget fallback):** If Meraki licensing costs are prohibitive, Catalyst 1300-48FP-4X switches ($2,200 each) with a Catalyst 8200 Series edge router could be substituted. This trades cloud management simplicity for lower annual OpEx but requires more hands-on CLI configuration.

---

## 5. WAN Architecture

### 5.1 Dual ISP Design

| ISP      | Circuit Type | Bandwidth   | SLA     | Handoff         | MX85 Port |
|----------|-------------|-------------|---------|-----------------|-----------|
| AT&T     | Dedicated fiber | 1 Gbps DIA | 99.95%  | Single-mode fiber, 1G-LX | WAN 1     |
| Spectrum | Business cable  | 500 Mbps   | 99.9%   | RJ45 handoff from modem  | WAN 2     |

### 5.2 Failover Behavior

The MX85 is configured for **active/passive WAN failover** with the following logic:

1. **Primary path:** All traffic egresses via WAN 1 (AT&T 1 Gbps).
2. **Health probes:** The MX85 sends ICMP probes to multiple upstream targets (8.8.8.8, 1.1.1.1, and the AT&T gateway) every 5 seconds.
3. **Failover trigger:** If 5 consecutive probes fail on WAN 1 (25 seconds), the MX85 shifts all traffic to WAN 2 (Spectrum 500 Mbps).
4. **Failback:** When WAN 1 recovers and passes 10 consecutive health checks (50 seconds), traffic shifts back to WAN 1.
5. **SD-WAN tunnels:** Auto VPN tunnels are established over both WAN links simultaneously. The Meraki fabric handles tunnel failover independently of internet failover, typically completing in under 1 second.

**Traffic shaping on failover:** When operating on the 500 Mbps backup link, the MX applies a traffic shaping policy that prioritizes:
1. Voice/video (DSCP EF/AF41) — guaranteed 100 Mbps
2. SD-WAN tunnel to Dallas (business applications) — guaranteed 200 Mbps
3. Internet breakout — best effort on remaining bandwidth

### 5.3 SD-WAN Overlay

| Parameter              | Value                                         |
|------------------------|-----------------------------------------------|
| SD-WAN Platform        | Meraki Auto VPN (built into MX firmware)      |
| Tunnel Type            | IPsec (AES-256-CBC, SHA-256, DH Group 14)    |
| Hub Site               | Dallas HQ — MX250 (or existing hub appliance) |
| Topology               | Hub-and-spoke (Austin spoke to Dallas hub)    |
| Full Tunnel            | No — split tunnel with internet local breakout |
| Applications via tunnel | ERP (SAP), file shares, Active Directory, DNS, internal apps |
| Local breakout         | SaaS (M365, Salesforce, Zoom), general web    |

**Split tunnel rationale:** Backhauling all internet traffic to Dallas would saturate the VPN capacity. SaaS applications perform better with direct internet access from the branch. The MX85's Layer 7 application awareness steers traffic per application.

### 5.4 Routing

- The MX85 advertises the branch summary route `10.44.0.0/16` to Dallas over the Auto VPN tunnel.
- Dallas advertises `10.10.0.0/16` (HQ supernet) and `10.0.0.0/8` (catch-all for other branches) to Austin.
- No dynamic routing protocol is needed at the branch — the MX85 handles route exchange natively via the Meraki VPN fabric.
- Default route points to the active WAN uplink for internet-bound traffic.

---

## 6. Security Posture

### 6.1 Firewall Zones

The MX85 operates in routed mode with the following logical zones:

| Zone       | VLANs      | Trust Level | Notes                             |
|------------|------------|-------------|-----------------------------------|
| CORPORATE  | 10, 20, 40 | High        | Full inter-zone access (with ACLs)|
| PCI        | 30         | Restricted  | Isolated; controlled egress only  |
| GUEST      | 50         | Untrusted   | Internet-only, no internal access |
| WAN        | —          | External    | Untrusted; all inbound denied     |

### 6.2 Inter-VLAN Access Control Policy

| Source VLAN    | Destination VLAN | Action | Notes                                          |
|----------------|------------------|--------|-------------------------------------------------|
| 20 (Eng)       | 40 (HR)          | Permit | General corporate inter-department access       |
| 40 (HR)        | 20 (Eng)         | Permit | Bidirectional corporate access                  |
| 20 (Eng)       | 30 (Sales)       | Deny   | PCI-DSS isolation — no direct access            |
| 40 (HR)        | 30 (Sales)       | Deny   | PCI-DSS isolation — no direct access            |
| 30 (Sales)     | 20 (Eng)         | Deny   | PCI-DSS isolation — no lateral movement         |
| 30 (Sales)     | 40 (HR)          | Deny   | PCI-DSS isolation — no lateral movement         |
| 30 (Sales)     | 10 (Mgmt)        | Deny   | PCI-DSS — Sales cannot reach infrastructure     |
| 30 (Sales)     | SD-WAN Tunnel    | Permit | Sales needs ERP and payment gateway at HQ       |
| 30 (Sales)     | Internet         | Permit | Restricted to HTTPS (443) and DNS (53) only     |
| 50 (Guest)     | Any Internal     | Deny   | Complete guest isolation                        |
| 50 (Guest)     | Internet         | Permit | HTTP/HTTPS/DNS only; bandwidth capped at 25 Mbps |
| 10 (Mgmt)      | All              | Permit | Infrastructure management access everywhere     |
| Any            | 10 (Mgmt)        | Deny   | Only MGMT-initiated flows reach infrastructure  |

### 6.3 PCI-DSS Compliance Controls (Sales VLAN 30)

PCI-DSS v4.0 requires network segmentation to reduce the cardholder data environment (CDE) scope. The following controls apply specifically to VLAN 30:

1. **Network segmentation:** VLAN 30 is isolated from all other internal VLANs via Layer 3 ACLs on the MX85. No east-west traffic is permitted to or from the Sales VLAN except to the SD-WAN tunnel (for payment gateway access at HQ).

2. **Egress filtering:** Sales VLAN internet access is restricted to TCP/443 (HTTPS) and UDP/53 (DNS). All other outbound ports are blocked. This prevents data exfiltration over non-standard protocols.

3. **Content filtering:** The MX85's content filtering is enabled for VLAN 30, blocking categories including malware, P2P, anonymizers, and adult content.

4. **Intrusion detection:** Meraki Advanced Security license enables IDS/IPS on the MX85. Signatures are applied to traffic entering and leaving VLAN 30.

5. **Logging:** All traffic to/from VLAN 30 is logged to the Meraki dashboard with a 12-month retention policy. Syslog forwarding to the Dallas SIEM (Splunk) is configured for real-time alerting.

6. **Wireless isolation:** The Sales SSID maps exclusively to VLAN 30. Client isolation is enabled so Sales wireless devices cannot communicate with each other directly over the air — all traffic is forced through the MX85 for inspection.

7. **Port security:** Switch ports in the Sales area are configured with 802.1X authentication via Meraki RADIUS proxy to the Dallas AD/NPS server. Unauthenticated devices are placed into a quarantine VLAN (VLAN 99).

**QSA Note:** This design reduces the PCI scope to VLAN 30 endpoints, the MX85 firewall, and the switch ports carrying VLAN 30. The QSA should confirm that the segmentation testing (penetration test across VLAN boundaries) validates this scope reduction.

### 6.4 Guest Network Controls

- Captive portal with Terms of Service acceptance (Meraki built-in splash page).
- Bandwidth limit: 25 Mbps aggregate for the entire Guest VLAN (configured as traffic shaping on MX85).
- Per-client limit: 10 Mbps down / 5 Mbps up.
- Client isolation enabled — guests cannot see or communicate with other guests.
- DNS filtering via Cisco Umbrella integration to block malicious domains.
- Session timeout: 8 hours, then re-authentication required.

---

## 7. Wireless Design

### 7.1 SSID Configuration

| SSID Name           | VLAN | Auth Method        | Band     | Hidden | Notes                          |
|---------------------|------|--------------------|----------|--------|--------------------------------|
| ACME-CORP           | 20   | WPA3-Enterprise (802.1X) | 5 GHz preferred | No  | Engineering, HR default SSID  |
| ACME-SALES          | 30   | WPA3-Enterprise (802.1X) | 5 GHz preferred | No  | Sales only — PCI scope        |
| ACME-GUEST          | 50   | Open + Captive Portal | 2.4 + 5 GHz | No  | Visitor access                 |
| ACME-MGMT           | 10   | WPA3-Personal (PSK) | 5 GHz only | Yes | Infrastructure devices only    |

**SSID-to-VLAN detail:**
- `ACME-CORP` authenticates users via 802.1X against the Dallas AD/NPS server. RADIUS attributes dynamically assign users to VLAN 20 (Engineering) or VLAN 40 (HR) based on AD group membership. This is handled via Meraki RADIUS policy with VLAN override.
- `ACME-SALES` is a dedicated SSID for the Sales department to maintain PCI-DSS segmentation. The separate SSID ensures that Sales traffic is always tagged to VLAN 30 regardless of RADIUS attribute behavior.
- `ACME-GUEST` uses an open association with a Meraki splash page for Terms of Service acceptance.
- `ACME-MGMT` is hidden and uses a strong PSK rotated quarterly. Used only for out-of-band management of APs and other infrastructure.

### 7.2 AP Placement Guidance

The facility is assumed to be a single-floor office of approximately 15,000 sq ft (typical for 200 users). Six MR46 APs provide adequate coverage:

| AP ID | Location                  | Coverage Area        | Primary VLANs Served   | Switch Port     |
|-------|---------------------------|----------------------|------------------------|-----------------|
| AP-01 | Engineering — open floor  | Eng desks, east wing | 20 (Eng)               | SW-AUS-01 Gi1/1 |
| AP-02 | Engineering — lab area    | Lab / dev space      | 20 (Eng)               | SW-AUS-01 Gi1/2 |
| AP-03 | Sales bullpen             | Sales desks          | 30 (Sales)             | SW-AUS-01 Gi1/3 |
| AP-04 | HR / executive area       | HR offices, conf rooms | 40 (HR)              | SW-AUS-02 Gi1/1 |
| AP-05 | Common area / lobby       | Lobby, break room    | 50 (Guest), 20 (Eng)  | SW-AUS-02 Gi1/2 |
| AP-06 | Conference room wing      | Large conf rooms     | 20 (Eng), 50 (Guest)  | SW-AUS-02 Gi1/3 |

**Placement notes:**
- Target cell overlap: 15-20% between adjacent APs for seamless roaming.
- Mount APs on ceiling tiles at approximately 10 ft height, centered in their coverage zones.
- Channel plan: Use auto-channel on the Meraki dashboard for initial deployment, then tune manually if co-channel interference is observed. Prefer 5 GHz channels (36, 40, 44, 48, 149, 153, 157, 161) with 40 MHz channel width.
- 2.4 GHz is enabled only for the Guest SSID to support IoT and older devices. Corporate SSIDs prefer 5 GHz via band steering.
- A formal predictive site survey should be conducted before AP installation to validate placement against the actual floor plan and construction materials.

### 7.3 Roaming and Performance

- 802.11r (Fast BSS Transition) is enabled on all corporate SSIDs for sub-50ms roaming.
- 802.11k (Neighbor Reports) and 802.11v (BSS Transition Management) are enabled to assist clients in making intelligent roaming decisions.
- Minimum data rate set to 12 Mbps on 2.4 GHz and 24 Mbps on 5 GHz to discourage clients from clinging to distant APs at low rates.

---

## 8. IP Addressing Scheme

### 8.1 Branch Site Summary

| Allocation             | Network           | Size  | Purpose                     |
|------------------------|-------------------|-------|-----------------------------|
| Branch supernet        | 10.44.0.0/16      | /16   | Entire Austin branch        |
| Management             | 10.44.10.0/24     | /24   | Infrastructure management   |
| Engineering            | 10.44.20.0/24     | /24   | Engineering endpoints       |
| Sales (PCI)            | 10.44.30.0/24     | /24   | Sales — PCI-DSS scope       |
| HR                     | 10.44.40.0/24     | /24   | HR endpoints                |
| Guest                  | 10.44.50.0/24     | /24   | Guest / visitor WiFi        |
| WAN link — ISP A       | DHCP from ISP     | /30   | AT&T handoff                |
| WAN link — ISP B       | DHCP from ISP     | /30   | Spectrum handoff            |
| SD-WAN tunnel          | Auto (169.254.x.x)| /30   | Meraki Auto VPN tunnel IPs  |

### 8.2 Static IP Assignments (VLAN 10 — Management)

| IP Address     | Hostname       | Device              | Notes                     |
|----------------|----------------|----------------------|---------------------------|
| 10.44.10.1     | gw-aus-01      | Meraki MX85          | Default gateway, DHCP     |
| 10.44.10.2     | sw-aus-01      | MS225-48FP #1        | IDF-A access switch       |
| 10.44.10.3     | sw-aus-02      | MS225-48FP #2        | IDF-B access switch       |
| 10.44.10.11    | ap-aus-01      | MR46 #1              | Engineering east          |
| 10.44.10.12    | ap-aus-02      | MR46 #2              | Engineering lab           |
| 10.44.10.13    | ap-aus-03      | MR46 #3              | Sales bullpen             |
| 10.44.10.14    | ap-aus-04      | MR46 #4              | HR / executive            |
| 10.44.10.15    | ap-aus-05      | MR46 #5              | Common area / lobby       |
| 10.44.10.16    | ap-aus-06      | MR46 #6              | Conference room wing      |
| 10.44.10.50    | ups-aus-01     | APC SMT1500RM2UC     | UPS network management card |

---

## 9. Physical Infrastructure

### 9.1 Data Closet Requirements

- **Rack:** 12U wall-mount enclosed rack with locking front door and ventilated sides.
- **Power:** Two dedicated 20A circuits (NEMA 5-20R) on separate breakers for redundancy. One circuit feeds the UPS; the second is a bypass for non-critical equipment.
- **UPS:** APC SMT1500RM2UC provides approximately 20 minutes of runtime for the MX85, both switches, and all APs at full PoE load (~800W total draw). This allows for a clean shutdown or ride-through of brief outages.
- **Cooling:** Data closet must maintain ambient temperature below 80F (27C). A dedicated mini-split or supplemental vent from the building HVAC is recommended.
- **Cable management:** Horizontal cable managers between each 1U device. Vertical cable managers on rack sides.
- **Grounding:** Rack bonded to building ground per TIA-607-C.

### 9.2 Cabling

| Run Type           | Cable Spec      | Count | Notes                                    |
|--------------------|-----------------|-------|------------------------------------------|
| Workstation drops  | Cat 6A (plenum) | 150   | Two drops per desk where possible        |
| AP drops           | Cat 6A (plenum) | 6     | Ceiling-mounted, PoE capable             |
| Switch uplinks     | OM4 multimode or Cat 6A | 4 | Between closet devices (short run)  |
| ISP A handoff      | Single-mode fiber | 1   | From demarc to MX85 WAN 1               |
| ISP B handoff      | Cat 6A          | 1     | From cable modem to MX85 WAN 2          |

---

## 10. Monitoring and Management

- **Dashboard:** All Meraki devices managed via the Meraki cloud dashboard (dashboard.meraki.com). Network-wide alerts configured for device offline, WAN failover events, and PoE budget warnings.
- **SNMP:** SNMPv3 enabled on all devices, polling from the Dallas monitoring stack (LibreNMS or equivalent) over the SD-WAN tunnel.
- **Syslog:** All devices forward syslog to the Dallas SIEM (10.10.1.100, UDP/514) over the SD-WAN tunnel for centralized logging and security alerting.
- **Firmware:** Meraki firmware updates are scheduled for the maintenance window (Sunday 02:00–06:00 local time) via the dashboard's staged rollout feature.
- **Alerting thresholds:**
  - WAN link utilization > 80% sustained for 15 minutes
  - AP client count > 50 per radio
  - PoE budget utilization > 85%
  - VPN tunnel down > 30 seconds

---

## 11. Open Questions

The following items require stakeholder input or further investigation before this design can be finalized:

| # | Question | Owner | Impact |
|---|----------|-------|--------|
| 1 | What is the exact floor plan and square footage? AP placement is estimated and requires a predictive site survey. | Facilities / Network Eng | Wireless coverage accuracy |
| 2 | Does the Sales team process credit card transactions locally or via a hosted/cloud payment gateway? This affects PCI-DSS scope significantly. | Sales Ops / Compliance | PCI scope and firewall rules |
| 3 | Are there any VoIP phones at this branch? If so, a dedicated Voice VLAN (e.g., VLAN 60) with QoS markings will need to be added. | IT / Telecom | VLAN plan, PoE budget, QoS |
| 4 | What is the expected growth rate? If headcount exceeds 250 within 2 years, a third access switch and additional APs should be planned now. | HR / Finance | BOM and budget |
| 5 | Is there an existing Meraki organization/dashboard, or does a new one need to be provisioned? Licensing should be co-termed if possible. | IT Operations | Licensing strategy |
| 6 | Does Dallas HQ already run a Meraki MX as the VPN hub, or will a hub-side appliance need to be added/upgraded? | Network Eng (Dallas) | SD-WAN tunnel compatibility |
| 7 | What is the building's available ISP demarc location relative to the data closet? Long fiber/cable runs may require additional conduit or a demarc extension. | Facilities / ISP | Cabling scope and cost |
| 8 | Is 802.1X/RADIUS infrastructure already deployed at HQ (NPS, ClearPass, ISE)? If not, the wireless auth design will need to fall back to WPA3-Personal with PSK. | Security / IAM | Wireless authentication |
| 9 | Are there any printers, security cameras, or IoT devices that need wired or wireless connectivity? These may require an additional IoT VLAN. | Facilities / IT | VLAN plan, port allocation |
| 10 | What is the approved budget ceiling? The current BOM is ~$21,400 hardware + ~$12,300 (3-year licensing). If this exceeds budget, the Catalyst fallback option should be evaluated. | Finance / IT Director | Hardware selection |

---

## Appendix A — Revision History

| Rev  | Date       | Author              | Changes                    |
|------|------------|----------------------|----------------------------|
| 0.1  | 2026-03-19 | Network Engineering  | Initial draft              |

---

## Appendix B — Reference Documents

- Cisco Meraki MX85 Datasheet
- Cisco Meraki MS225-48FP Datasheet
- Cisco Meraki MR46 Datasheet
- PCI-DSS v4.0 — Requirement 1 (Network Segmentation)
- TIA-942 — Data Center Cabling Standard
- IEEE 802.11ax (Wi-Fi 6) Specification
- Company SD-WAN Policy — WAN-POL-003
