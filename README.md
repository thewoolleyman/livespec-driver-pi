# livespec-driver-pi

pi Driver package for [livespec](https://github.com/thewoolleyman/livespec) —
thin SKILL.md bindings over livespec core's harness-neutral operation prose
and spec-side CLIs, for the pi coding agent runtime. The analogue of
[livespec-driver-claude](https://github.com/thewoolleyman/livespec-driver-claude)
and [livespec-driver-codex](https://github.com/thewoolleyman/livespec-driver-codex).

Everything substantive — the driving prose, the reference spec-side CLIs, the
JSON schemas, the built-in templates — ships with livespec core. This package
only binds that material to the pi runtime, per core's ratified v208 contracts
(`SPECIFICATION/contracts.md` §"Plugin distribution", §"Driver-shipped hooks";
`non-functional-requirements.md` §"pi dogfooding compatibility", §"pi
dogfooding contracts", §"pi dogfooding constraints").

## What ships today

| Path | What it is |
|---|---|
| `skills/livespec-<operation>/SKILL.md` | The eight thin operation bindings: `seed`, `propose-change`, `critique`, `revise`, `doctor`, `prune-history`, `next`, `help`. Invoked as `/skill:livespec-<operation>`. |
| `lib/resolve-core-root.sh` | The single realization of livespec-CORE-root resolution. All eight bindings call it; none restates the algorithm. |
| `extensions/livespec-footgun-guard.ts` | The ONE sanctioned first-party pi extension: the `tool_call`-blocking footgun guard, required before any mutating operation is exercised. |
| `package.json` | The pi package manifest (`pi.skills`, `pi.extensions`, the `pi-package` keyword). |
| `dev-tooling/`, `justfile`, `check-targets.txt`, `.github/` | The family-standard enforcement suite, per-target matrix CI, and the fleet shim / release-automation workflows. |

## Install

Both core and this Driver install as pi git packages, at PROJECT scope (`-l`),
from the governed project's root:

```bash
pi install git:github.com/thewoolleyman/livespec@release -l
pi install git:github.com/thewoolleyman/livespec-driver-pi@release -l
```

Core is a resource-less carrier: it declares no `pi` manifest and ships no pi
resource directories, so pi loads zero resources from it. This Driver resolves
core's `prose/` and `scripts/` under `.claude-plugin/` inside that clone.

Two things to know before driving anything unattended:

- **pi's project-trust gate.** A non-interactive invocation (`-p`, `--mode
  json`, `--mode rpc`) silently ignores project-local settings and packages
  until a trust decision exists (`~/.pi/agent/trust.json`, a global
  `defaultProjectTrust: always`, or a per-run `--approve`). Untrusted means the
  operation resolves nothing — with no error to say so.
- **Currency.** `pi update --extensions` moves a branch-ref clone to the
  fetched branch tip, which is how the `release` channel stays current.

## How a binding works

Each SKILL.md carries pi-runtime mechanics only:

1. Resolve `<core-root>` via `lib/resolve-core-root.sh` — the
   `LIVESPEC_CORE_PLUGIN_ROOT` override, else the governed project's own
   `.claude-plugin/` when it carries `prose/` (the project IS core), else the
   project-scope pi clone, else the user-scope pi clone.
2. Read `<core-root>/prose/<operation>.md` completely and follow it.
3. Dispatch the CLI named in the governed project's `.livespec.jsonc`
   `spec_clis.<key>`, defaulting to `<core-root>/scripts/bin/<name>.py`.

A binding never copies operation prose, wrapper files, or templates, and never
points at `.claude-plugin/skills/*` — core ships no such tree. Edit core's
`prose/<name>.md` for BEHAVIOR; edit a binding here only for pi mechanics.
`check-pi-package-structure` is the mechanical guard over all of that.

## Still pending

Own `SPECIFICATION/` tree, the beads tenant, the three repo secrets, branch
protection, and fleet-manifest registration. See `AGENTS.md` §"Bootstrap
status" for the current state and the exact remaining steps.
