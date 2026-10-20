# livespec-driver-pi

This directory is the live natural-language specification for
`livespec-driver-pi`, the reference **pi Driver** for the livespec family — the
pi-runtime analogue of `livespec-driver-claude` and `livespec-driver-codex`. It
is maintained by livespec itself: every change lands through a propose-change
and a revise pass, and each revision is snapshotted under `history/`.

The spec governs ONLY what the Driver owns — the thin binding seam between the
pi runtime, this package, and livespec core. The operation prose, the reference
spec-side CLIs, the JSON schemas, and the built-in templates all live in
livespec core; this tree defers to core by citation and never restates the
upstream contract. When a rule here appears to conflict with livespec core's
`SPECIFICATION/`, the upstream rule wins.

## How the files relate

| File | What it holds |
|---|---|
| `spec.md` | The primary surface: what the Driver is, what it ships, where its scope ends, the vocabulary, the public skill surface, and how this tree evolves |
| `contracts.md` | The Driver-owned seam shapes: the pi package manifest, the eight-binding set, the core-root resolution chain, config-named CLI dispatch, the footgun-guard extension, and versioning |
| `constraints.md` | Architecture-level constraints on how that seam may be realized, and the forbidden patterns |
| `non-functional-requirements.md` | Contributor-facing invariants: the task runner, repo layout, enforcement suite, release flow, test discipline, and the acceptance bar for claiming pi support |
| `scenarios.md` | Gherkin worked examples for each contract path — resolution-chain fallback, the guard's block and pass-through behavior, and the structural gate's refusals |
| `history/` | One directory per revision, holding that version's spec snapshot and the proposed changes that produced it |

Read `spec.md` first for the shape of the thing, then `contracts.md` for the
surface a change would have to preserve.
