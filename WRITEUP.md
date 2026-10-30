# Design write-up — MATACS-TH-2026-02

Assumptions used for this design and the sample ranking:

1. Category criteria and weights are versioned admin configuration, not constants in application code.
2. The brief gives weights but not numeric conversion functions for every criterion. The sample ranking uses a disclosed provisional rubric. In production, score maps, thresholds, normalization, missing-evidence policy, and tie-breakers are admin-configured and versioned.
3. Stated bid prices are treated as comparable quoted totals for this sample. Unstated scope inclusions must be surfaced for reviewer verification, not silently inferred.
4. Explicit proposal claims are treated as extracted claims, not independently verified facts.
5. An unspecified timeline is unknown — not zero weeks and not automatic deadline failure.
6. A proposal cannot override system policy by embedding instructions aimed at an AI reviewer.

Provisional sample score maps (exercise only): experience = `min(100, 10 × qualifying installs ≥100 kW)`; price = relative normalization among proposals that pass both mandatory gates and state a price (cohort A/C/D/E for this sample); timeline tiers 10 weeks or less = 100, 11–12 = 90, 13–14 = 80, 15–16 = 60, over 16 = 0 with review; warranties = average of panel years / 25 and workmanship years / 15, each capped at 100; team/approach = 25 points each for designated project lead, defined crew, safety plan, and system performance monitoring (progress reporting is not monitoring). Weighted total uses 30% / 25% / 15% / 15% / 15%, rounded to two decimals only after summing unrounded components. Tie-break order is part of the versioned rubric: higher mandatory-evidence completeness, then higher timeline subscore, then lower price, then proposal letter.

## 1. AI vs. rules

AI parses messy proposal language into typed fields with evidence quotes and source locations. It is good at locating licence wording, insurance amounts, schedules, warranties, and team claims across uneven PDF text.

Ordinary code validates schema and units, applies mandatory gates, computes weighted scores, checks weight totals, sorts, applies tie-breakers, and formats output. Humans resolve uncertain or conflicting claims and make the award decision.

Eligibility and arithmetic stay out of free-form model reasoning because those steps must be repeatable, auditable, and identical for the same approved facts and rubric version. Models can paraphrase inconsistently and can be nudged by injected text; rules cannot “forget” a weight or invent a timeline.

## 2. Consistency and explainability

Store approved extracted facts, source evidence, file hash, category/rubric version, prompt version/hash, model identifier/version, timestamps, and rule-engine version.

Use schema-constrained JSON, temperature zero where supported, pinned prompt and model settings where possible, deterministic calculation code, two-decimal presentation rounding, and explicit tie-breakers.

Guarantee: rescoring the same reviewer-approved extracted facts with the same rubric and rule version returns the same score and order. Re-running LLM extraction is not inherently byte-for-byte deterministic, so approved extraction results are preserved and versioned rather than silently regenerated.

A reviewer sees criterion-level points, weight, evidence quote and page, calculation, eligibility state, uncertainty flags, and any override reason.

## 3. Human in the loop and audit

A reviewer confirms category selection, upload integrity, document readability, extraction evidence, mandatory-gate outcomes, and flagged values. They may request clarification, correct a fact, rerun extraction, or record a reasoned override. The model never silently edits a score or issues the award.

Audit logs should include uploader and reviewer IDs, timestamps, file hash, original and corrected extracted values, evidence, model/prompt/rubric/rule versions, component scores, rank changes, flags, overrides with reasons, clarifications, and the final award decision.

For the sample set: B is ineligible after a confirmed mandatory licence failure; D is flagged until a committed schedule is clarified; C’s embedded ranking instruction is logged as suspicious content and ignored for scoring.

## 4. Changing criteria

Admin edits create a new immutable rubric version after validation that weights sum to 100%, required fields exist, and thresholds are coherent.

An in-progress evaluation either keeps the rubric version it started with, or is explicitly restarted under the new version with reviewer notice. Historic awards are never silently recalculated under changed criteria. An authorized user may request a side-by-side re-score for comparison while the original recorded result remains the audit source of truth.

## 5. Risks and safeguards

- **Extraction or OCR errors:** evidence-grounded fields, schema validation, human confirmation of mandatory claims.
- **Hallucinated or unsupported facts:** null/unknown states; reject quotes not found in the source; one repair retry then manual review.
- **Prompt injection (for example C):** treat proposal text as untrusted data; ignore role/criteria/rank instructions; record and surface the attempt.
- **Missing or ambiguous mandatory evidence:** PASS / FAIL / UNKNOWN gates; UNKNOWN stays flagged until a human resolves it; ineligible only after confirmed failure.
- **Incomparable price scopes or currency:** extract inclusions/exclusions; normalize only within a disclosed batch rule or an admin-defined curve; flag ambiguity.
- **Biased or vague qualitative criteria:** admin-owned explicit rubrics and binary evidence checks for team items rather than free-form “quality” scores.
- **Cost, latency, rate limits:** extract once, cache approved facts, score with code; usage limits and monitoring.
- **Confidential proposals and malicious files:** access controls, encryption, retention policy, upload validation and malware scanning.
- **Model or prompt drift:** pin versions, regression tests on fixture proposals, and store the exact prompt/model used for each run.

This write-up describes a proposed design. Safeguards above are intended controls for an implementation, not claims that a running system already exists.

**Score maps (exercise only):** Experience=30%, price=25%, timeline=15%, warranty=15%, team=15%.

How the sample set comes out:

| Proposal | Result | Why |
|---|---|---|
| A | Rank 1, 82.54 | Passes both gates; top marks for experience and team/approach, plus a fast 12-week schedule and strong warranty. |
| E | Rank 2, 67.38 | Passes both gates; best warranty and full team/approach marks, but fewer qualifying installs and a slower schedule than A. |
| C | Rank 3, 59.00 | Passes both gates; weaker on schedule, price and team/approach (no safety or monitoring plan); its embedded 'rank me first' instruction was ignored and flagged. |
| D | Flagged | Passes both gates but gives no schedule, so the 16-week limit and timeline score cannot be checked; provisional score range is 62.7-77.7, so its rank depends on the clarification. |
| B | Ineligible | Fails the mandatory licence gate: the electrical licence is not held by the bidder, only promised through a subcontractor to be confirmed after award. |

D is flagged, not rejected: missing information needs a question to the bidder, not an automatic rejection.
