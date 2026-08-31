# Full Pi plugin-skill support across the livespec fleet

## Origin
Split out from livespec-overseer plan `foreman-codex-pi-runtime-support`
(epic `overseer-nbzgrk`) on 2026-08-30, after that plan's Codex/Pi foreman
support was shown NOT to work in a real Pi session. Root cause was NOT the
identity gate (sound, proven) but Pi plugin DELIVERY: no Pi session on the
fleet can load the livespec-overseer skills. This is a fleet-wide Pi
concern, out of scope for that narrow foreman-identity plan. This plan is a
DEPENDENCY of `overseer-nbzgrk`; that plan closes only after this one
finishes and its foreman-in-Pi proof is re-verified.

## Confirmed scope: Pi only. Codex already works.
Verified 2026-08-30: `codex plugin list` shows every fleet plugin
installed+enabled; Codex skills are model-invoked (natural language) and the
foreman skill runs end-to-end that way. No Codex delivery work is required.

## THE ESTABLISHED PI CONVENTION (do not reinvent it)
Established by the archived `bootstrap-pi-driver` (livespec core) and
`bootstrap-pi-driver-wrapup` (this repo) plans, and recorded in this repo's
`plan/archive/bootstrap-pi-driver-wrapup/research/adopter-pi-readiness-audit.md`:

- A repo opts into Pi by committing a tracked `.pi/settings.json` declaring
  the packages a Pi session in THAT repo loads, using the `@release` channel:
  `git:github.com/thewoolleyman/<repo>@release`. This is PROJECT-LOCAL — it
  applies only when Pi runs inside that repo.
- The repo also declares `pi` in its `.livespec.jsonc` `harnesses` block.
- Pi adoption is a per-repo decision; the audit deliberately declined to force
  it on adopters (openbrain/resume/homelab/dolt-server) that never opted in.

Consequence: a USER-GLOBAL `pi install` (as was done ad-hoc on the diagnosis
host on 2026-08-30 for livespec-overseer) is the WRONG shape. It must be
reverted so it does not mask the per-repo gap during verification; the durable
fix is per-repo `.pi/settings.json`.

## The real gap map (measured 2026-08-30)
Repos that RUN Pi seats vs. repos that DECLARE Pi packages:

| Repo | runs a Pi seat? | `.pi/settings.json` | declares livespec-overseer? |
|---|---|---|---|
| livespec-dev-tooling | YES (tmux `rop-railway-enforcement`) | NONE | no |
| livespec-overseer | (foreman seats) | NONE | no |
| livespec | – | yes: livespec, driver-pi, orchestrator-beads-fabro | **NO** |
| livespec-driver-pi | – | yes: livespec, driver-pi, orchestrator-beads-fabro | **NO** |
| livespec-orchestrator-beads-fabro | – | NONE | no |
| livespec-console-beads-fabro, homelab | – | NONE | no |

Two distinct defects:
1. Repos that run Pi seats (livespec-dev-tooling, livespec-overseer, …) have NO
   `.pi/settings.json` at all, so a Pi session there loads no livespec skills.
2. Even the two repos that DO declare packages omit
   `git:github.com/thewoolleyman/livespec-overseer@release`, so the overseer's
   five Pi skills (foreman, supervise-plan, grooming, overseer,
   caam-anthropic-loop) are unavailable in Pi EVERYWHERE.

Pi-publishing repos (enumerate from `.claude-plugin/.pi-plugin/skills/*`, do not
hardcode): livespec-overseer (5 skills), livespec-orchestrator-beads-fabro
(12), plus livespec and livespec-driver-pi surfaces.

## Evidence the mechanism works
Installing `git:github.com/thewoolleyman/livespec-overseer@release` made a
normal Pi session list and invoke `/livespec-overseer-foreman`, which ran a
full foreman tick end-to-end (entry gate admitted the seat, tick advanced,
correct no-action decision). The `@release` channel and the package shape are
proven; they were simply never declared for these repos.

## Work to do (ALL Pi skills, ALL repos that run Pi seats)
1. For every repo that runs (or will run) Pi seats, add/extend a committed
   `.pi/settings.json` declaring ALL the Pi packages that repo's seats need —
   crucially including `livespec-overseer@release` — plus the `pi` harnesses
   entry. Start with livespec-overseer and livespec-dev-tooling (the live Pi
   seat repo); extend livespec and livespec-driver-pi to add livespec-overseer.
2. Revert the ad-hoc user-global `pi install` on the diagnosis host (wrong
   shape) BEFORE verifying, so per-repo declarations are proven on their own.
3. Correct misleading invocation docs (plugin.json/descriptions say
   `/livespec-overseer:foreman`, which is Claude-only; Pi uses
   `/<plugin>-<skill>` once declared).
4. Resolve the Pi recurring-loop question: Pi has no CronCreate, so the
   foreman's (and any looping skill's) recurrence-arming in Pi is UNVERIFIED.
   Determine Pi's real recurrence mechanism and prove the loop recurs, or
   record the supported alternative.
5. Add a fleet-conformance check asserting each Pi-seat repo declares its
   Pi packages and each Pi-publishing repo's skills are invocable in a real Pi
   session (close the acceptance-theater gap mechanically). Respect the
   per-repo-opt-in rule from the adopter audit.

## Overlap with `bootstrap-pi-driver-wrapup` (archived; deliberately NOT rolled in)
That plan is driver-pi REPO PLUMBING — TS extension gating (F1), `.ai/` tree
(F2), CI runner labels (F3/F4), shell-quality test (F5), doc rot (F6), symlink
(F7), LLOC gate (F8) — none of which is skill delivery. Its skill-adjacent
output is the CONVENTION above (adopter audit F10), which this plan builds on
rather than repeats. Its two still-open children: `livespec-driver-pi-ulvjs2`
(foreman actuator mechanics into `.ai/` — foreman-in-Pi operability, candidate
to fold in) and `livespec-driver-pi-1zt` (Fabro sandbox gh wrapper — unrelated,
leave it).

## Verification criteria (SAME standard as overseer-nbzgrk; non-negotiable)
A Pi skill is accepted ONLY when the real skill is invoked, by its real
user-facing invocation, in a real Pi session that loaded it from the repo's
committed `.pi/settings.json` (no user-global install, no `--skill`/`-e`
force-load, no fakes), and observed to run to a real outcome. Per repo and per
skill verify: (a) the package is declared and actually loaded (`pi list -l`),
(b) the documented invocation works, (c) `$PLUGIN_ROOT` resolves to the
intended version, (d) the loop/recurrence mechanism the skill needs exists.

## Dogfooding / live proof target
A live Pi session runs in tmux `rop-railway-enforcement` (pid 3375447, cwd
/data/projects/livespec-dev-tooling) — a repo that currently has NO
`.pi/settings.json`, so it is the ideal proof surface: add the declaration
there and show the skills appear and run. opus-4-8 in Pi is blocked by
Anthropic's third-party extra-usage wall (Pi ignores --api-key); use Pi's
working provider unless the maintainer enables extra usage.

## Blocking relationship
This plan blocks livespec-overseer `overseer-nbzgrk`. When done and verified,
re-run the foreman-in-Pi end-to-end proof from a Pi seat that loaded the
overseer package via a committed `.pi/settings.json`, record it on
overseer-nbzgrk (criterion A1), then that plan may archive.
