---
topic: hold-label-disarm-inherits-core
author: claude-opus-5-5
created_at: 2026-11-11T08:36:48Z
---

## Proposal: This repository carries the hold-label disarm workflow livespec core makes inherited fleet policy

### Target specification files

- SPECIFICATION/non-functional-requirements.md

### Summary

Add one paragraph to `## Constraints` in `non-functional-requirements.md` binding this repository, which carries `auto-enable-merge.yml`, to also carry `disarm-on-hold-label.yml`, citing livespec core for the behaviour rather than restating it.

### Motivation

livespec core's proposal `hold-label-disarm-inherited-policy` (merged as livespec#3162, 16503c72; ratified in livespec v240, livespec#3163) makes the `auto-enable-merge.yml` / `disarm-on-hold-label.yml` pair inherited fleet policy in livespec `non-functional-requirements.md` §"Shared content sync — copier template", and says a non-template member carries its own copy and cites that section rather than restating it. This repository runs `auto-enable-merge.yml` but carries no `disarm-on-hold-label.yml`, so a `do-not-merge` label added after the factory bot armed a pull request leaves auto-merge on, the gap measured on livespec-dev-tooling#4019, #4031 and #4033. livespec-overseer, livespec-runtime, livespec-driver-claude and livespec-driver-codex already carry it under the same inherited clause. No clause in this specification governs auto-merge or hold labels today, so the carrier work item has no honest References line; this paragraph gives it one. This repository's spec has no `## Inherited from livespec` section in `non-functional-requirements.md`, so the clause sits beside the other upstream-owned contributor rule, the repository-mutation paragraph under `## Constraints`. This repository's `auto-enable-merge.yml` mints its App token with the `app-id:` input key, while livespec's root disarm copy uses `client-id:`, so the clause states the one permitted difference up front, as livespec-driver-claude v017 and livespec-driver-codex v023 ratified it.

### Proposed Changes

In `SPECIFICATION/non-functional-requirements.md`, under `## Constraints`, append this paragraph after the **Repository mutation.** paragraph:

**Hold-label disarm (inherited).** Because this repository carries `.github/workflows/auto-enable-merge.yml`, it MUST also carry `.github/workflows/disarm-on-hold-label.yml`, identical to livespec's root copy except that the App-token input key matches this repository's `auto-enable-merge.yml`, which turns a pull request's auto-merge off when the `do-not-merge` label is added to it. The behaviour, and the rule that every fleet member carrying `auto-enable-merge.yml` carries it, are livespec's `non-functional-requirements.md` §"Shared content sync — copier template" and are not restated here.

The same revise MUST add `§"Shared content sync — copier template"` to the `livespec` entry of `.livespec.jsonc`'s `external_references` allowlist, in the bare heading form that file requires.

Ordering: the cited section's disarm bullet is already ratified in livespec v240, so this proposal may be revised as soon as it merges.
