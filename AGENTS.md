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

## What this repo will ship

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
| `.livespec.jsonc` | Project-local livespec config: template, spec_root, active orchestrator plugin, the Driver `compat` pin against core, the declared harnesses, and the per-repo beads tenant connection block. |
| `dev-tooling/` | The family-standard enforcement scaffolds: the `just check` aggregate runner, the pre-push gate, the staged-ruff autofixer, the factory-branch workflow guard, and the repo-local spec-governance default-block check. The worktree-discipline pack and the commit-refuse hooks are NOT tracked here — `just bootstrap` installs both from the shared `livespec-dev-tooling` package. |
| `justfile`, `lefthook.yml`, `check-targets.txt`, `pyproject.toml` | Family-standard task runner, git-hook config, aggregate target list, and dev-tooling pins. |
| `.github/` | Per-target matrix CI plus the seven fleet shim / release-automation workflows, and the closed-loop Honeycomb telemetry export script. |
| `.claude/` | Project-scope Claude plugin enablement (`settings.json`) and the `CLAUDE.md` → `AGENTS.md` symlink. |
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

**Pending, in roughly this order:**

1. **The eight `livespec-<operation>` pi skills** and the pi plugin/
   marketplace manifests. That pass MUST also: wire `check-plugin-structure`
   into the justfile, `check-targets.txt`, and the CI matrix; and add the
   `extra-files` JSON updater entry to `release-please-config.json` pointing
   at the new plugin manifest's `$.version`, or the manifest version silently
   stops tracking releases.
2. **The TypeScript footgun-guard pi extension** plus its tests. That pass
   wires its own gate, and revisits `[tool.livespec_dev_tooling]`
   `source_trees` / `source_tree_prefixes` if it brings any Python with it.
3. **The dogfooded `SPECIFICATION/` seed.** That pass MUST also add
   `dev-tooling/check-doctor-static.sh`, the `check-doctor-static` justfile
   recipe and `check-targets.txt` entry, and the dedicated
   `check-doctor-static` CI job — including adding it to `ci-green`'s
   `needs:` list, which is where a forgotten job silently stops gating.
4. **The beads tenant** (`.beads/config.yaml` + the regenerable
   `metadata.json`) — provisioned by the supervising session, not by repo
   work. `.livespec.jsonc` already carries the matching connection block.
5. **The three repo secrets** the sibling Drivers carry, none of which exist
   here yet — verified live against `livespec-driver-codex`, which has all
   three. Until they are set, four workflows fail on every trigger:
   `release-please.yml`, `auto-enable-merge.yml`, and
   `fast-forward-release-branch.yml` all die at `Mint App installation
   token` with `Input required and not supplied: app-id`, and
   `export-telemetry` cannot reach Honeycomb. None of them gate `ci-green`,
   so this does not block merges — it silently disables the release train
   and the auto-merge path.

   | Secret | Used by |
   |---|---|
   | `APP_ID` | release-please, auto-enable-merge, fast-forward-release-branch |
   | `APP_PRIVATE_KEY` | the same three |
   | `HONEYCOMB_GITHUB_CI_INGEST_KEY_LIVESPEC` | the CI telemetry export |

6. **Branch protection** with `ci-green` as the sole required context.
7. **Fleet-manifest registration** in livespec core's
   `.livespec-fleet-manifest.jsonc`, and the `livespec-sibling` GitHub topic.
   These happen **LAST**, once everything above is done.

**Deliberately not wired yet, because their subjects do not exist:**
`check-plugin-structure`, `check-doctor-static`, and the shipped-hook /
CLI-end-to-end test gates. Each is wired by the pass that creates what it
guards — a gate shipped ahead of its subject is a red CI job that teaches
nothing.

**Known upstream gap.** `.livespec.jsonc` declares `claude` and `codex` as
EXEMPT harnesses but does not declare this repo's own `pi` harness. The
shared `check-plugin-resolution` Verifier fails closed on an unknown
harness key, and its `_KNOWN_HARNESSES` set in `livespec-dev-tooling` is
currently `{"claude", "codex"}`. Extending that set (plus a pi runner in
`_build_live_runners`) is upstream work in `livespec-dev-tooling`; adding
the `"pi": { "status": "supported", ... }` entry here is the follow-up that
lands with it.

## Repository mutation protocol

Every repo change uses a **worktree → PR → merge → cleanup** path. Leaving
dirty state, committing on the primary checkout, or asking whether to commit
are failures of the workflow, not acceptable stopping points.

The one exception is the current bootstrap phase itself, which commits
directly to `master` because no branch protection and no commit-refuse hook
are installed yet. Once `just bootstrap` has run and branch protection is
enabled, the ordinary discipline applies without exception:

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
