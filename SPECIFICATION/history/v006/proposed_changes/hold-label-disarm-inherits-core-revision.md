---
proposal: hold-label-disarm-inherits-core.md
decision: accept
revised_at: 2026-11-11T08:51:51Z
author_human: Chad Woolley <thewoolleyman@gmail.com>
author_llm: claude-opus-5-5
---

## Decision and Rationale

Accepted under delegated revise authority (spec_governance.revise_decision_mode delegated; legacy-coordinator-agent R301 standing grade for the hold-label disarm member revises, --only-topic hold-label-disarm-inherits-core). The paragraph is appended to ## Constraints of non-functional-requirements.md, beside the upstream-owned repository-mutation rule, because this specification has no ## Inherited from livespec section in that file. It cites livespec non-functional-requirements.md §"Shared content sync — copier template" (ratified in livespec v240, livespec#3163) rather than restating the behaviour. It already carries the App-token input-key exception (this repository's auto-enable-merge.yml mints with app-id:, livespec's disarm copy with client-id:), in the form livespec-driver-claude v017 and livespec-driver-codex v023 ratified, so no modification is needed. The same commit adds the cited heading to .livespec.jsonc external_references.

## Resulting Changes

- non-functional-requirements.md

## Ratification Review

ratification_review: auto-spawn
reviewer_model: sonnet
reviewer_identity: sonnet
separate_reviewer: True
read_only: True
reviewed_at: 2026-11-11T08:50:13Z
verdict: NO BLOCKERS
proposal_stem: hold-label-disarm-inherits-core
content_digest: 8ad905f9be5ec4fd6e21efcb2d914761822370cbb63b8d78081c07030eeec9bc
