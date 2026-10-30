---
name: 54_analysis ANSYS sim variants of interest
description: On ws2 (cvbml02), under ~/project/54_analysis/solid_data/case_*, only analyze ansys_results_type1 and ansys_results_type1_expB
type: project
originSessionId: df786f55-d131-4e24-98a3-f82ad2d94466
---
When working on `~/project/54_analysis/` on ws2 (cvbml02 / cvbml02.kaist.ac.kr), the user only cares about two ANSYS sim result variants per case dir:

- `ansys_results_type1`
- `ansys_results_type1_expB`

Other variants present in case dirs (`ansys_results_type1_expB_new`, `ansys_results_type2_expB_new`, `ansys_ver5_0430`) should be ignored unless the user says otherwise.

**Why:** User stated this directly when scoping the analysis work for 54_analysis.

**How to apply:** When writing scripts, post-processing, or summaries that iterate over case dirs, restrict to these two subdirs. Don't surface or aggregate the other variants by default. Case dirs run `case_500` through `case_999` (500 total), though not every case has every variant (e.g., `case_999` is missing the `_new` and `ansys_ver5_0430` ones).
