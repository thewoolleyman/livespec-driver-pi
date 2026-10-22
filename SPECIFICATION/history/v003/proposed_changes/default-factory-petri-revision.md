---
proposal: default-factory-petri.md
decision: accept
revised_at: 2026-10-22T22:23:45Z
author_human: Chad Woolley <thewoolleyman@gmail.com>
author_llm: claude-opus-5-5
---

## Decision and Rationale

Accepted per ruling R668 (maintainer direction relayed by coordinator session gitops-fleet-capacity-monitoring: this repository's dispatch default moves from the `legacy` Fabro factory to `petri`, the current Fabro server) and ruling R672 (this spec revise is approved as a delegated decision); work-item bd-ib-iud52v. The committed .livespec.jsonc on the same branch declares a registry-backed `petri` entry, keeps `legacy` declared and registry-backed, and sets `default_factory` to `petri`; the orchestrator's resolver resolves `petri` through /etc/livespec/fabro-factories.json to gmktec-xubuntu:32276, environment livespec-ci. Only the default-factory sentence of §"Factory routing" changes; the registry-backed, no-server, no-docker_host rule and the registry-bound resolution are unchanged, and no heading moves. In addition to the configured ratification reviewer recorded below, an independent read-only review of the same resulting bytes ran on OpenAI Codex (reviewer model gpt-6-astra, `codex exec -s read-only`), verdict NO BLOCKERS in round 1 of 1 at 2026-10-22T22:20:36Z; its only observation (stale .livespec.jsonc comments) was folded into the branch's configuration comments, which are outside the ratified bytes.

## Resulting Changes

- constraints.md

## Ratification Review

ratification_review: auto-spawn
reviewer_model: fable
reviewer_identity: fable
separate_reviewer: True
read_only: True
reviewed_at: 2026-10-22T22:22:00Z
verdict: NO BLOCKERS
proposal_stem: default-factory-petri
content_digest: c28dfe5eeacd9f82eac12262c9fa0348f1ec6e863bfc9890ca8b8facd73a5868
