---
name: Master's thesis project overview
description: What the 7_individaul_project directory is — FEM+GPR sensitivity study of coronary plaque rupture
type: project
originSessionId: c77eab40-493f-4340-9781-116415e346c5
---
Directory `/home/jeff/project/56_road_to_NV/7_individaul_project/` holds the user's master's thesis: "Global Sensitivity of Peak Plaque Stress to Morphology, Material, and Hemodynamics: a Three-Experiment FEM-GPR Study."

**Research question:** Is cap thickness alone enough to predict coronary plaque rupture (TCFA paradigm), or is cap stiffness an equal co-driver?

**Experiments:**
- ExperimentA: LAP baseline, 13 inputs (morph + material + hemo). E_fc dominates.
- ExperimentB / ExperimentB_2 / ExperimentB_3: Calcified plaque variants, up to 18 inputs.
- ExperimentC: Narrow cap-focused design, 4 inputs (fc_av_th, E_fc, SBP, PP). fc_av_th dominates, E_fc second, interaction S_2≈0.06.
- ExperimentD: Simple cap-thickness × stiffness sweep (exploratory).

**Pipeline per experiment:** Q0 distributions → Q1 Sobol → Q2 pairwise → Q3 group sensitivity → Q4 rupture location → Q5 reliability (PSS>170 kPa) → Q6 FFR redundancy → Q7–Q8 high/low PSS contrasts (Cliff's δ, Cohen's d, GPC classifiers).

**Central claim:** cap thickness and stiffness are coupled co-drivers → argues for dual imaging (OCT for thickness + elastography for stiffness + BP monitoring).

**Supporting files:** `journal/` has LaTeX manuscript in prep; `fcvm-13-1766059.pdf` is a Frontiers in Cardiovascular Medicine reference; `ExperimentA_strength_conversation_claude.txt` is a Korean advisor discussion on stress/strength normalization.

**Why:** User is writing this thesis toward journal submission (Journal of Biomechanics or Annals of Biomedical Engineering).

**How to apply:** When the user asks about any experiment folder, scripts, or plots, assume the above framing. Results labeled Q0–Q8 map to the pipeline steps above. When discussing findings, remember the broad-vs-narrow design split (A/B show stiffness dominance, C shows thickness dominance — this is a feature of the argument, not a contradiction).
