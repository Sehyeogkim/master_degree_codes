---
name: ANSYS license server (Etri-pc)
description: FlexNet license server config for ANSYS 2025 R1 — host, port, env var, and known-good license string format
type: reference
originSessionId: cd230770-599c-42d2-99a6-836f6ca70c4f
---
ANSYS uses a FlexNet license server hosted on the KAIST network.

- **Host**: `Etri-pc` (alias) / `143.248.174.50`
- **Port**: `1055`
- **License string**: `1055@Etri-pc` (preferred) or `1055@143.248.174.50`
- **Env var for PyMAPDL / standalone clients**: `ANSYSLMD_LICENSE_FILE=1055@Etri-pc`
- **Server-side license file path** (on Etri-pc): `/ansys_inc/shared_files/licensing/license_files/ansyslmd.lic`
- **Server vendor daemon**: `ansyslmd`, FlexNet v11.17.2

**Hosts entry already added on this WSL** (verified via `ping Etri-pc` → 143.248.174.50). On WSL2, /etc/hosts is regenerated from the Windows hosts file each boot, so the source-of-truth entry lives in `C:\Windows\System32\drivers\etc\hosts`.

**Network requirement**: must be on KAIST internal network or VPN to reach Etri-pc.

**Troubleshooting**: if checkout fails, verify firewall allows port 1055 and the vendor daemon port (random unless pinned in the .lic file), then `ping Etri-pc` to confirm name resolution.
