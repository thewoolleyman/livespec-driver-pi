# livespec-driver-pi — constraints

Architecture-level constraints the bindings, the shared resolver, the guard
extension, and the structural gate honor. `contracts.md` says what the seam MUST
look like; these constraints say what the implementation MAY and MAY NOT do to
realize it.

## Inherited from livespec

Every constraint in `livespec/SPECIFICATION/constraints.md` that applies to a
Driver binding applies here unmodified; this tree does not relax or restate
them. Where an inherited constraint and a Driver-local one appear to conflict,
the upstream constraint wins.

## Binding constraints

- A binding is **thin**: it carries no behavior of its own beyond resolving
  `<core-root>`, reading core's operation prose, and dispatching the
  config-named CLI. All dialogue capture, content generation, and
  structured-finding interpretation are dictated by core's prose, never invented
  in the binding.
- A binding MUST NOT paraphrase, summarize, or act on a partial read of the
  prose, and MUST NOT restate the prose's steps, failure handling, output
  schemas, or wrapper behavior in a form that can drift from core.
- Each `SKILL.md` is self-contained: a binding MUST NOT depend on another
  binding's files. The shared resolver is the deliberate exception, and it is
  package infrastructure rather than a binding.
- A thin-transport binding MUST NOT accrete ranking, filtering, formatting, a
  confirmation dialogue, or an opt-in flag — all such logic lives in the backing
  core wrapper.
- The Driver package ships NO `prose/` tree and NO wrapper CLIs: both are
  core-owned and resolved at runtime. It ships the bindings, the resolver, the
  guard, and the manifest only.

## Resolution-substrate constraints

- The resolution chain in `contracts.md` §"Core-root resolution" is fixed. A
  binding MUST walk it through the shared resolver, in order, and MUST NOT
  short-circuit to a hardcoded path.
- A binding MUST NOT reach core's wrappers through this Driver's own package
  root; that root carries no wrapper tree.
- A binding MUST NOT assume a single installation shape — the operator override,
  the core-repo dogfooding checkout, the project-scope clone, and the user-scope
  clone are all valid.
- A candidate path counts as resolved only on positive evidence that it carries
  core's prose. Existence of the directory alone is not evidence.
- Resolution failure MUST be surfaced, never worked around. The Driver MUST NOT
  install anything on the user's behalf in response to a failed resolution.

## Guard constraints

- The guard MUST catch its own errors internally rather than relying on the
  runtime's default, because the pi default is fail-CLOSED and the required
  discipline is fail-OPEN.
- The guard MUST block only on positive identification of a forbidden
  invocation. An unrecognized write form, an unparseable segment, or a probe
  that cannot run is a pass-through, not a block.
- The guard MUST NOT be extended into a general policy engine. Adding a block
  predicate, removing one, or changing the posture routes through a
  propose-change cycle against
  `livespec/SPECIFICATION/contracts.md` §"Driver-shipped hooks", which owns the
  discipline; only the mechanical detection internals — segment tokenization,
  the wrapper-stripping set, the primary-checkout probe — are Driver
  implementation detail and MAY be tuned without a spec cycle, provided the
  posture holds.
- The guard MUST remain the ONLY first-party extension in this package. An
  operation binding MUST NOT be reimplemented as an extension.

## Structural-check constraints

- `dev-tooling/check-pi-package-structure` MUST be stdlib-only and runnable
  under a bare interpreter with no virtualenv, so it can gate commits and CI
  before any environment is provisioned.
- It is **fail-closed**: it exits non-zero with one diagnostic per violation on
  stderr, and exits zero only when every assertion holds.
- It MUST assert against the tree that actually ships. The shared family
  Verifier for skill-invocation paths is scoped to the Claude plugin layout and
  VACUOUSLY SKIPS over a pi package — returning success having inspected
  nothing — which is the entire reason this repo-local analogue exists. A check
  that cannot fail on this repo's layout is not a gate.

## Forbidden patterns

- `uv run`, a literal `.claude-plugin/scripts` path, or this Driver's own
  package root in any fenced wrapper invocation inside a `SKILL.md`.
- Any reference to `.claude-plugin/skills/*` in a binding, or any requirement
  that such a tree exist.
- Copying core's operation prose, wrapper files, or built-in templates into this
  repo.
- An extra skill directory, a missing binding, or a `SKILL.md` whose frontmatter
  `name` disagrees with its directory or whose `description` is empty.
- Shipping a pi manifest that declares a resource directory the package does not
  contain.
- Claiming a mutating operation while the guard extension is not loaded.
- Auto-activating `prune-history` from a generic mention of history.
- Committing or pushing at the primary checkout; passing a hook-bypass flag to a
  commit or push; editing tracked files outside a dedicated worktree.
- Claiming pi-native support from the presence of package entries alone; the
  acceptance evidence is a live drive, per
  `non-functional-requirements.md` §"Scenarios".
