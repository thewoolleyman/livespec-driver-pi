# livespec-driver-pi — repo orientation

This repo is the **pi Driver** for the livespec family: the thin,
agent-runtime-specific bindings through which a human drives the livespec
spec lifecycle interactively under the **pi** coding agent (per livespec
`SPECIFICATION/spec.md` §"Contract + reference implementations
architecture"). It is the pi-runtime analogue of `livespec-driver-claude`
and `livespec-driver-codex`, and it is deliberately small. Everything
substantive — the harness-neutral driving prose, the reference spec-side
CLIs, the JSON schemas, the built-in templates — ships with livespec core
(`thewoolleyman/livespec`); this repo only binds that material to the pi
runtime.

The authoritative contracts this repo implements were ratified as livespec
core **v208**:

- `livespec/SPECIFICATION/contracts.md` §"Plugin distribution" —
  how the pi Driver is packaged and installed.
- `livespec/SPECIFICATION/contracts.md` §"Driver-shipped hooks" —
  the pi Driver ships **exactly one** sanctioned extension, the
  `tool_call`-blocking footgun guard, and **no auto-memory guard**.
- `livespec/SPECIFICATION/non-functional-requirements.md`
  §"pi dogfooding compatibility", §"pi dogfooding contracts",
  §"pi dogfooding constraints".

## What this repo ships

Eight thin pi skills, named `livespec-<operation>` and invoked as
`/skill:livespec-<operation>`:

| Skill | Operation |
|---|---|
| `livespec-seed` | author the initial natural-language spec |
| `livespec-propose-change` | file a proposed change against the spec |
| `livespec-critique` | surface issues in the spec |
| `livespec-revise` | accept or reject pending proposed changes |
| `livespec-doctor` | run static + LLM-driven validation |
| `livespec-prune-history` | collapse old `history/vNNN/` entries |
| `livespec-next` | rank the next spec-side action |
| `livespec-help` | overview + routing to the right sub-command |

Plus the ONE sanctioned pi extension: a TypeScript `tool_call`-blocking
**footgun guard**, which per §"Driver-shipped hooks" must be in place
before any mutating operation is claimed.

## The one design rule that matters here

Each binding is thin and self-contained:

1. **Resolve `<core-root>`** — the livespec CORE plugin root. This Driver's
   own plugin root carries no `prose/` and no `scripts/`.
2. **Read the prose completely** — `<core-root>/prose/<name>.md` is the
   complete harness-neutral driving prose; the binding executes it, and
   MUST read it fully before acting.
3. **Dispatch the config-named CLI** — the governed project's
   `.livespec.jsonc` `spec_clis.<key>` argv, or core's reference default
   under `<core-root>/scripts/bin/`, with explicit argv.

Hard prohibitions from §"pi dogfooding compatibility": a binding MUST NOT
copy operation prose, wrapper files, or built-in templates, and MUST NOT
point at `.claude-plugin/skills/*` — core intentionally ships no
`.claude-plugin/skills/` tree.

Edit livespec core's `prose/<name>.md` for BEHAVIOR changes; edit the
bindings here only for pi-runtime mechanics.

## Layout (current)

| Path | Purpose |
|---|---|
| `skills/livespec-<operation>/SKILL.md` | The eight thin operation bindings. pi-runtime mechanics only: resolve `<core-root>`, read core's prose in full, dispatch the config-named CLI. |
| `lib/resolve-core-root.sh` | The single realization of the core-root resolution chain, called by all eight bindings. |
| `extensions/livespec-footgun-guard.ts` | The ONE sanctioned first-party pi extension — the `tool_call`-blocking footgun guard. |
| `package.json` | The pi package manifest (`pi.skills`, `pi.extensions`, the `pi-package` keyword). Its `$.version` is release-please-managed via `extra-files`. |
| `SPECIFICATION/` | This repo's own live livespec spec (dogfooded), governing the Driver-owned seam only: the pi package manifest, the eight-binding set, the core-root resolution chain, config-named CLI dispatch, and the footgun-guard extension. It defers to livespec core by citation and never restates the upstream contract. |
| `tests/dev-tooling/` | pytest mirror of `dev-tooling/`, holding the 100%-coverage suite for both repo-local structural checks. |
| `tests/heading-coverage.json` | The heading-coverage map. Every `## ` H2 in the spec tree needs an entry; co-edit it in the SAME revise payload that changes an H2 set. |
| `.livespec.jsonc` | Project-local livespec config: template, spec_root, active orchestrator plugin, the Driver `compat` pin against core, the declared harnesses, and the per-repo beads tenant connection block. |
| `dev-tooling/` | The family-standard enforcement scaffolds: the `just check` aggregate runner, the pre-push gate, the staged-ruff autofixer, the factory-branch workflow guard, and the two repo-local structural checks (the spec-governance default-block gate and `check-pi-package-structure`). The worktree-discipline pack and the commit-refuse hooks are NOT tracked here — `just bootstrap` installs both from the shared `livespec-dev-tooling` package. |
| `justfile`, `lefthook.yml`, `check-targets.txt`, `pyproject.toml` | Family-standard task runner, git-hook config, aggregate target list, and dev-tooling pins. |
| `.github/` | Per-target matrix CI plus the seven fleet shim / release-automation workflows, and the closed-loop Honeycomb telemetry export script. |
| `.claude/` | Project-scope Claude plugin enablement (`settings.json`) and the `CLAUDE.md` → `AGENTS.md` symlink. |
| `.ai/` | Progressive-load agent guidance: repo-specific operational notes that are too situational for this file and must not live in harness-local memory. Referenced from §"Progressive guidance" below, which is what makes `check-agents-ai-references-resolve` non-vacuous here. |
| `.mise.toml`, `.python-version`, `.gitignore` | Family-standard toolchain configuration. |

## Bootstrap status

This repo is mid-bootstrap (plan `bootstrap-pi-driver`, epic
`livespec-g5h5ff` in the livespec core ledger). Read this section before
assuming a piece is missing by accident.

**Present:**

- The Python toolchain (mise pins, uv-managed interpreter + dev group,
  ruff/pyright/pytest/coverage policy, the `[tool.livespec_dev_tooling]`
  layout role keys).
- The enforcement wiring: `justfile` (sole entry point), `lefthook.yml`,
  `check-targets.txt` carrying the full canonical block plus the private
  extras, and the `dev-tooling/` scripts.
- All eight fleet workflows and release automation (matrix CI, the
  release-dispatch producer shim, the bump-pin and pin-freshness receiving
  shims, release-park, release-please, fast-forward-release-branch,
  auto-enable-merge) plus the CI telemetry export.
- `.livespec.jsonc` and the project-scope `.claude/` configuration.
- **The beads tenant.** `.beads/config.yaml` (committed; TCP server-mode
  connection to the `livespec-driver-pi` Dolt tenant) plus the gitignored,
  regenerable `metadata.json`, landed in `183321d`.
- **The pi package surface.** The eight `livespec-<operation>` SKILL.md
  bindings, the shared `lib/resolve-core-root.sh` resolver, the sanctioned
  TypeScript footgun-guard extension, and the `package.json` pi manifest —
  with `release-please-config.json` carrying the `extra-files` JSON updater
  for the manifest's `$.version`, so it tracks releases.
- **`check-pi-package-structure`**, the repo-local structural gate over that
  surface, wired into the justfile, `check-targets.txt`, and the CI matrix. It
  exists because the shared `check-skill-invocation-paths` Verifier is scoped
  to `.claude-plugin/skills/` and therefore VACUOUSLY SKIPS in a pi package —
  it returns 0 having inspected nothing. There is NO shared
  `check-plugin-structure` module in `livespec-dev-tooling` (the earlier note
  here naming one was mistaken); this repo-local check is the analogue.
- **The `tests/` tree**, mirroring `dev-tooling/`, at 100% coverage — which is
  what makes `check-coverage` / `check-per-file-coverage` meaningful rather
  than green over an empty measurement.
- **The dogfooded `SPECIFICATION/` tree**, seeded at `v001` through livespec
  core's own seed operation, governing the Driver-owned seam only. Its
  companion wiring landed in the same pass: `dev-tooling/check-doctor-static.sh`,
  the `check-doctor-static` justfile recipe and `check-targets.txt` entry, the
  dedicated CI job (which checks livespec core out at the release tag
  `.livespec.jsonc` pins, since the checker ships with CORE), and — the part a
  forgotten pass silently loses — that job's entry in `ci-green`'s `needs:`
  list.
- **`tests/heading-coverage.json`**, one entry per spec `## ` H2. Every entry is
  a `TODO` today; the `scenarios.md` reasons name the INTEGRATION tier
  explicitly, which `check-heading-coverage` requires for a scenario heading —
  a reason that merely cites the implementing work-item fails the check.
- **The citation allowlist.** `.livespec.jsonc` carries `external_references`
  for the upstream sections this spec cites, plus a `cross_repo_targets`
  entry for `livespec`. Doctor-static re-reads the real upstream file when that
  clone is resolvable, so a renamed upstream section fails here instead of
  rotting silently. Adding a new upstream citation to the spec means adding it
  to that list in the same change.
- **Branch protection**, verified live: `master` requires exactly one status
  context, `ci-green`, with admin enforcement and linear history on and
  strict/up-to-date OFF. That single context is why adding a CI job without
  adding it to `ci-green`'s `needs:` list stops gating silently.

**Pending, in roughly this order:**

1. **The fleet GitHub App installation grant** (MAINTAINER-ONLY). The three
   repo secrets the sibling Drivers carry — `APP_ID`, `APP_PRIVATE_KEY`
   (normalized single-line PEM), `HONEYCOMB_GITHUB_CI_INGEST_KEY_LIVESPEC` —
   ARE all set (verified 2026-08-15 via `gh secret list`; an earlier revision
   of this section claimed they were missing, which was true before
   2026-08-15T14:43Z and is stale now). The remaining gap is that the fleet
   GitHub App installation `131208965` does not include this repository, so
   `Mint App installation token` 404s and `release-please.yml`,
   `auto-enable-merge.yml`, and `fast-forward-release-branch.yml` fail on
   every trigger (verified against the 2026-08-15T15:37Z run). None of them
   gate `ci-green`, so this does not block merges — it silently disables the
   release train and the auto-merge path. Once the grant lands: first release
   cut (multiple `feat:` commits pending) → `release` branch → the `@release`
   install channel exists.

2. **Fleet-manifest registration** in livespec core's
   `.livespec-fleet-manifest.jsonc`, and the `livespec-sibling` GitHub topic.
   These happen **LAST**, once everything above is done.

**Deliberately not wired yet, because its subject does not exist:** the
CLI-end-to-end harness. A gate is wired by the pass that creates what it guards
— one shipped ahead of its subject is a red CI job that teaches nothing.
(`check-doctor-static` was the other entry here; the `SPECIFICATION/` seed pass
created its subject and wired it in the same change.)

The CLI-end-to-end gate deserves its own sentence, because "the subject does not
exist" is not the whole reason. The sibling Drivers' `tests/e2e-cli/` suites
drive a REAL agent runtime end-to-end; the pi analogue would have to launch the
pi CLI against a live model. That is a live-credential, live-network dependency,
and the honest options are to wire it as a `real_only`-marked suite that CI skips
(which gates nothing) or to leave it out until the acceptance drive that
§"pi dogfooding constraints" already requires is run. It is left out. Do NOT
substitute a mocked stand-in and call the gate satisfied — a fake pi CLI would
verify only the fake.

**Known upstream gap.** `.livespec.jsonc` declares `claude` and `codex` as
EXEMPT harnesses but does not declare this repo's own `pi` harness. The
shared `check-plugin-resolution` Verifier fails closed on an unknown
harness key, and its `_KNOWN_HARNESSES` set in `livespec-dev-tooling` is
currently `{"claude", "codex"}`. Extending that set (plus a pi runner in
`_build_live_runners`) is upstream work in `livespec-dev-tooling`, filed
there as `livespec-dev-tooling-a924`; adding the
`"pi": { "status": "supported", ... }` entry here is the follow-up that
lands with it.

## Progressive guidance

Repo-specific operational notes live under `.ai/`, loaded on demand rather
than inlined here (livespec core contracts §"Fleet agent-instruction core"
— the progressive-disclosure convention; every reference below MUST
resolve, which `check-agents-ai-references-resolve` enforces).

- Read `.ai/beads-tenant.md` before running live `bd` or
  livespec-orchestrator-beads-fabro commands against this repo's beads
  tenant — the `-C` wrong-tenant hazard and the never-print rule for
  `BEADS_DOLT_PASSWORD`.
- Read `.ai/pi-runtime.md` before authoring a SKILL.md binding or driving
  the `pi` CLI unattended — the fatal unquoted `: ` in frontmatter, and
  `pi -p` exiting 0 on a failed model call.

## Repository mutation protocol

Every repo change uses a **worktree → PR → merge → cleanup** path. Leaving
dirty state, committing on the primary checkout, or asking whether to commit
are failures of the workflow, not acceptable stopping points.

The bootstrap-phase exception that let early passes commit directly to `master`
is CLOSED: the commit-refuse hooks are armed on the primary checkout and
`master` is protected behind `ci-green`. The ordinary discipline now applies
without exception:

1. Confirm the primary checkout before editing (a primary checkout's git-dir
   equals its git-common-dir; a secondary worktree's differs).
2. Create a dedicated worktree from `master` under the per-user root
   `~/.worktrees/livespec-driver-pi/<branch>` — never as a peer of the clones
   under `/data/projects`:

   ```bash
   mise exec -- git -C /data/projects/livespec-driver-pi worktree add \
       -b <branch> "$HOME/.worktrees/livespec-driver-pi/<branch>" master
   ```

3. Use `mise exec -- git commit ...` / `mise exec -- git push ...` so the
   mise-managed lefthook hooks actually run. **Never** pass `--no-verify`;
   if a hook fails, fix the cause or halt with the failure.
4. Open a PR, wait for `ci-green`, and merge through the PR under the repo's
   rebase-merge discipline.
5. After merge, refresh the primary checkout to `origin/master`, remove the
   feature worktree, delete the local branch, and verify clean status on
   `master`.

## Relationship to the family

- `livespec` — core: contract, prose, reference CLIs, templates.
- `livespec-driver-claude` — the Claude Code Driver.
- `livespec-driver-codex` — the Codex Driver (the donor scaffold this repo
  was adapted from).
- `livespec-driver-pi` (this repo) — the pi Driver.
- `livespec-dev-tooling` — the shared enforcement-check library every repo
  above pins.
- `livespec-orchestrator-beads-fabro` / `livespec-orchestrator-git-jsonl` —
  orchestrator plugins (work-item stores, gap and drift capture). A Driver
  has ZERO dependencies on them, and they have ZERO dependencies on any
  Driver (load-bearing invariant).
