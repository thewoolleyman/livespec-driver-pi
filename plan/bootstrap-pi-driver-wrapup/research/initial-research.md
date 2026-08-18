# bootstrap-pi-driver-wrapup — initial research (post-bootstrap audit)

Date: 2026-08-19. Successor plan to the archived `bootstrap-pi-driver`
thread (`/data/projects/livespec/plan/archive/bootstrap-pi-driver/`,
epic `livespec-g5h5ff`, closed 2026-08-18 with an independent COMPLETE
completeness review). This plan records everything the post-bootstrap
audit of `livespec-driver-pi` found missing or unfinished, plus the
upstream template/checklist changes needed so future new repos —
especially future runtime Drivers — do not repeat the omissions.

## Method

Three parallel investigations on 2026-08-19: (1) a tracked-file and
config inventory diff of this repo against `livespec-driver-claude`
(primary reference) and `livespec-driver-codex` (the donor scaffold);
(2) a full read of the archived plan record and its ledger timeline,
including deferral re-trigger status; (3) an inventory of the family's
`.ai/` guidance trees and of every upstream scaffolding artifact
(copier template, `just bootstrap` reconcile rows, fleet-membership
contract, installation docs).

Headline: the repo's plumbing is in much better shape than its own
AGENTS.md bootstrap-status section claims — all eight fleet workflows,
the full check-target block, justfile/lefthook/pyproject/livespec.jsonc
surfaces, and the CI job graph are structurally equivalent to the codex
donor. The real gaps are concentrated in (a) the shipped TypeScript
extension's quality gating, (b) the absent `.ai/` guidance tree, (c)
repo-side GitHub/CI configuration, (d) documentation rot, and (e) the
upstream scaffolding hole that produced all of the above.

## Findings — this repo (livespec-driver-pi)

### F1 (CRITICAL) — TypeScript footgun-guard extension is ungated

`extensions/livespec-footgun-guard.ts` (13 KB) is the Driver's entire
sanctioned-extension surface (core contracts §"Driver-shipped hooks"),
and the ONLY verification it has is `extension_violations()` in
`dev-tooling/check-pi-package-structure` (lines 195-209): substring/
regex assertions over the file text. A file that never compiles, or
whose guard logic is inverted, passes. There is no `tsconfig.json`, no
node/npm/bun pin in `.mise.toml` (which pins only uv/just/lefthook/
shellcheck), no TS lint/format config, and no test anywhere. Both
siblings' Python guards ride lint/format/types/coverage automatically
and carry dedicated behavioral suites (claude:
`tests/hooks/test_livespec_footgun_guard.py`; codex adds
`test_footgun_shell.py`, `test_footgun_tmux.py`,
`test_footgun_primary_checkout.py`,
`test_footgun_guard_variable_paths.py`) driven by a `check-hooks`
recipe invoking the guard as a subprocess with a JSON stdin payload.

The archived plan's own deferral record corroborates: "the
livespec-footgun-guard.ts extension's runtime block predicates were not
exercised by the audit (… its behavior under an actual denied tool call
is unverified) — deferred to a future pass". This is that pass.

Scope note: the repo's standing argument against a live pi-CLI e2e
suite (live-credential dependency; "a fake pi CLI would verify only the
fake") does NOT extend here. A `tsc --noEmit` gate plus a unit suite
over the guard's decision function needs no live model and no
credentials. Carrier: add a node toolchain pin, `tsconfig.json`, a
`check-extension-types` (or equivalent) gate wired into justfile +
check-targets.txt + CI (`ci-green.needs` included), and a behavioral
unit suite over the block predicates.

### F2 (IMPORTANT) — no `.ai/` guidance tree; the gate over it is vacuous

This repo has zero `.ai/` files and zero references to any.
`check-agents-ai-references-resolve` is target #1 in
`check-targets.txt` and runs in CI, but by its own docstring "a repo
whose AGENTS.md references zero `.ai/` files passes" — the gate is
armed and structurally incapable of firing. Root cause: the donor
(`livespec-driver-codex`) has no `.ai/` tree either; only
`livespec-driver-claude` grew one (`.ai/beads-tenant.md`, 26 lines).

That one file covers exactly the hazard pi shares: a per-repo Dolt
tenant reached through the credential wrapper
(`/usr/local/bin/with-livespec-env.sh -- bd -C <repo> …`), where
getting `-C` wrong writes to the WRONG repo's ledger, and where
`BEADS_DOLT_PASSWORD` must never be printed. Carrier: author
`.ai/beads-tenant.md` (pi analogue) plus an AGENTS.md reference per
core contracts §"Fleet agent-instruction core" (progressive-disclosure
convention, references MUST resolve). Consider whether any pi-specific
operational gotchas earned during bootstrap (frontmatter colon-space
fatality; `pi -p` exiting 0 on model-call failure — classify from
output shape via `dev-tooling/check-pi-drive-output`) belong in a
second topic file rather than inline in AGENTS.md.

### F3 (IMPORTANT) — `CI_RUNNER_LABELS` repo variable unset

`gh variable list -R thewoolleyman/livespec-driver-pi` is empty; codex
carries `CI_RUNNER_LABELS=["livespec-driver-codex-k3s"]`. Every matrix
job in `ci.yml` falls through `fromJSON(vars.CI_RUNNER_LABELS ||
'["ubuntu-latest"]')` onto GitHub-hosted runners, silently opting this
repo out of the fleet ARC k3s pool. Green CI makes it invisible.
Carrier: provision a `livespec-driver-pi-k3s` scale set (or confirm the
fleet's shared pool naming) and set the variable — a repo-config
action, not a workflow edit (`check-no-workflow-edits` forbids the
latter).

### F4 (IMPORTANT) — AGENTS.md lacks the `## CI runner routing` section

Both siblings end AGENTS.md with it, documenting that runner routing is
a repo VARIABLE and never a workflow edit, with a pointer to the
cutover record. It is the doc that stops the next session from "fixing"
routing by editing `ci.yml` and tripping the guard. Carrier: add the
section (naturally lands with F3).

### F5 (IMPORTANT) — no shell-quality positive-control test

`check-shell-quality` is wired (justfile:370, check-targets.txt) over
five first-party shell files (`lib/resolve-core-root.sh` + four
`dev-tooling/` scripts), but nothing proves the gate is non-vacuous.
Codex has `tests/test_shell_quality_gate.py` (builds a throwaway repo,
asserts the checker fires); claude has
`tests/hooks/test_shell_quality_migration.py`. The codex test is
largely portable. Carrier: port it.

### F6 (IMPORTANT) — documentation rot in AGENTS.md and release-please.yml

- AGENTS.md §"Bootstrap status" still lists as pending: the fleet App
  installation grant (landed 2026-08-16), fleet-manifest registration
  (`.livespec-fleet-manifest.jsonc:57`, commit `cb1a8409`), the
  `livespec-sibling` topic (set), and describes the pi harness as an
  undeclared upstream gap (declared supported in `.livespec.jsonc` line
  ~103 since `500faad`; upstream `livespec-dev-tooling-a924` and
  `-phb3` both closed). The section's whole purpose is to be read
  before assuming a piece is missing; it now actively misleads.
- `.github/workflows/release-please.yml` still carries "This repo ships
  no plugin manifest yet, so it declares no extra-files; the pass that
  lands the pi plugin manifest MUST add the matching extra-files entry"
  — that pass landed (`release-please-config.json` declares the
  `package.json` `$.version` updater; releases 0.2.0→0.3.0 cut). A
  future reader could act on the stale instruction and duplicate the
  entry. NOTE: workflow edits require the maintainer seam
  (`check-no-workflow-edits` + the withheld `workflows` grant) — this
  carrier must ride an authorized workflow-editing pass.

Carrier: one doc-refresh pass rewriting §"Bootstrap status" to
post-bootstrap reality (and renaming it, e.g. "Post-bootstrap status"),
plus the workflow-comment fix routed through the sanctioned seam.

### F7 (NICE-TO-HAVE) — root `CLAUDE.md → AGENTS.md` symlink missing

Both siblings track BOTH symlinks (root `CLAUDE.md -> AGENTS.md` and
`.claude/CLAUDE.md -> ../AGENTS.md`); pi tracks only the second.
Trivial carrier.

### F8 (DECISION) — `file_lloc_hard_gate = false`

`pyproject.toml` `[tool.livespec_dev_tooling]` sets it `false`; both
siblings set `true`. The repo now has first-party Python (three
checkers + tests) as a real subject. Carrier: arm it and see whether it
already passes; if deliberate, record why beside the key.

### F9 (DECISION) — `.claude/settings.json` dev-time agent hooks

Claude-driver wires `PreToolUse` → dev-tooling
`pretooluse_background_guard` + a footgun-guard hook and
`SubagentStop` → `subagent_stop_guard` for sessions working ON the
repo. Pi's file is byte-identical to codex's, which also lacks them —
defensible as-is, but this repo IS dogfooded under Claude Code (this
audit ran under it), so the guards would bite. Carrier: a deliberate
decision, then either adopt (likely alongside a
`.claude/hooks/livespec_footgun_guard.py` install, per the claude
layout) or record the reason for divergence.

## Findings — loose ends from the archived plan record

### F10 (IMPORTANT) — adopter-audit deferral's re-trigger fired with no carrier

Scope event 2 deferred auditing the adopter repos (openbrain, resume,
homelab, dolt-server) for a committed `.pi/settings.json` "until at
least one shipper-side item closes"; the shipper-side items closed, the
completeness review explicitly recorded "the adopter-audit deferral's
re-trigger has fired with no carrier item", and none was ever filed.
This plan is where the carrier lands. Carrier: audit the four adopters
for pi consumption readiness; file per-adopter items in their own
tenants per the cross-tenant conventions (never admit in another repo's
queue).

### F11 (DEFERRAL, reconsiderable) — prompt-template layer

Scope event 1 deferred "/livespec-<op> bare commands: purely additive
ergonomics over the skills; reconsider after the live end-to-end
exercise as a work-item on repo livespec-driver-pi". The live e2e
exercise happened (`livespec-ewqnqm` closed on real structured JSON
from `pi -p "/skill:livespec-next"`). The reconsider condition is met;
this plan should reach an explicit adopt-or-re-defer decision.

### F12 (TRACKING) — open transferred items, not children here

- `livespec-driver-pi-1zt` (blocked, this repo's tenant): the Fabro
  sandbox `gh` wrapper hard-calls
  `.claude-plugin/scripts/bin/mint_app_token.py`, which target repos do
  not vendor; fallback token lacks PR-creation permission; wrapper is
  baked into a container image whose source is not on this host.
  Fleet-wide; unblocking is upstream of any future factory dispatch
  from this repo. Not re-filed — tracked here for visibility.
- `overseer-4od1` (backlog, livespec-overseer tenant): pre-existing
  tmux test defect surfaced by the pi work. Owned there; noted only.

## Findings — upstream prevention (templates / checklists / tooling)

### F13 (IMPORTANT) — the driver-plugin templatization trigger has fired

`TEMPLATE_BORN_CLASSES = frozenset({"impl-plugin"})`
(`livespec-dev-tooling/livespec_dev_tooling/fleet/_contract_classes.py:53`)
deliberately excludes driver-plugins; the recorded revisit condition —
"if a third runtime driver is created — three hand-built drivers is the
templatization trigger" — is now satisfied by this repo. The only
end-to-end driver-plugin obligation inventory in existence is ARCHIVED
plan research
(`livespec/plan/archive/bootstrap-pi-driver/research/initial-research.md`),
which is exactly how a hand-bootstrap misses pieces: the donor (codex)
lacked `.ai/`, so pi lacked `.ai/`. Two candidate levers, to be decided
in this plan and routed as a livespec-core spec proposal +
dev-tooling work:

- Small lever: promote the archived inventory into a MAINTAINED
  per-class obligation list under livespec core
  `SPECIFICATION/non-functional-requirements.md` §"Fleet membership
  contract" (where the three obligation types already live), covering
  at minimum: `.ai/` seed topic + AGENTS.md convention block, both
  CLAUDE.md symlinks, `.claude/settings.json` (+hooks decision),
  `plan/` store note, `tests/heading-coverage.json`,
  `.livespec.jsonc` `external_references` + `cross_repo_targets`,
  the full workflow set, check-target swaps per class,
  `CI_RUNNER_LABELS` + the AGENTS.md CI-runner-routing section,
  shell-quality positive control, extension/hook quality gating
  (typecheck + behavioral tests), branch protection + secrets + App
  grant + topic, beads tenant provisioning, register-LAST ordering.
- Large lever: extend `TEMPLATE_BORN_CLASSES` (and the copier template)
  to `driver-plugin` — a contract change per the recorded rationale.

The small lever is cheap and durable; the large one is only worth it if
a fourth driver is plausible. Default recommendation: small lever now,
record the large one as an explicit deferral with the fourth-driver
trigger.

### F14 (IMPORTANT) — `external_references` has zero tooling/template coverage

The key is mandated by livespec core `SPECIFICATION/constraints.md`
(~l.282-298) and enforced only as a livespec-core-private doctor
invariant; NO `livespec_dev_tooling` module references it and the
copier template's `.livespec.jsonc.jinja` does not mention it. A new
repo learns it only by reading constraints.md or copying a sibling (pi
got it right by luck of the seed pass). Carrier: add the key (with a
TODO placeholder) to the template jinja, and mention it in the
per-class obligation list of F13.

### F15 (NICE-TO-HAVE) — `check-agents-ai-references-resolve` cannot detect absence

Fleet-wide: a repo with zero `.ai/` files passes by construction
(dangling-reference check only). Options: a per-class minimum-guidance
obligation (fits F13's list), or a seed-topic requirement asserted by
the fleet `agent-instruction-surface` row. Also noted in passing: the
`.ai/` files in livespec-overseer and livespec-orchestrator-beads-fabro
are unreferenced from their AGENTS.md (orphaned from the
progressive-disclosure path) — upstream hygiene, file where owned.

## Proposed requirement carriers (for the scope event)

1. Extension quality gate: node pin + tsconfig + typecheck gate +
   behavioral unit suite for `livespec-footgun-guard.ts` (F1).
2. `.ai/` tree seed: `beads-tenant.md` + AGENTS.md references; decide
   the pi-gotchas topic file (F2).
3. Repo CI config: runner scale set + `CI_RUNNER_LABELS` +
   AGENTS.md CI-runner-routing section (F3, F4).
4. Shell-quality positive-control test ported from codex (F5).
5. Doc-rot pass: AGENTS.md bootstrap-status rewrite + sanctioned-seam
   release-please.yml comment fix (F6).
6. Root CLAUDE.md symlink; `file_lloc_hard_gate` decision;
   `.claude/settings.json` hooks decision (F7, F8, F9).
7. Adopter `.pi/settings.json` audit — the fired re-trigger's carrier;
   per-adopter filing in owning tenants (F10).
8. Prompt-template-layer decision: adopt or re-defer with a new
   trigger (F11).
9. Upstream: per-class obligation list proposal into livespec core NFR
   §"Fleet membership contract" + `external_references` template
   coverage + `.ai/`-absence gate decision — routed as
   `propose-change` in livespec core and work in livespec-dev-tooling
   (F13, F14, F15).

## Explicit deferral candidates

- Copier-template extension to driver-plugin class (large lever of
  F13): defer with trigger "a fourth runtime driver is planned";
  the maintained obligation list is the compensating control.
- Live pi-CLI e2e harness: remains out per the standing AGENTS.md
  rationale (live-credential dependency; a mock verifies only the
  mock); unchanged by this plan.
- `livespec-driver-pi-1zt` (sandbox gh wrapper) and `overseer-4od1`:
  already tracked in their owning tenants; not children of this plan.
