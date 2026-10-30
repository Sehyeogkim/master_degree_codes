---
name: KAIST TERA Lab ANSYS install manual
description: Path to the lab's official ANSYS install manual PDF (Korean) — authoritative source for FTP/license server settings
type: reference
originSessionId: 0fbf1096-fa34-4e91-afbf-1f17f6f127b2
---
Path: `/home/jeff/project/58_ansys_install/2024_ANSYS 제품 설치 메뉴얼_URL 통합.pptx.pdf` (24 pages, Korean)

Author: 이정현 (junghyunlee@kaist.ac.kr), KAIST 전기및전자공학부, 김정호 교수 lab (TERA — TeraByte Interconnection and Package Laboratory).

Covers: ANSYS download via lab FTP, Fluid / Structural / Electromagnetics installation, license-overlap prevention, common license-error fixes (Pro/Premium/Enterprise toggle, legacy Electronics HPC license = False, hosts file, etc.).

To extract text: PDF reader requires poppler-utils (not installed, no sudo). Use `pymupdf` instead — already pip-installed in `/home/jeff/miniconda3`:
```python
import fitz
doc = fitz.open(path)
for p in doc: print(p.get_text())
```
