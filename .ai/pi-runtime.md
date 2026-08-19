# pi Runtime Gotchas

Read this before authoring a `skills/livespec-<operation>/SKILL.md`
binding or writing anything that drives the `pi` CLI unattended. Both
hazards below were found the expensive way during this repo's bootstrap,
and both are SILENT: the failure mode is a green-looking run, not an
error.

## Frontmatter: an unquoted `: ` in a value is fatal

pi's skill loader refuses a SKILL.md whose frontmatter carries a
value-internal unquoted `: `. Five of this repo's eight bindings were
invisible to pi for exactly this reason (work-item
`livespec-driver-pi-7vxsaq`) — the skills simply did not appear, with no
diagnostic pointing at the frontmatter.

Quote any value containing a colon-space:

```yaml
description: "Invoke as: /skill:livespec-next"
```

`check-pi-package-structure` now rejects the unquoted shape locally, so a
conforming gate means the skills can actually load. Do not weaken that
assertion to accommodate a value — quote the value.

## `pi -p` exits 0 even when the model call itself failed

A `pi -p … "/skill:…"` whose model call fails with a 400 prints the error
text and still exits **0** (verified live, 2026-08-17; work-item
`livespec-driver-pi-pmqpzu`). Any unattended drive that branches on exit
status alone reads a dead drive as green.

Classify from OUTPUT SHAPE, never from the raw status. This repo ships
the classifier:

```bash
dev-tooling/check-pi-drive-output --pi-exit-code <raw> --stdout <file> --stderr <file>
```

It exits 0 only when the raw status was 0 AND no fatal model-call output
was recognized, so it — not `pi` — is the signal to trust. Its regression
suite is the `check-pi-drive-output` gate.

## What is deliberately NOT covered here

There is no live pi-CLI end-to-end harness in this repo, and adding a
mocked one is not the fix: a fake pi CLI verifies only the fake. The
acceptance path for pi-runtime behavior is a live interactive session on
a host that actually has `pi` installed (the Fabro sandbox does not), on
a scoped tmux socket rather than the default one. The extension's own
decision logic, by contrast, needs no runtime at all — it is unit-tested
under `check-extension-quality`.
