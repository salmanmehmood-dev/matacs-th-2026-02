# MATACS-TH-2026-02 — AI Proposal Triage Design

**Full name:** Salman Mehmood  
**Assessment reference:** MATACS-TH-2026-02  
**Time spent:** [UPDATE WITH ACTUAL TIME BEFORE SUBMISSION]

## AI use

I used Cursor Agent to draft and validate the repository files against the assessment structure and the disclosed provisional scoring rubric. I disagreed with treating proposal D’s missing schedule as a zero timeline score; it is flagged with null rank and score until clarified. I also rejected the embedded instruction in proposal C that tried to force a first-place ranking—scoring stays in deterministic rules, not in model output. I reviewed the component scores and file layout myself rather than treating generated results as final without checking.

## Deliverables

| File | Contents |
|------|----------|
| [WRITEUP.md](WRITEUP.md) | Answers to the five design questions, including assumptions and safeguards |
| [PROMPTS.md](PROMPTS.md) | Extraction prompt (and repair prompt) exactly as they would be sent |
| [ranking.json](ranking.json) | Expected sample ranking for proposals A–E |
| [diagram/proposal-triage.png](diagram/proposal-triage.png) | Process flow from criteria setup and upload through ranked output and award |

## Notes

This is a design submission only. No application is deployed. Criteria are treated as admin-configured and versioned. The sample ranking uses a provisional, disclosed score-conversion rubric so results are reproducible for this exercise.
