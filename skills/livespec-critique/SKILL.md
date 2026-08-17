---
name: livespec-critique
description: Critique an existing livespec specification or a pending proposed change, surfacing ambiguities, contradictions, and missing rules as findings the user can act on. Use when the user asks to critique the spec or find issues in it. This mutating operation can land its findings as a proposed change.
allowed-tools: bash read write edit
---

# livespec-critique — pi Driver binding

This file is the thin pi binding for the `critique` operation, shipped by the
**livespec-driver-pi** Driver package. It carries pi-runtime mechanics ONLY.
The complete harness-neutral driving prose is livespec CORE's artifact at
`<core-root>/prose/critique.md`.

Order of work, every time:

1. Resolve `<core-root>` (next section).
2. Read `<core-root>/prose/critique.md` **completely** with the `read` tool.
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
`spec_clis.critique` as an argv-form array, pre-populated with core's reference
default and individually overridable. To "run the critique CLI named in config":

1. Read `<project-root>/.livespec.jsonc` (JSONC — tolerate `//` comments). If
   the file, the `spec_clis` section, or the `spec_clis.critique` key is
   absent, use core's reference default argv:
   `python3 <core-root>/scripts/bin/critique.py`.
2. If the configured argv contains the literal plugin-root substitution token
   (the `CLAUDE_PLUGIN_ROOT` placeholder, written as a `$`-brace expansion in
   config), expand it to `<core-root>`. Core's schema defines that token as
   "the installed livespec plugin root", which is CORE's root — never this
   Driver's, which carries no `scripts/` at all.
3. Append the operation's flags and invoke with the `bash` tool.

With the default config this collapses to:

```bash
python3 "$LIVESPEC_CORE_ROOT/scripts/bin/critique.py" --findings-json <path> [--author <id>] [--spec-target <path>] [--project-root <path>]
```

## Mutating-operation precondition

`critique` MUTATES the specification tree. Per the Driver-shipped-hooks
contract in livespec `SPECIFICATION/contracts.md`, a mutating pi operation
MUST NOT be exercised unless this Driver's `tool_call` footgun-guard extension
(`extensions/livespec-footgun-guard.ts`) is loaded. If pi reports that the
package's extensions are not loaded — most often the project-trust gate under a
non-interactive run — STOP and say so rather than proceeding unguarded.

## Runtime bindings

- **"run the critique CLI named in config" / "invoke the critique CLI"** —
  dispatch per the Config-named CLI dispatch section above; with the
  default config:

  ```bash
  python3 "$LIVESPEC_CORE_ROOT/scripts/bin/critique.py" --findings-json <path> [--author <id>] [--spec-target <path>] [--project-root <path>]
  ```
- **"run the template-resolution CLI"** — via the `bash` tool:

  ```bash
  python3 "$LIVESPEC_CORE_ROOT/scripts/bin/resolve_template.py"
  ```
- **"ask the user" / "confirm with the user" / "surface" / "narrate"** —
  conversational turns in this pi session. pi has no structured-picker tool, so
  ask in plain prose, present the options explicitly, and wait for the user's
  reply before proceeding.
- **"read `<file>`"** — the `read` tool. **"write `<file>`"** — the `write`
  tool. **"edit `<file>`"** — the `edit` tool. **"list `<dir>`" / shell work** —
  the `bash` tool.
- **"the revise / propose-change operation"** — the
  `/skill:livespec-revise`, `/skill:livespec-propose-change` skills in this
  Driver package.
- **"the doctor prose (`prose/doctor.md`)"** — read
  `$LIVESPEC_CORE_ROOT/prose/doctor.md` with the `read` tool and follow it; the
  LLM-driven post-step phase runs under this Driver's `livespec-doctor` skill.
- **"core's `livespec/schemas/` package"** — resolves at runtime to
  `$LIVESPEC_CORE_ROOT/scripts/livespec/schemas/`.
