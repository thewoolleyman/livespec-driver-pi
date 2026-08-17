---
name: livespec-prune-history
description: Destructively prune old vNNN/ snapshots from <spec-root>/history/ to bound history size. Requires explicit user invocation because model-driven invocation is disabled, and a generic mention of history NEVER activates it. Invoked only via /skill:livespec-prune-history or an explicit user request to prune the livespec history.
allowed-tools: bash read write edit
disable-model-invocation: true
---

# livespec-prune-history — pi Driver binding

This file is the thin pi binding for the `prune-history` operation, shipped by the
**livespec-driver-pi** Driver package. It carries pi-runtime mechanics ONLY.
The complete harness-neutral driving prose is livespec CORE's artifact at
`<core-root>/prose/prune-history.md`.

Order of work, every time:

1. Resolve `<core-root>` (next section).
2. Read `<core-root>/prose/prune-history.md` **completely** with the `read` tool.
3. Execute that prose end-to-end, binding its harness-neutral vocabulary to
   this runtime via the Runtime bindings section below.

Never paraphrase, summarize, or act on a partial read of the prose, and never
restate its steps here — core owns the behavior, this file owns the wiring.

## Resolving livespec core (`<core-root>`)

This Driver package ships the eight bindings, the resolver named below, and one
sanctioned extension. It carries **no** `prose/` and **no** `scripts/`. The
harness-neutral prose and the reference spec-side CLIs ship with **livespec
core** (`thewoolleyman/livespec`), installed alongside this Driver as a
resource-less pi git package.

The ordered algorithm is realized ONCE, by this package's
`lib/resolve-core-root.sh`. Do NOT restate it inline. Eight inline copies of a
resolution rule are kept in agreement only by copying, and that is exactly how
one defect came to live in all eight of a sibling Driver's bindings at once.

`<skill-dir>` below is the directory holding THIS `SKILL.md` — you read this
file from disk, so you know its absolute path; the resolver sits two levels up
at the package root.

```bash
LIVESPEC_CORE_ROOT="$(bash "<skill-dir>/../../lib/resolve-core-root.sh" .)" || exit 1
echo "$LIVESPEC_CORE_ROOT"
```

The resolver searches, in order: the `LIVESPEC_CORE_PLUGIN_ROOT` override; the
governed project's own `.claude-plugin/` when it carries `prose/` (the project
IS livespec core — dogfooding); the project-scope pi package clone under
`.pi/git/github.com/thewoolleyman/livespec/`; and the user-scope clone under
`~/.pi/agent/git/github.com/thewoolleyman/livespec/`.

On failure the resolver writes its own diagnostic to stderr and exits 1. STOP
and surface that diagnostic verbatim. Do not improvise a path, and do not run
an install command the diagnostic did not ask for — in particular, a failure
under a non-interactive `pi -p` run is frequently pi's project-trust gate
silently ignoring project packages rather than a missing install.

## Config-named CLI dispatch

Per livespec core's contract (its `contracts.md`), every spec-side operation is
named in the **governed project's** `.livespec.jsonc` under
`spec_clis.prune_history` as an argv-form array, pre-populated with core's reference
default and individually overridable. To "run the prune-history CLI named in config":

1. Read `<project-root>/.livespec.jsonc` (JSONC — tolerate `//` comments). If
   the file, the `spec_clis` section, or the `spec_clis.prune_history` key is
   absent, use core's reference default argv:
   `python3 <core-root>/scripts/bin/prune_history.py`.
2. If the configured argv contains the literal plugin-root substitution token
   (the `CLAUDE_PLUGIN_ROOT` placeholder, written as a `$`-brace expansion in
   config), expand it to `<core-root>`. Core's schema defines that token as
   "the installed livespec plugin root", which is CORE's root — never this
   Driver's, which carries no `scripts/` at all.
3. Append the operation's flags and invoke with the `bash` tool.

With the default config this collapses to:

```bash
python3 "$LIVESPEC_CORE_ROOT/scripts/bin/prune_history.py" [--project-root <path>]
```

The prose's requirement that "every Driver MUST configure its runtime so
model-driven self-invocation is disabled" is realized in this binding by the
`disable-model-invocation: true` frontmatter above: pi hides this skill from
the system prompt entirely, so the model cannot reach for it on its own
initiative — only an explicit `/skill:livespec-prune-history` invocation, or an
explicit user request to prune the history, triggers it. Never infer it from a
generic mention of history, and never auto-activate it as a follow-up to
another operation.

## Mutating-operation precondition

`prune-history` MUTATES the specification tree. Per the Driver-shipped-hooks
contract in livespec `SPECIFICATION/contracts.md`, a mutating pi operation
MUST NOT be exercised unless this Driver's `tool_call` footgun-guard extension
(`extensions/livespec-footgun-guard.ts`) is loaded. If pi reports that the
package's extensions are not loaded — most often the project-trust gate under a
non-interactive run — STOP and say so rather than proceeding unguarded.

## Runtime bindings

- **"run the prune-history CLI named in config" / "invoke the prune-history CLI"** —
  dispatch per the Config-named CLI dispatch section above; with the
  default config:

  ```bash
  python3 "$LIVESPEC_CORE_ROOT/scripts/bin/prune_history.py" [--project-root <path>]
  ```
- **"ask the user" / "confirm with the user" / "surface" / "narrate"** —
  conversational turns in this pi session. pi has no structured-picker tool, so
  ask in plain prose, present the options explicitly, and wait for the user's
  reply before proceeding.
- **"read `<file>`"** — the `read` tool. **"write `<file>`"** — the `write`
  tool. **"edit `<file>`"** — the `edit` tool. **"list `<dir>`" / shell work** —
  the `bash` tool.
- **"the doctor prose (`prose/doctor.md`)"** — read
  `$LIVESPEC_CORE_ROOT/prose/doctor.md` with the `read` tool and follow it; the
  LLM-driven post-step phase runs under this Driver's `livespec-doctor` skill.
