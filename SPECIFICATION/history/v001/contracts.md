# livespec-driver-pi — contracts

The contracts in this file are the Driver-owned seam: the shapes and disciplines
that MUST hold at the boundary between the pi runtime, this Driver package, and
livespec core. Each is mechanically enforced by
`dev-tooling/check-pi-package-structure` unless noted otherwise. Where a
contract has an upstream owner, this file cites it rather than restating it.

## pi package manifest

The Driver ships as a pi package declared by a repo-root `package.json`. The
following invariants hold:

- `package.json` MUST parse as JSON and MUST carry `pi-package` among its
  `keywords`, which is how the package announces itself as pi-loadable.
- The `pi` block MUST declare exactly the two resource directories this Driver
  ships: the skills directory holding the eight bindings, and the extensions
  directory holding the single guard. Every declared directory MUST exist — a
  manifest naming an absent directory loads nothing and reports nothing.
- `$.version` is the single source of truth for the shipped Driver version and
  is release-please-managed (§"Versioning").

Core's own packaging is the deliberate complement: per
`livespec/SPECIFICATION/contracts.md` §"Plugin distribution", core declares NO
pi manifest key and ships NO pi resource directories, so pi loads zero resources
from the core package. Core is an artifact carrier on the pi path exactly as it
is on the Claude and Codex paths. This Driver therefore MUST NOT expect core to
surface anything to pi by itself; it resolves core's files from the clone.

## Skill-binding set

The package MUST ship exactly the eight bindings, one per spec-side operation:
`seed`, `propose-change`, `critique`, `revise`, `doctor`, `prune-history`,
`next`, `help`. For each:

- a directory `skills/livespec-<operation>/` MUST exist;
- it MUST contain a `SKILL.md`;
- that `SKILL.md` MUST open with a `---`-fenced frontmatter block whose `name`
  equals `livespec-<operation>` and whose `description` is non-empty. pi refuses
  to load a description-less skill and warns on a name that breaks the skill
  name rules, and both failures are quiet at runtime.

No extra skill directory may exist, and none of the eight may be missing. The
operation *set* is a core contract; this contract governs the Driver-local
binding directories that realize it.

Each binding MUST be **thin**, in the sense fixed upstream by the pi dogfooding
contracts in `livespec/SPECIFICATION/non-functional-requirements.md`: it reads
the named core prose file completely before acting, follows
that prose for behavior and failure handling, and invokes the named wrapper when
the operation is wrapper-backed. A binding MUST NOT copy operation prose,
wrapper files, or built-in templates, and MUST NOT point at
`.claude-plugin/skills/*` — core intentionally ships no such tree, so a binding
that names one is pointing at nothing.

## Core-root resolution

Every binding resolves `<core-root>` — the livespec core plugin root from which
it reads operation prose and dispatches the spec-side CLIs — through the ONE
shared resolver `lib/resolve-core-root.sh`, surfaced to shell as
`$LIVESPEC_CORE_ROOT`. A binding MUST call the shared resolver and MUST NOT
restate the chain inline: independently-maintained inline copies are kept in
agreement only by copying, which is how a single positional defect once came to
live in all eight of a sibling Driver's bindings at once.

The chain is ordered, first hit wins:

1. the `LIVESPEC_CORE_PLUGIN_ROOT` environment variable, when set and non-empty
   — the explicit operator override;
2. else the governed project's own `.claude-plugin/` — the project IS the
   livespec core repo (the dogfooding path; core ships its prose under
   `.claude-plugin/` regardless of which Driver runtime consumes it);
3. else the PROJECT-scope pi package clone of core;
4. else the USER-scope pi package clone of core.

Steps 3 and 4 are pi's own git-package clone locations for a project-scope and a
user-scope install respectively. A candidate counts as resolved ONLY when it
carries a `prose/` directory: a clone that exists but is empty or half-fetched
MUST fail loudly rather than resolve to a path whose every prose read would fail
separately and confusingly.

This chain is Driver-owned; livespec core is agnostic to how a Driver finds it.
A binding MUST NOT hardcode a core path and MUST NOT assume a single
installation shape.

On exhaustion the resolver MUST write a diagnostic naming every candidate it
searched, in order, and exit non-zero; the calling binding MUST surface that
diagnostic verbatim and stop, rather than improvising a path or running an
install command the diagnostic did not ask for. The diagnostic MUST distinguish
two causes that look identical from the outside: an override that is set but
resolves nothing is a configuration error rather than a missing install, and a
non-interactive run in an untrusted project is pi's trust gate silently ignoring
project packages rather than an absent one.

## Config-named CLI dispatch

When core's prose calls for a CLI, the binding MUST invoke the wrapper named in
the **governed project's** `.livespec.jsonc` under the operation's `spec_clis`
key, as an argv-form array, with explicit argv. When the file, the `spec_clis`
section, or the operation's key is absent, the binding falls back to core's
reference default under `<core-root>`.

Two substitutions are contractual:

- A plugin-root substitution token in a configured argv expands to
  `<core-root>` — CORE's root. It MUST NOT expand to this Driver's own package
  root, which carries no wrapper tree at all.
- The wrapper path is resolved through `$LIVESPEC_CORE_ROOT`, never through a
  literal `.claude-plugin/scripts` path and never under `uv run`: the installed
  package has no project for `uv` to resolve, so the wrappers run under bare
  `python3`.

The structural gate walks every `SKILL.md`, tracks fenced regions, and emits one
violation per fenced wrapper invocation that breaks either rule.

## Footgun-guard extension

The Driver SHIPS exactly one first-party pi extension: the footgun guard
required by `livespec/SPECIFICATION/contracts.md` §"Driver-shipped hooks". Its
required behavior is owned upstream; this contract states the Driver-local
surface that realizes it.

- The extension MUST register exactly ONE `tool_call` event handler.
- The handler MUST carry all four block predicates the upstream contract
  enumerates: `--no-verify` passed to a commit or push, an assignment disabling
  lefthook, setting a checkout bare, and a write targeting a livespec PRIMARY
  checkout.
- Detection MUST be segment- and token-based over the EXECUTED leading command,
  so a forbidden string appearing as DATA — inside an echo, a read-only config
  query, a here-doc body, or a commit message — is NOT blocked.
- A block MUST carry an actionable reason naming the correct alternative, not a
  bare refusal.

**Fail-open is delivered by hand here, and that is the whole point.** pi's own
default is the OPPOSITE of the upstream fail-open discipline: a `tool_call`
handler that throws BLOCKS the tool. So the handler MUST catch its own errors
internally and pass through on any failure. Inheriting pi's default would turn a
guard bug into a wedged session, which is precisely the outcome the upstream
discipline forbids. The guard acts ONLY when it POSITIVELY identifies a
forbidden invocation.

The guard is a backstop-of-last-notice, not the enforcement itself: the family
commit-refuse hook and branch protection are the real backstops, and the guard
converts a silent footgun into an actionable, named block.

**Mutating-operation gate.** Per the pi dogfooding constraints in
`livespec/SPECIFICATION/non-functional-requirements.md`, the mutating operations
(`seed`, `propose-change`, `critique`, `revise`, `prune-history`) MUST NOT be
exercised unless the guard is in place;
the read-only operations (`doctor`, `next`, `help`) do not depend on it. Each
mutating binding MUST say so and MUST stop rather than proceed unguarded when
the extension is not loaded — most often the trust gate under a non-interactive
run.

**Destructive-command controls are preserved and additive.** Every control the
core prose already carries survives this guard unchanged. In particular
`prune-history` remains explicit-user-invocation only: its binding MUST disable
model invocation and MUST say in prose that it is never inferred or
auto-activated from a generic mention of history.

**Absent by contract: no auto-memory guard.** This Driver ships NO auto-memory
write guard, because pi has no harness-private local-memory store to guard. That
absence is anchored to the pi release observed when this contract was ratified
rather than assumed permanent; if a future pi release adds such a store, an
auto-memory guard becomes required through a propose-change cycle against
`livespec/SPECIFICATION/contracts.md` §"Driver-shipped hooks", not through a
Driver-local decision.

## Versioning

`package.json`'s `$.version` is the single source of truth for the shipped
Driver package version and is auto-managed by release-please from per-commit
Conventional Commits. No other file in this repo restates that version. This
mirrors the release mechanism every other family member uses for its own
distributed artifact.
