---
topic: enforcement-suite-typescript-lane
author: claude-opus-4-8
created_at: 2026-09-02T04:50:26Z
---

## Proposal: Document all four repo-local enforcement gates

### Target specification files

- SPECIFICATION/non-functional-requirements.md

### Summary

The enforcement-suite narrative asserts exactly two repo-local gates, but four ship; the spec MUST enumerate check-extension-quality and check-pi-drive-output alongside the two it already names.

### Motivation

capture-spec-drift found heuristic impl->spec drift: non-functional-requirements.md was frozen at v001 before the TypeScript-extension-quality pass. Its §"Contracts" states 'The two repo-local gates are: check-pi-package-structure ... check-doctor-static' and §"Constraints" reinforces 'Both the repo-local structural gate and the doctor-static gate exist because a shared Verifier would otherwise skip vacuously or have no tree to read.' The implementation actually ships four repo-local gates in dev-tooling/. The static doctor phase cannot catch this because the spec text is internally consistent; it simply describes a smaller repo than the one that ships.

### Proposed Changes

§"Contracts", the enforcement-suite paragraph: the spec MUST replace the assertion that there are exactly two repo-local gates with an enumeration of all four repo-local gates that ship. It MUST retain the existing check-pi-package-structure and check-doctor-static entries and MUST add: (a) check-extension-quality -- the behavioral-plus-typecheck gate over the first-party TypeScript footgun guard (tsc --noEmit under erasableSyntaxOnly, plus a node --test suite driving the guard's exported decide()), wired repo-locally because a TypeScript guard rides none of the Python gates and the structural gate's text assertions cannot detect a guard that stopped compiling or a predicate that inverted; and (b) check-pi-drive-output -- which classifies unattended pi drive transcripts, so automation MUST branch on the classifier's exit status rather than pi's raw process status, because pi has been observed exiting 0 on a failed model call. §"Constraints", the 'A gate is not shipped ahead of its subject' paragraph MUST generalize the sentence that currently names only the structural gate and the doctor-static gate so it also acknowledges check-extension-quality, whose behavioral coverage MUST be wired repo-locally for the same vacuous-skip reason. This change edits prose inside existing H2 sections and adds or removes no H2, so tests/heading-coverage.json MUST NOT require a co-edit.

## Proposal: Reflect the node and npm toolchain lane in the Toolchain paragraph

### Target specification files

- SPECIFICATION/non-functional-requirements.md

### Summary

§"Toolchain" claims uv owns 'every package', but the extension-quality lane makes node a pinned toolchain member and gives the extension's JavaScript dependencies to npm; the spec MUST scope the uv claim to Python and name the node/npm lane.

### Motivation

capture-spec-drift found that §"Toolchain" ('mise pins the non-Python binaries; uv owns the Python version and every package') predates the TypeScript-extension-quality pass. The impl now pins node via mise and manages the footgun-guard extension's JavaScript dependencies through package.json / package-lock.json via npm ci, consumed by check-extension-quality. The 'every package' claim no longer holds -- npm owns the JavaScript side.

### Proposed Changes

§"Toolchain": the spec MUST qualify the claim that uv owns 'every package' so that it reads 'every Python package', and MUST add that node is mise-pinned and that the footgun-guard extension's JavaScript dependencies are npm-managed via package.json / package-lock.json (npm ci), consumed by the check-extension-quality gate. The revised text MUST make clear that the TypeScript guard lane is why node and npm participate in the toolchain, so that a reader MUST NOT infer that uv manages the extension's dependencies.
