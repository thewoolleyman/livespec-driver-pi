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

**And nothing else — deliberately.** pi also supports PROMPT TEMPLATES
(`pi.prompts` in the manifest, or a conventional `prompts/` directory),
which would give bare `/livespec-<operation>` commands alongside the
`/skill:` form. This Driver does NOT ship them. The question was deferred
during bootstrap "until the live end-to-end exercise", that exercise
happened (`livespec-ewqnqm` closed on real structured JSON from
`pi -p "/skill:livespec-next"`), and the answer on the evidence is no:

- A prompt template is a Markdown snippet that EXPANDS into prompt text.
  Writing eight of them means writing eight descriptions of what each
  operation does — a second place where the operation's intent lives.
  This repo's one design rule is that a binding never copies operation
  prose; a prompt layer would reintroduce exactly that drift surface for
  six characters of typing.
- The Driver surface is fixed by livespec core contracts §"Plugin
  distribution" as the eight operations. A second invocation surface is a
  contract question, not free ergonomics.
- Nothing has asked for it. The deferral's reconsider condition fired
  and produced no evidence of friction, because the only pi consumer
  today is this repo dogfooding itself.

RE-OPEN when a real pi consumer — an adopter, or a maintainer session
that is not this repo's own dogfooding — reports the `/skill:` prefix as
actual friction. That is a demand signal, not a calendar trigger, and it
is cheap to satisfy if it arrives: the templates would be additive and
would change no existing surface.

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
| `tests/dev-tooling/` | pytest mirror of `dev-tooling/`, holding the 100%-coverage suite for the repo-local structural checks. |
| `tests/extensions/` | The behavioral suite for the footgun-guard extension, run by `check-extension-quality` under `node --test`. TypeScript, not pytest — it drives the guard's exported `decide()` with no pi runtime and nothing mocked. |
| `tests/test_shell_quality_gate.py` | The shell-quality positive control: proves `check-shell-quality` can go RED, so a green run means something. |
| `tests/heading-coverage.json` | The heading-coverage map. Every `## ` H2 in the spec tree needs an entry; co-edit it in the SAME revise payload that changes an H2 set. |
| `.livespec.jsonc` | Project-local livespec config: template, spec_root, active orchestrator plugin, the Driver `compat` pin against core, the declared harnesses, and the per-repo beads tenant connection block. |
| `dev-tooling/` | The family-standard enforcement scaffolds: the `just check` aggregate runner, the pre-push gate, the staged-ruff autofixer, the factory-branch workflow guard, and the repo-local gates (`check-spec-governance-default-block`, `check-pi-package-structure`, `check-pi-drive-output`, `check-extension-quality`, `check-doctor-static`). The worktree-discipline pack and the commit-refuse hooks are NOT tracked here — `just bootstrap` installs both from the shared `livespec-dev-tooling` package. |
| `justfile`, `lefthook.yml`, `check-targets.txt`, `pyproject.toml` | Family-standard task runner, git-hook config, aggregate target list, and dev-tooling pins. |
| `.github/` | Per-target matrix CI plus the seven fleet shim / release-automation workflows, and the closed-loop Honeycomb telemetry export script. |
| `.claude/` | Project-scope Claude plugin enablement plus the dev-time agent hooks (`settings.json`), and the `CLAUDE.md` → `AGENTS.md` symlink. The root `CLAUDE.md` symlink is the second half of that pair. |
| `.ai/` | Progressive-load agent guidance: repo-specific operational notes that are too situational for this file and must not live in harness-local memory. Referenced from §"Progressive guidance" below, which is what makes `check-agents-ai-references-resolve` non-vacuous here. |
| `tsconfig.json`, `package-lock.json` | Typecheck-only TS configuration (no emit; `erasableSyntaxOnly` keeps the guard loadable under Node's type stripping) and the npm lockfile `check-extension-quality` reconstructs `node_modules/` from. |
| `.mise.toml`, `.python-version`, `.gitignore` | Family-standard toolchain configuration. `.mise.toml` pins `node` too, for the TypeScript extension's gate. |

## Post-bootstrap status

The bootstrap is COMPLETE. Plan `bootstrap-pi-driver` (epic
`livespec-g5h5ff`, livespec core ledger) closed 2026-08-18 with an
independent completeness review. The successor thread is
`plan/bootstrap-pi-driver-wrapup/`, epic `livespec-driver-pi-jvvhxi` in
THIS repo's own tenant, which carries the post-bootstrap audit's findings
and the upstream-prevention work.

Read this section before assuming a piece is missing by accident — and
read the ledger before assuming this section is current. Status is
ledger-held; what follows is orientation, not the source of truth:

```bash
/usr/local/bin/with-livespec-env.sh -- bd -C /data/projects/livespec-driver-pi list --status all
```

**Present and working:**

- The Python toolchain (mise pins, uv-managed interpreter + dev group,
  ruff/pyright/pytest/coverage policy, the `[tool.livespec_dev_tooling]`
  layout role keys) and, since the extension-quality pass, a `node` pin
  with `package.json` / `package-lock.json` as its npm-side analogue.
- The enforcement wiring: `justfile` (sole entry point), `lefthook.yml`,
  `check-targets.txt` carrying the full canonical block plus the private
  extras, and the `dev-tooling/` scripts.
- All eight fleet workflows and release automation, and they are not
  merely present — they RUN. The fleet GitHub App installation grant
  landed 2026-08-16, and `release-please`, `auto-enable-merge`,
  `fast-forward-release-branch`, and the release-dispatch fan-out have
  all succeeded since. The `release` branch exists, so the `@release`
  install channel is live; v0.3.0 through v0.5.0 are cut, each carrying
  the `package.json` `$.version` bump via `release-please-config.json`'s
  `extra-files` updater.
- **Fleet-manifest registration and the GitHub topic**, the two
  register-LAST obligations: `.livespec-fleet-manifest.jsonc:57` in
  livespec core carries `{ "repo": "livespec-driver-pi", "class":
  "driver-plugin" }` (commit `cb1a8409`), and the `livespec-sibling`
  topic is set.
- **The pi harness declaration.** `.livespec.jsonc` declares `"pi": {
  "status": "supported" }`; the shared `check-plugin-resolution`
  Verifier's `_KNOWN_HARNESSES` set includes `pi` as of
  livespec-dev-tooling v1.28.x, so the declaration is EXERCISED rather
  than failing closed. The upstream items that blocked it
  (`livespec-dev-tooling-a924`, `-phb3`) are closed.
- `.livespec.jsonc`, the project-scope `.claude/` configuration, and the
  citation allowlist (`external_references` plus a `cross_repo_targets`
  entry for `livespec`). Doctor-static re-reads the real upstream file
  when that clone is resolvable, so a renamed upstream section fails here
  instead of rotting silently. Adding a new upstream citation to the spec
  means adding it to that list in the same change.
- **The beads tenant.** `.beads/config.yaml` (committed; TCP server-mode
  connection to the `livespec-driver-pi` Dolt tenant) plus the gitignored,
  regenerable `metadata.json`, landed in `183321d`. Operational hazards:
  `.ai/beads-tenant.md`.
- **The pi package surface.** The eight `livespec-<operation>` SKILL.md
  bindings, the shared `lib/resolve-core-root.sh` resolver, the sanctioned
  TypeScript footgun-guard extension, and the `package.json` pi manifest.
- **`check-pi-package-structure`**, the repo-local structural gate over that
  surface. It exists because the shared `check-skill-invocation-paths`
  Verifier is scoped to `.claude-plugin/skills/` and therefore VACUOUSLY
  SKIPS in a pi package — it returns 0 having inspected nothing. There is NO
  shared `check-plugin-structure` module in `livespec-dev-tooling`; this
  repo-local check is the analogue.
- **`check-extension-quality`**, the gate over the TypeScript footgun
  guard: `tsc --noEmit` (with `erasableSyntaxOnly`, so the guard is proven
  loadable under Node's type stripping) plus a behavioral suite driving
  the guard's exported `decide()`. It exists because
  `check-pi-package-structure`'s assertions are over the file's TEXT and
  survive both a guard that stopped compiling and a predicate that
  inverted — both mutations were confirmed to pass it and to be killed by
  the suite. The sibling Drivers get this coverage free from the Python
  gates; a TypeScript guard rides none of them.
- **The `tests/` tree** at 100% coverage — which is what makes
  `check-coverage` / `check-per-file-coverage` meaningful rather than green
  over an empty measurement — including the shell-quality positive control
  that proves that gate can go red.
- **The dogfooded `SPECIFICATION/` tree**, seeded at `v001`, with
  `dev-tooling/check-doctor-static.sh`, its justfile recipe and
  `check-targets.txt` entry, and its dedicated CI job (which checks livespec
  core out at the release tag `.livespec.jsonc` pins, since the checker ships
  with CORE) — including that job's entry in `ci-green`'s `needs:` list,
  which is the part a forgotten pass silently loses.
- **`tests/heading-coverage.json`**, one entry per spec `## ` H2. Every entry
  is a `TODO` today; the `scenarios.md` reasons name the INTEGRATION tier
  explicitly, which `check-heading-coverage` requires for a scenario heading —
  a reason that merely cites the implementing work-item fails the check.
- **The `.ai/` guidance tree** (`beads-tenant.md`, `pi-runtime.md`),
  referenced from §"Progressive guidance" below. Before it landed,
  `check-agents-ai-references-resolve` was armed and structurally
  incapable of firing: it is a dangling-REFERENCE check, and a repo that
  references zero `.ai/` files passes by construction.
- **Branch protection**, verified live: `master` requires exactly one status
  context, `ci-green`, with admin enforcement and linear history on and
  strict/up-to-date OFF. That single context is why adding a CI job without
  adding it to `ci-green`'s `needs:` list stops gating silently.

**Open, each with a named carrier under epic `livespec-driver-pi-jvvhxi`:**

- `CI_RUNNER_LABELS` is UNSET, so every matrix job falls through
  `fromJSON(vars.CI_RUNNER_LABELS || '["ubuntu-latest"]')` onto
  GitHub-hosted runners — this repo is silently opted out of the fleet ARC
  k3s pool, and green CI makes that invisible. Carrier
  `livespec-driver-pi-pbmnua` (maintainer-only: it needs a scale set and a
  repo-variable write). See §"CI runner routing" below before touching it.
- The small parity items — the `file_lloc_hard_gate` decision and the
  `.claude/settings.json` dev-time-hooks decision: carrier
  `livespec-driver-pi-zazr4d`.
- The adopter `.pi/settings.json` audit (openbrain, resume, homelab,
  dolt-server): carrier `livespec-driver-pi-no6in2`.
- The prompt-template layer (`/livespec-<op>` bare commands) adopt-or-
  re-defer decision: carrier `livespec-driver-pi-jyuvlv`.
- Upstream prevention, so the next hand-built Driver does not repeat these
  omissions: a maintained per-class obligation list into livespec core
  (`livespec-driver-pi-65yari`), `external_references` coverage in the
  copier template (`livespec-driver-pi-ybsp4p`), and the decision on
  whether `check-agents-ai-references-resolve` must detect `.ai/` ABSENCE
  (`livespec-driver-pi-nwsjym`). These land in the livespec and
  livespec-dev-tooling tenants, not here.
- `livespec-driver-pi-1zt` (blocked): the Fabro sandbox `gh` wrapper
  hard-calls a `mint_app_token.py` that target repos do not vendor. Fleet-
  wide; it blocks factory dispatch FROM this repo, not merges.

**Deliberately not wired, and not an oversight:** the CLI-end-to-end
harness. A gate is wired by the pass that creates what it guards — one
shipped ahead of its subject is a red CI job that teaches nothing. But
"the subject does not exist" is not the whole reason here. The sibling
Drivers' `tests/e2e-cli/` suites drive a REAL agent runtime end-to-end;
the pi analogue would have to launch the pi CLI against a live model.
That is a live-credential, live-network dependency, and the honest
options are to wire it as a `real_only`-marked suite that CI skips (which
gates nothing) or to leave it out until the acceptance drive that
§"pi dogfooding constraints" already requires is run. It is left out. Do
NOT substitute a mocked stand-in and call the gate satisfied — a fake pi
CLI would verify only the fake. (`check-extension-quality` is NOT an
exception to this: it typechecks and unit-tests the guard's own decision
function, which needs no runtime at all.)

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

## Decision authority — when to ask, proceed, or self-resolve

Fleet-standard guidance, ported from
`livespec/AGENTS.md` §"When to ask, proceed, or self-resolve" and
`livespec-orchestrator-beads-fabro/AGENTS.md` §"Drive authorized work to
completion; do not over-ask". The default is to decide and report, not to
escalate.

**Why every governed member carries this.** On 2026-08-20 a track in this
fleet sat roughly sixteen hours parked on a picker whose option 1 was its own
recorded next action, and five self-decidable engineering calls were escalated
as standing maintainer questions. The investigation found the guidance was
real but partial: `AGENTS.md` is authored per repo and nothing propagates it,
so sessions in the repos that lacked it were reading a file that never told
them what they were allowed to decide.

- **Drive authorized work to completion; do not over-ask.** When the maintainer
  names a goal and says to finish or continue it, execute the WHOLE arc —
  implement, dispatch, PR, merge, iterate, archive — without pausing to confirm
  each already-authorized step. An operator-flow step that says "present
  options and let the user select" is satisfied by a standing directive once
  the goal is named; do not re-prompt. Default to acting, then reporting
  outcomes.
- **A recorded next action is an instruction, not a menu.** When a handoff, a
  work-item, or a plan timeline names exactly one next action, take it.
  Re-presenting it as option 1 of a picker is the stall shape above.
- **Research before gating.** If a question is answerable by reading the code,
  the spec, the docs, or by testing on a live system, do that, decide,
  implement, and report for objection. Reserve gates for genuine product or
  values calls, irreversible or outward-facing actions, and secret or
  host-mutation authorization.
- **Only ask on genuine doubt, one thing at a time.** Self-resolve trivial
  wording fixes, internal-consistency repairs, and items clearly aligned with
  established preferences, presenting each with its disposition. When a gate is
  warranted, ask exactly one question per turn.
- **One investigation, one finding, one question.** When a focused
  investigation surfaces unrelated discrepancies, finish the original question
  first and surface only the load-bearing finding; log side observations
  briefly. Cosmetic drift never blocks on its own.
- **Prescribed destructive ops are pre-authorized.** When a destructive git
  operation is the codified mechanism of an adopted workflow — the
  `git commit --amend` of the Red→Green step, for instance — the adoption is
  the authorization. Keep per-instance gating for ad-hoc `--amend`,
  force-push, `reset --hard`, or `branch -D` on unmerged branches.
- **An unratified filter inside a check is conformance, not ratification.**
  Narrowing, excluding, or filtering inside an enforcement check to match what
  the ratified spec already says is a conformance fix — implement it and report
  it. It only becomes a ratification question when the change would make the
  check assert something the spec does not.
- **A question you can answer with a recommendation is a finding, not a
  maintainer question.** If you can state the options, the costs, and which one
  you would pick, you have already done the deciding work. Decide it, record
  the reasoning where the work is tracked, and report it as decided.

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

## Dev-time agent hooks (Claude Code sessions working ON this repo)

`.claude/settings.json` wires two SHARED `livespec_dev_tooling` guards for
sessions editing this repository — distinct from
`extensions/livespec-footgun-guard.ts`, which is the SHIPPED pi-runtime
guard this Driver distributes to its users:

- `PreToolUse` (Bash) → `agent_hooks.pretooluse_background_guard`, which
  denies bare-backgrounding a gate command (`just check`, `git commit`,
  `git push`, the PR handoff). A backgrounded gate leaves the verdict only
  in tool output, so a killed task or a turn-end loses it; the sanctioned
  detached runner (`just gate-start` / `gate-wait`) is allowed instead.
- `SubagentStop` → `agent_hooks.subagent_stop_guard`.

Both are shared modules, so there is no repo-local hook body to drift.

**Deliberate divergence from livespec-driver-claude:** that repo ALSO wires
a third `PreToolUse` hook, a 276-line repo-local
`.claude/hooks/livespec_footgun_guard.py`. This repo does not, and should
not. Its footgun policy already exists here as first-party TypeScript,
gated by `check-extension-quality`; vendoring a second implementation of
the same four block predicates in a different language would give this repo
two policies to keep in sync, and the family has no shared module to
delegate to. The real backstops — the commit-refuse hooks and branch
protection — are unaffected either way.

## CI runner routing

Runner routing is a repo VARIABLE, never a workflow edit.

Every gating job in `ci.yml` resolves its runner from
`fromJSON(vars.CI_RUNNER_LABELS || '["ubuntu-latest"]')`. To route the
gating jobs at a conforming self-hosted host, SET the repo variable
`CI_RUNNER_LABELS` to that host's label; to return them to hosted
capacity, unset it or set it to `'["ubuntu-latest"]'`. Neither direction
needs a specification revision, and neither is a `.github/workflows/`
change — `check-no-workflow-edits` refuses implementation branches that
carry one, and the fleet App's `workflows` grant is withheld precisely so
routing cannot be "fixed" that way.

The hosted-capacity fallback is a merge-gate SAFETY property, not a
convenience. `master` requires exactly one status context, `ci-green`,
which `needs:` the check jobs. A job routed to self-hosted capacity that
is not there does not FAIL — it sits in `queued`, `ci-green` never
reports, and every merge waits on a check that will not arrive. That is
why the literal `'["ubuntu-latest"]'` fallback is repeated inline at each
`runs-on` rather than single-sourced through a job output: the fleet's
self-hosted routing guard parses `runs-on` values STATICALLY, so routing
hidden behind `needs.<job>.outputs.*` would read as "this workflow has no
self-hosted job" and silently disable the forbidden-trigger check.

CURRENT STATE: `CI_RUNNER_LABELS` is unset, so this repo runs on hosted
capacity and is silently opted out of the fleet ARC k3s pool that
`livespec-driver-codex` uses. Provisioning a pool and setting the
variable is maintainer-only work, tracked as `livespec-driver-pi-pbmnua`.
