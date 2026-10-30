---
name: validation-singleshot-works
description: Outcome of the first real gpt-image-2 validation run of the figure-coworker pipeline
metadata: 
  node_type: memory
  type: project
  originSessionId: 3237df2d-5237-4891-9ecb-aa4e5a3439e5
---

On 2026-06-11 the full figure-coworker pipeline was validated end-to-end with real `gpt-image-2` generations (2 of the user's 10-call budget). The project's central open question — can a single-shot image model reliably fill a multi-panel grid while respecting panel boundaries — got a **strong YES** on both demos (plaque `cross-section-progression` and FSI `linear-horizontal-pipeline`): clean panel boundaries, no cross-panel bleed, no text inside the image, clean white background. No serious failure tags triggered.

Key setup detail: instantiate the demo canvas at a gpt-image-2-supported size (1536×1024) so canvas==image and the crop scale is 1.0 — exact panel alignment. `.env` was changed `IMAGE_MODEL` gpt-image-1 → gpt-image-2 (the user said "gpt image 2.0"; the real id is `gpt-image-2`, no "2.0").

Open follow-ups recorded in `docs/superpowers/specs/2026-06-11-validation-findings.md`: overlay labels sit cramped inside panels (move to a reserved title strip); cairosvg won't composite `final.svg`'s external image href (works in browsers; consider base64 embed); subjective eval scores are `pending_review` pending a vision judge. 8 image calls remain for the user to explore. See [[autonomous-overnight-cost-boundary]].
