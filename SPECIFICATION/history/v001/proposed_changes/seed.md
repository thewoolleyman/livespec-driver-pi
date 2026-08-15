---
topic: seed
author: livespec-seed
---

## Proposal: seed

### Target specification files

- SPECIFICATION/spec.md
- SPECIFICATION/contracts.md
- SPECIFICATION/constraints.md
- SPECIFICATION/non-functional-requirements.md
- SPECIFICATION/scenarios.md
- SPECIFICATION/README.md

### Summary

Initial seed of the specification from user-provided intent.

### Motivation

Specify livespec-driver-pi: the reference pi Driver for the livespec family — the pi-runtime analogue of livespec-driver-claude and livespec-driver-codex. The spec governs ONLY the Driver-owned seam between the pi coding agent, this package, and livespec core: the pi package manifest and its declared resource directories; the eight thin livespec-<operation> SKILL.md bindings invoked as /skill:livespec-<operation>; the single shared core-root resolution chain (operator override, then the governed project's own livespec-core checkout, then the project-scope pi package clone, then the user-scope clone, each resolved only on positive evidence of core's prose directory); the config-named spec-side CLI dispatch discipline; and the ONE sanctioned first-party pi extension, the tool_call footgun guard that must deliver fail-open by catching its own errors because pi's own tool_call default is fail-closed, and that gates every mutating operation. Everything substantive — the operation prose, the reference spec-side CLIs, the JSON schemas, and the built-in templates — stays in livespec core, which reaches a pi project as a resource-less git package; this tree defers to core by citation and never restates the upstream contract, and the upstream rule wins on any conflict.

### Proposed Changes

Specify livespec-driver-pi: the reference pi Driver for the livespec family — the pi-runtime analogue of livespec-driver-claude and livespec-driver-codex. The spec governs ONLY the Driver-owned seam between the pi coding agent, this package, and livespec core: the pi package manifest and its declared resource directories; the eight thin livespec-<operation> SKILL.md bindings invoked as /skill:livespec-<operation>; the single shared core-root resolution chain (operator override, then the governed project's own livespec-core checkout, then the project-scope pi package clone, then the user-scope clone, each resolved only on positive evidence of core's prose directory); the config-named spec-side CLI dispatch discipline; and the ONE sanctioned first-party pi extension, the tool_call footgun guard that must deliver fail-open by catching its own errors because pi's own tool_call default is fail-closed, and that gates every mutating operation. Everything substantive — the operation prose, the reference spec-side CLIs, the JSON schemas, and the built-in templates — stays in livespec core, which reaches a pi project as a resource-less git package; this tree defers to core by citation and never restates the upstream contract, and the upstream rule wins on any conflict.
