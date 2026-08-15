# livespec-driver-pi — the pi Driver for livespec

This is the natural-language specification for `livespec-driver-pi`, the
reference **pi Driver** for the livespec family — the pi-runtime analogue of
`livespec-driver-claude` and `livespec-driver-codex`. The Driver dogfoods
livespec: this `SPECIFICATION/` tree evolves through the same seed /
propose-change / critique / revise / doctor / prune-history loop every governed
project uses.

Throughout this spec, the token "v1" refers to the Driver package's first MAJOR
release line (semver `1.x.x`). Pre-1.0 `0.x` releases are bootstrap territory
and do not satisfy any rule scoped to "v1". Rules without a "v1" qualifier are
unconditional and bind every release.

## Purpose

A **Driver** is the thin, agent-runtime-specific binding layer through which a
human drives the livespec spec lifecycle interactively. `livespec-driver-pi` is
the pi-runtime Driver under livespec's contract-plus-reference-implementations
architecture (`livespec/SPECIFICATION/spec.md`). It binds livespec core's
harness-neutral material to ONE tool runtime — the pi coding agent.

This repo ships exactly four things, all pi-runtime mechanics:

1. **The eight thin SKILL.md bindings** under `skills/livespec-<operation>/`,
   one per spec-side operation (`seed`, `propose-change`, `critique`, `revise`,
   `doctor`, `prune-history`, `next`, `help`). Each binding resolves livespec
   core at runtime, reads core's operation prose completely, and dispatches the
   config-named spec-side CLI.
2. **One shared resolver** (`lib/resolve-core-root.sh`) — the single realization
   of the core-root resolution chain every binding calls.
3. **One sanctioned pi extension** (`extensions/livespec-footgun-guard.ts`) —
   the `tool_call`-blocking footgun guard required by
   `livespec/SPECIFICATION/contracts.md` §"Driver-shipped hooks". It is the ONE
   first-party extension this Driver ships; the eight operation bindings remain
   SKILL.md skills.
4. **A structural gate** (`dev-tooling/check-pi-package-structure`) that
   mechanically enforces the manifest, binding-set, invocation, and guard
   invariants this spec codifies.

Everything substantive stays in livespec core: the harness-neutral operation
prose, the reference spec-side CLIs, the JSON schemas, and the built-in
templates. The Driver carries none of those. Core reaches a pi project as a
**resource-less pi git package** — it declares no `pi` manifest key and ships no
pi resource directories, so pi loads zero resources from it and the Driver
resolves core's material out of the clone itself.

## Scope boundary

This spec governs the Driver's own seam — the surface this repo owns and that
nothing upstream governs:

- the pi package manifest shape and the resource directories it declares
  (`contracts.md` §"pi package manifest");
- the eight-binding set and its frontmatter discipline
  (`contracts.md` §"Skill-binding set");
- the **core-root resolution chain** and its fail-modes
  (`contracts.md` §"Core-root resolution");
- the **config-named CLI dispatch** discipline by which a binding invokes core's
  wrapper CLIs (`contracts.md` §"Config-named CLI dispatch");
- the **footgun-guard extension**'s existence, registration, and delivered
  posture (`contracts.md` §"Footgun-guard extension").

Out of scope — core-owned, referenced here and never restated: the operation
prose contents; the wrapper-CLI surfaces, exit codes, and wire contracts; the
JSON schemas; the built-in templates; the eight operation *names* and any rename
(those require a core propose-change cycle); the guard's *behavioral discipline*
(which invocations are forbidden, and the fail-open requirement), owned by
`livespec/SPECIFICATION/contracts.md` §"Driver-shipped hooks"; and the
family-standard primary-checkout commit-refuse hook, owned by
`livespec/SPECIFICATION/non-functional-requirements.md`.

Upstream-wins: when a rule here conflicts with livespec core's
`SPECIFICATION/`, the upstream rule wins.

## Terminology

The family vocabulary is defined upstream in `livespec/SPECIFICATION/spec.md`;
this tree uses it without redefinition. The terms that recur here:

- **Driver** — the thin, agent-runtime-specific binding layer (this repo, for
  pi). Core is agnostic to it.
- **core-root** (`<core-root>`) — the resolved livespec core plugin root from
  which a binding reads prose and dispatches CLIs. Surfaced to the bindings as
  the `$LIVESPEC_CORE_ROOT` shell variable.
- **Binding** — a single `skills/livespec-<operation>/SKILL.md` that binds one
  core operation to pi.
- **Thin-transport binding** — a binding (`next`) whose whole job is to invoke
  its backing wrapper and present the structured output verbatim, with no
  ranking or judgment in the binding.
- **Guard** — the `tool_call` footgun-guard extension this Driver ships.

## Public surface

The Driver's public, user-facing surface is the eight pi skills, named
`livespec-<operation>` and invoked as `/skill:livespec-<operation>`. pi skill
names admit no colon-namespacing, so the `livespec-` name prefix carries the
namespace; the same skill-command form selects an operation in a non-interactive
`pi -p` or RPC prompt. The operation *set* and *names* are a core v1 contract;
the *runtime mechanics* that expose them are this repo's.

The package is installed **project-scoped**, recorded in the governed project's
committed `.pi/settings.json`, per
`livespec/SPECIFICATION/contracts.md` §"Plugin distribution". Two consequences
are load-bearing for this Driver and are treated as part of its public surface:

- The install ref is the moving `release` branch channel — the same channel the
  Claude and Codex marketplaces track — not a pinned tag.
- pi's **project-trust gate** means a NON-INTERACTIVE invocation silently
  ignores project-local settings and packages until a trust decision is
  established. An unattended drive of a livespec operation therefore resolves
  NOTHING rather than failing loudly, and a Driver diagnostic MUST name that
  possibility rather than reporting a missing install.

The guard is the second public surface: a package-shipped pi extension that
loads automatically once the package is loaded and the project is trusted.

## Lifecycle and evolution

This `SPECIFICATION/` tree is the live spec for the pi Driver seam and evolves
through the standard livespec loop. The Driver's *behavior* — what each
operation does — is owned by core's operation prose; edits to behavior happen in
livespec core, not here. This repo's spec changes when the Driver-local seam
changes: the manifest shape, the resolution chain, the dispatch discipline, the
guard's wiring, or the structural gate.

Renaming the package, adding or removing a binding, or changing the guard's
posture requires a propose-change cycle, routed by ownership: a Driver-local
mechanic runs against this tree, and an upstream contract (the operation set,
the guard's behavioral discipline, the install model) runs against livespec
core.
