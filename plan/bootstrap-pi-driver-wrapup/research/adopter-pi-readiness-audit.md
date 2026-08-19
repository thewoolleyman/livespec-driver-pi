# Adopter pi-readiness audit (F10)

Date: 2026-08-19. Carrier for the re-trigger the archived
`bootstrap-pi-driver` plan's scope event 2 left obligation-free: auditing
the adopter repos for a committed `.pi/settings.json`, deferred "until at
least one shipper-side item closes". Those items closed, the g5h5ff
completeness review recorded that the re-trigger had fired with no carrier,
and `livespec-driver-pi-no6in2` is where it landed.

## Method

Inspected the four named adopters — `openbrain`, `resume`, `homelab`,
`dolt-server` — at their `/data/projects/` clones for: a tracked `.pi/`
tree, the `harnesses` block in `.livespec.jsonc`, and ANY textual mention
of the pi Driver (`driver-pi`, `.pi/settings`) across markdown, JSON/JSONC,
and workflow files.

## Result

**No adopter consumes the pi Driver, and none is configured to.**

| Repo | `.pi/settings.json` | `harnesses` block | Mentions the pi Driver |
|---|---|---|---|
| `openbrain` | absent | none declared | none |
| `resume` | absent | none declared | none |
| `homelab` | absent | none declared | none |
| `dolt-server` | absent | `claude` + `codex`, both `exempt` | none |

All four track `.claude/settings.json` and `.livespec.jsonc`;
`dolt-server` additionally records `codex_host_registrations` for the Codex
Driver. Zero files across the four repos mention `livespec-driver-pi`.

## Reading

The absence is CORRECT STATE, not drift. A `.pi/settings.json` in a repo
that has not opted into pi would declare packages nobody in that repo
loads. There is no per-adopter defect to file, and filing one in each
adopter's tenant would push an adoption decision those repos never made —
which is the opposite of the cross-tenant convention that motivated the
"file in the owning tenant" rule in the first place.

What HAS changed since the deferral was written is that pi adoption is now
POSSIBLE, which is exactly what the deferral was waiting on:

- the `@release` install channel exists (the `release` branch is live and
  v0.3.0–v0.5.0 are cut, each stamping `package.json` `$.version` through
  the release-please `extra-files` updater);
- this repo's own `.pi/settings.json` demonstrates the consumer shape —
  `git:github.com/thewoolleyman/livespec@release`,
  `…/livespec-driver-pi@release`,
  `…/livespec-orchestrator-beads-fabro@release`;
- the pi harness is declared `supported` in `.livespec.jsonc` and is
  exercised rather than failing closed, since `_KNOWN_HARNESSES` gained
  `pi` in livespec-dev-tooling v1.28.x.

## Disposition

The deferral is DISCHARGED: the audit ran, and its answer is "nothing to
remediate". Rolling pi out to any adopter is a fresh per-repo decision for
that repo's maintainer, not a defect this plan should force. If such a
decision is taken, the work-item belongs in that adopter's own tenant and
the shape to copy is this repo's `.pi/settings.json` plus a `pi` entry in
its `harnesses` block.
