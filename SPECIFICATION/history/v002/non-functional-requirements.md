# livespec-driver-pi — non-functional requirements

Contributor-facing invariants: how this repo is structured, guarded, built,
tested, and evolved. Where `contracts.md` says *what MUST be true* of the Driver
seam, this file says *how it is guarded* and how the repo is operated.

## Boundary

Content belongs in this file when it is invisible at the user-facing surface —
a contributor developing the Driver observes it, a person driving
`/skill:livespec-<operation>` from pi never does. The decision rule, applied
against the other four files:

- If an end user could observe it by installing and driving the package, it
  belongs in `spec.md`, `contracts.md`, or `constraints.md` instead.
- If it is a wire-level or surface-level shape of the Driver seam, it belongs in
  `contracts.md`.
- If it is an architecture-level prohibition on how the seam is realized, it
  belongs in `constraints.md`.
- If it is a worked example of externally-visible behavior, it belongs in
  `scenarios.md`.
- Everything else — the task runner, the repo layout, the enforcement suite,
  the release flow, test discipline, and the spec-evolution loop — belongs here.

The four sections below mirror that same decomposition, each holding the
contributor-facing analogue of its user-facing counterpart.

## Spec

**Task-runner discipline.** `just` is the single source of truth for every
dev-tooling invocation. `lefthook` (pre-commit and pre-push) and CI delegate via
`just <target>`; neither invokes a tool binary directly. `just check` is the
full enforcement aggregate and is the load-bearing safety net — it runs locally,
at pre-push, and in CI, so the same suite runs in every context.

**Toolchain.** `mise` pins the non-Python binaries; `uv` owns the Python version
and every package. Git operations that must fire lefthook run through
`mise exec -- git …`, and the hook-bypass flag is never used.

**Repo layout.**

| Path | Purpose |
|---|---|
| `package.json` | The pi package manifest — the `pi-package` keyword, the declared resource directories, and the release-please-managed version |
| `skills/livespec-<operation>/SKILL.md` | The eight thin bindings; pi-runtime mechanics only |
| `lib/resolve-core-root.sh` | The single realization of the core-root resolution chain, called by every binding |
| `extensions/` | The one sanctioned first-party extension: the `tool_call` footgun guard |
| `dev-tooling/` | The enforcement scaffolds, including the repo-local structural gate over the pi package surface and the doctor-static gate over this spec tree |
| `tests/dev-tooling/` | The pytest mirror of `dev-tooling/`, at full coverage |
| `SPECIFICATION/` | This spec tree (dogfooded) |
| `.livespec.jsonc` | Project-local livespec config: template, spec root, active orchestrator plugin, the compat pin against core, declared harnesses, and the cross-repo citation allowlist |
| `justfile`, `lefthook.yml`, `check-targets.txt`, `pyproject.toml` | Task runner, git-hook config, aggregate target list, and dev-tooling pins |

## Contracts

**Enforcement suite.** `just check` aggregates the gates guarding the seam in
`contracts.md`. The two repo-local gates are:

- **`check-pi-package-structure`** — the stdlib-only, fail-closed structural
  gate. It is the mechanical teeth behind
  `contracts.md` §"pi package manifest", §"Skill-binding set",
  §"Config-named CLI dispatch", and §"Footgun-guard extension": the eight
  bindings and only those, frontmatter conformance, no reference to a Claude
  skills tree, canonical wrapper invocation inside fenced regions, the
  explicit-invocation-only posture of `prune-history`, the manifest's declared
  resource directories, and the guard's single registration plus its four
  predicates and its internal catch.
- **`check-doctor-static`** — runs livespec core's static doctor phase against
  this `SPECIFICATION/` tree. It resolves core at the release tag this repo
  pins, so the gate checks the spec against the contract version the Driver
  actually claims compatibility with.

The rest of `just check` is the family-standard canonical block: lint, format,
types, coverage and per-file coverage, the structural AST checks, the
heading-coverage map, and the Red-Green-Replay commit gate.

**CI parity is itself a contract.** Every gate is wired into both lefthook and
the CI matrix. A dedicated CI job MUST also be listed in the aggregate gate
job's dependency list — a job added to the workflow but omitted from that list
runs and reports while gating nothing, which is indistinguishable from a green
result on a casual read.

**Build and release.** The Driver ships as a pi package installed from the
moving `release` branch channel. `package.json`'s `$.version` is the single
source of truth and is release-please-managed from Conventional Commits, per
`contracts.md` §"Versioning". The compat pin against livespec core tracks core's
latest RELEASE tag rather than raw master, and the cross-repo fan-out rewrites
it on each new core release.

## Constraints

**Test discipline.** The `tests/` tree mirrors `dev-tooling/` one-to-one and is
held at full coverage, which is what makes the coverage gates meaningful rather
than green over an empty measurement. Product changes land through the
family's Red-then-Green single-commit ritual, enforced by the commit-refuse
hook and replayed as a range gate at push and in CI.

**A gate is not shipped ahead of its subject.** A check whose subject does not
exist is a red job that teaches nothing, so each gate is wired by the pass that
creates what it guards. The inverse failure is worse and is the one to watch
for: a gate that cannot fail on this repo's layout reports success having
inspected nothing. Both the repo-local structural gate and the doctor-static
gate exist because a shared Verifier would otherwise skip vacuously or have no
tree to read.

**The end-to-end runtime harness is deliberately absent, not forgotten.** A pi
analogue of the sibling Drivers' end-to-end suites would have to launch the pi
CLI against a live model — a live-credential, live-network dependency. The
honest options are a suite CI always skips, which gates nothing, or leaving it
out until the acceptance drive below is run. It is left out. A mocked stand-in
MUST NOT be substituted and called satisfied: a fake pi CLI verifies only the
fake.

**Repository mutation.** Every change uses a worktree, a pull request, a merge,
and cleanup. Committing at the primary checkout, leaving dirty state, or leaving
an orphaned worktree are failures of the workflow rather than acceptable
stopping points. The primary-checkout commit-refuse hook is owned upstream by
`livespec/SPECIFICATION/non-functional-requirements.md`; this repo installs the
canonical scaffold and does not re-specify it.

## Scenarios

**The acceptance bar for claiming pi support.** Per the pi dogfooding
constraints in `livespec/SPECIFICATION/non-functional-requirements.md`, the
existence of package entries in a project's committed pi settings does NOT by
itself license the claim. Verification is
performed with separate pi processes against the INSTALLED distributed Driver,
and it passes only when all of the following hold together:

- the committed pi settings carry both package entries, core and this Driver;
- both packages are present at their project-scope install locations, or the
  user-scope equivalents;
- a non-interactive invocation, with trust established, drives a livespec
  operation through this Driver and core's prose without relying on any
  repo-local adapter directory or an agent-instruction mapping;
- the driven session names the bound core prose file and, for a wrapper-backed
  operation, the wrapper it invokes;
- the skill-command expansion is verified IN the non-interactive path itself,
  never assumed from its documented interactive behavior.

A separate human-discoverability claim drives pi's interactive skill surface and
verifies the eight `livespec-<operation>` skills appear there.

**Temporary registrations are cleaned up.** A package registration created for a
test is removed afterward unless the user explicitly asks to keep it, and
dogfooding installs nothing globally beyond the per-user pi CLI itself.

**Spec evolution.** This tree dogfoods livespec: every change lands through a
propose-change and a revise pass, which snapshots the result as a new version
directory. The static doctor phase flags out-of-process drift, and the
heading-coverage gate mechanically holds the spec's heading set in lockstep with
the coverage map — so adding or renaming a section without updating the map
fails the check rather than silently drifting.
