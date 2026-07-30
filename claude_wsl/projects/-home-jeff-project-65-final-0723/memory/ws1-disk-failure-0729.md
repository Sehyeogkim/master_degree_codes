---
name: ws1-disk-failure-0729
description: "ws1 root disk failed 2026-07-29 (read-only → I/O errors → sshd down); rescue partial, do not touch until sysadmin clears it"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7745583c-3bb8-4ce1-82e6-81ae89d07345
  modified: 2026-07-29T13:07:46.711Z
---

**2026-07-29 evening: ws1 (cvbml01) root disk `/dev/mapper/vgubuntu-root` failed.**
Sequence: ext4 `errors=remount-ro` triggered → writes blocked → **reads** started returning
`Input/output error` → binaries segfaulted one by one as the page cache drained
(`du`, `cp`, `tar`, `dd`, `uniq` died; `rsync`, `cat`, `ls`, `stat` survived) → sshd went
down (`Connection refused`, host still pings). Not a space problem: 236 GB free of 3.6 TB.

**`/mnt/hdd` (`/dev/sda1`, 15 TB, 27 % used) is a different physical disk and was healthy.**
The mesh independence study outputs live there (`/mnt/hdd/jeff/mesh_indep_solid/`) and are
expected to survive.

**Rescue progress before access was lost** (`→ /mnt/hdd/jeff/rescue_54_analysis/`):
`pre_data` + `ansys_CP_0728` complete; `ansys_LAP_0728` low vtk **215/215**; `LAP_mesh`
**212/475**; `solid_data` STP **436/476**, vtu 293. Read-error file list (6 778 entries) at
`/mnt/hdd/jeff/bad_files.txt`. Copied files were size-verified against source (0 mismatches),
so damaged files were skipped rather than silently corrupted.

**How to apply:** the user asked to **stop touching ws1** pending the sysadmin's check
(2026-07-30). Do not ssh, do not restart the rescue, until told. Ask the sysadmin for
`dmesg` + `smartctl` and to **image with ddrescue before any fsck** — fsck on failing media
can make things worse. Tell them a rescue is mid-flight so **do not power-cycle** unless
they intend to.

**Likely contributing factors** (not proven, needs smartctl): the root disk sat at 93–94 %
full for a long time, which on an SSD shrinks spare area and multiplies write amplification;
ANSYS out-of-core scratch writes tens of GB per solve and was pointed at the system disk.
Going forward: put ANSYS scratch and results on a data disk, keep the system disk under 80 %.
See [[solid-mesh-independence-0729]] and [[utils-bc-ws1-stale-trap]].
