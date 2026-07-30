---
name: ANSYS Linux install (planned)
description: User plans to install ANSYS on Linux; should reference the KAIST TERA Lab install manual PDF for server/license info
type: project
originSessionId: 0fbf1096-fa34-4e91-afbf-1f17f6f127b2
---
User intends to install ANSYS on Linux. The lab's official install manual (`/home/jeff/project/58_ansys_install/2024_ANSYS 제품 설치 메뉴얼_URL 통합.pptx.pdf`) covers Windows but contains the lab-specific FTP and license server details that still apply on Linux:

- FTP for installers: `143.248.174.154:21`, ID/PW `kaist_ansys` / `kaist_ansys` (KAIST-only, do not share externally)
- License server: `143.248.174.50`, ports `2325`, `1055`
- For Electromagnetics: TCP/IP option must be unchecked
- License-overlap rule: open new projects via File → Open inside a single running instance, never launch a second instance

**Why:** User explicitly asked me to keep this in mind for the upcoming Linux install and to reference the PDF.
**How to apply:** When the user starts the Linux install, read the PDF (use `pymupdf` / `python -c "import fitz; ..."` since `poppler-utils` isn't installed and sudo isn't available) and translate the Windows steps to Linux equivalents. Lab-specific server addresses and license rules carry over directly; the GUI/installer steps will differ on Linux.
