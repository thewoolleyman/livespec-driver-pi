# Foreman Actuator Mechanics

Read this before driving the foreman actuator (`foreman-act`) against this
repo. Resuming the foreman seat on 2026-08-21 (epic
`livespec-driver-pi-ob4`) cost FIVE consecutive `foreman-act` refusals
before the first accepted mutation. Every one of them was a MECHANICS
gap, not a policy refusal: the actuator was working exactly as designed
and the caller did not know its shape.

**Scope fence.** The foreman OPERATOR CONTRACT is plugin-owned prose at
the livespec-overseer cache root and is deliberately NOT restated here —
this repo's one design rule is that a binding never copies operation
prose, and that rule holds for guidance too. What follows is only what is
true of THIS repo's invocation environment: the argument shape, the
envelope, the credential wrapper, the race, and the journal.

## `--proposal` takes a file path, not inline JSON

Write the envelope to a file and pass the PATH:

```bash
foreman-act --proposal /tmp/proposal.json
```

Passing the JSON itself is the first refusal, and its diagnostic does not
say so. The argument is opened through `pathlib`, so inline JSON raises a
**`FileNotFoundError`** whose text is the JSON document — it reads as a
missing file rather than as a wrong argument shape, and the natural next
move (checking whether some file is missing) leads away from the actual
defect.

## The envelope's required fields

The envelope is validated field-by-field, so a caller who does not know
the whole required set pays one refusal per missing field. All of these
are REQUIRED:

```jsonc
{
  "schema_version": 1,
  "action_id": "<unique id for this action>",
  "repo": "livespec-driver-pi",
  "topic": "<plan topic>",
  "session_name": "<the seat's session name>",
  "snapshot": {
    "tick_generation": "<from a fresh gather>",
    "daemon_instance_id": "<from a fresh gather>",
    "session_identity": "<from a fresh gather>"
  }
}
```

All THREE snapshot fields are revalidated against a FRESH gather
document — see the next section for why that is a race and not merely a
copy.

**`session_identity` belongs INSIDE `snapshot`.** A `session_identity`
placed at the TOP LEVEL of the envelope is silently **ignored**: the
actuator finds no identity in the snapshot it validates and refuses with
`session_identity_changed`. That diagnostic reads as a STALE value, so
the obvious response is to re-gather and retry — which cannot work,
because nothing about the value was wrong. The key was in the wrong
place.

The ACTION PAYLOAD then sits under a key named for the action itself,
beside the fields above:

- `work_item_comment: {work_item_id, text}`
- `work_item_file: {filing: {target_repo, title, description, type,
  depends_on, checklist{the six gates}, …}}`

## gather, compose and act run in ONE credential-wrapper invocation

Two facts that only make sense together.

**The wrapper is not optional, and it scrubs `PATH`.** The ledger
subprocess shells a bare `bd` with `cwd=<repo>`, so the tenant
credentials have to be present — see `.ai/beads-tenant.md` for that
tenant's own hazards. But `with-livespec-env.sh` **scrubs `PATH`**, and
the scrubbed `PATH` loses `uv`, which the plugin bin shebangs need. The
working form re-exports the caller's `PATH` across the wrapper:

```bash
/usr/local/bin/with-livespec-env.sh -- env PATH="$PATH" <command>
```

**And the three stages must share that one invocation.** The daemon's
snapshot generation advances every few seconds, while the wrapper's
credstore hop is slow enough to lose that race. So gather, compose and
act run inside one credential-wrapper invocation — one wrapper call, all
three stages inside it:

```bash
/usr/local/bin/with-livespec-env.sh -- env PATH="$PATH" sh -c '
  <gather command> > /tmp/gather.json          # 1. gather
  <compose the envelope from /tmp/gather.json> # 2. compose
  foreman-act --proposal /tmp/proposal.json    # 3. act
'
```

The gather and compose steps are deliberately left as PLACEHOLDERS: the
gather command and the envelope composition are plugin-owned surface
whose spelling this file does not pin (see the scope fence above), and a
command name invented here is exactly the kind of wrong fact that costs
the next session a cycle. What is measured, and what this section
commits to, is the SHAPE: one wrapper call, with all three stages inside
it.

Split them across separate wrapper invocations and the snapshot composed
from the first gather is already stale by the time `act` validates it:
the actuator refuses with **`tick_generation_changed`**. That refusal is
not about a wrong value — re-gathering and retrying by hand loses the
same race again, which is how it consumes several attempts before the
shape becomes visible.

## The journal is the audit trail

Every actuator attempt — refused or acted, without exception — is
journaled to `tmp/fabro-dispatch-journal.jsonl` under
`"stage": "foreman-act"`. That file, not the ledger and not a terminal
scrollback, is the **audit trail** of what the seat actually tried, and
reading its tail is the fastest way to see what a prior session did
before guessing:

```bash
grep '"stage": "foreman-act"' tmp/fabro-dispatch-journal.jsonl | tail
```

A refusal that left no mark on the ledger still left one here, which is
why this is the first place to look when the ledger and the seat's own
account of a tick disagree.
