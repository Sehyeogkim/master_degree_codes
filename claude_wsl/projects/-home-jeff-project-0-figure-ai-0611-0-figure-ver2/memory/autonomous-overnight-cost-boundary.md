---
name: autonomous-overnight-cost-boundary
description: How to handle autonomous overnight build sessions and the paid-API boundary for this project
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3237df2d-5237-4891-9ecb-aa4e5a3439e5
---

On 2026-06-11 the user asked me to continue building the figure-coworker pipeline autonomously toward the final goal while they slept, starting with build-prompt. Earlier in the same session they were explicitly cautious about paid image-API spend (gpt-image-1 via OPENAI_API_KEY).

**Why:** "reach the final goal autonomously" and "don't surprise me with API cost" are both true at once.

**How to apply:** Build and test every deterministic (no-cost) stage fully. For any stage that fires a real paid/irreversible external call (gpt-image-1 generation; possibly an LLM-judged eval or the `plan` LLM command), implement the full code path and verify it with mocked/injected clients + fixtures — but do NOT fire the real call unsupervised. Leave it gated behind the user's explicit go-ahead and surface clearly in the morning summary what is ready to run for real. The codebase uses subagent-driven TDD, stage-by-stage (spec in docs/superpowers/specs, plans in docs/superpowers/plans); continue that rhythm but stop checkpointing between stages once autonomy is granted.
