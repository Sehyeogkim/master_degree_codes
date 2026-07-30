---
name: paperflow-mvp
description: PaperFlow = Manuscript Compiler product; MVP v0 built as standalone Next.js app (NOT on figureai)
metadata: 
  node_type: memory
  type: project
  originSessionId: 62f21681-6096-43ce-b57e-27cf1bce7ba8
---

PaperFlow is Jeff's product: a **Manuscript Compiler** (not a "writing tool") — structures research info, detects what's missing, enforces Claim→Contract→Validator, never fabricates absent experiments/numbers/citations. Design baseline = Notion "PaperFlow 설계 v2" page (id 3872a46dc68c811aa493ea43ec3ca113).

The codebase lives **outside** jeff_soul, at `/home/jeff/project/3_journal_template/paperflow/` (own CLAUDE.md, branch `masther_thesis`). `master_thesis/` there is a completed thesis used as the validation answer key (`contents/ch4_result.md` — never fed into generation).

**MVP v0 (built 2026-06-23):** standalone Next.js 14 + TypeScript app at `paperflow/paperflow-app/`. CLI + web API share `lib/core/` pipeline. Provider = OpenAI (gpt-4o / gpt-4o-mini) + Gemini for images; switchable via `PAPERFLOW_*` env. Run: `npm run cli -- run ../master_thesis --section result`. Build report = child page under the v2 design page.

**Why (decisions Jeff made):** (1) deliver as localhost Next.js that promotes to web later; (2) **build fresh — explicitly NOT reusing the figureai project's stack/code**, even though figureai is a working Next.js app; (3) include figures (matplotlib data plots from real `data/` + Gemini schematics).

**Key MVP finding:** anti-hallucination is solid (0 fabrications, fabricated-number guard always catches injected fakes); cost ~$0.06/section. But output depth is bounded by input claim granularity. See [[ai-news-cron-discord]].

**Quality loop (2026-06-23):** drove Results output from 15 → **stable 78–85/100 (peak 85)** vs the Journal-final Korean gold (eval rubric `lib/core/eval/judge.ts` + `scripts/eval.ts`; gold in `master_thesis/gold/`). Decisive fix: paragraph-by-paragraph write→validate→repair caused wild variance (15/55/25/35) → replaced with **whole-section single render** (`writer.ts::writeSectionWhole`) + deterministic number-coverage repair + source-table reproduction. Then the recommended 1→2→3: (1) **deeper claims** (method+interpretation claims) + **authoritative values** (`source.ts` puts user-provided `data/provided_result_values.md` first so the final R² 0.93/0.97/0.92/0.95 overrides the stale draft 0.9598); (2) **completability ensemble** (3-vote detection + deterministic state → Gate 1 stable, was flip-flopping); (3) **result-gap → author-request** (`stages/resultGaps.ts`: checklist of expected result values; provided→use, missing→`〔입력 필요: …〕` placeholder + question, never invent). Cost rose ~$0.06→~$0.16/section. Now produces real Korean journal Results (4.1/4.2/4.3 + Table 4.1 + all ρ/R²/% verbatim, structure=aligned). Lesson: feed the user's real result material and render whole-section; provided-values authority + ensemble voting kill the variance.

**How to apply:** when working PaperFlow, work in the paperflow repo (not jeff_soul); keep it independent of figureai; never feed the answer-key section into generation.
