---
name: PyMAPDL on WSL2 — must pass ip="127.0.0.1"
description: PyMAPDL launch_mapdl auto-detects the WSL2 gateway IP (172.x.x.1) instead of a bindable Linux IP, causing false "Port already in use" errors. Always pass ip="127.0.0.1" on WSL2.
type: feedback
originSessionId: cd230770-599c-42d2-99a6-836f6ca70c4f
---
When calling `pymapdl.launch_mapdl(...)` from WSL2, **always pass `ip="127.0.0.1"`** explicitly. Otherwise PyMAPDL's port validator (`_validate_port_availability` → `check_port_status` → `_check_port_socket`) tries to `socket.bind()` on the WSL2 gateway address (e.g. `172.20.224.1`), which isn't owned by Linux. The bind fails, so PyMAPDL reports `"Port 50052 is already in use by another process"` even though every port is free.

**Why:** Confirmed empirically on 2026-05-07 — pymapdl 0.73.0 on WSL2 Ubuntu (kernel 5.15-microsoft-standard). `socket.bind(("127.0.0.1", 50052))` works; `socket.bind(("172.20.224.1", 50052))` fails with `EADDRNOTAVAIL`. The validator's `bind()` failure is misinterpreted as "port in use" rather than "IP not bindable." Direct `check_port_status(port, "127.0.0.1")` returns `available=True`; pymapdl just calls it with the wrong host.

**How to apply:** Whenever editing or writing a `launch_mapdl()` call on the local WSL2 machine, include `ip="127.0.0.1"`. On native Linux workstations (cvbml01/02) and Harvey this is unnecessary — pymapdl auto-detection works there. The fix doesn't hurt to include unconditionally.

**File where this is set for the project:** `/home/jeff/project/58_ansys_install/pymapdl_simulation_ver5_fibrous.py` line ~57 in `pymapdl_launch()`.
