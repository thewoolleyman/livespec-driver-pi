# Beads Tenant Operations

Read this before running live `bd` or livespec-orchestrator-beads-fabro
commands against the `livespec-driver-pi` beads tenant.

## The two things that go wrong

**Writing to the WRONG repo's ledger.** Every livespec repo has its own
per-repo Dolt tenant, and `bd` selects one from the `.beads/config.yaml`
of the directory it resolves. Pass `-C <repo-path>` as a literal command
argument so the connection block that gets used is this repo's:

```bash
/usr/local/bin/with-livespec-env.sh -- bd -C /data/projects/livespec-driver-pi list --status all
```

A `bd` run from a *sibling* clone with no `-C`, or with the wrong one,
writes into that sibling's tenant. Nothing errors: the write succeeds
against the tenant you did not mean. The damage surfaces later, as a
work-item that is missing from the repo that owns it and present in one
that does not.

**Leaking the tenant password.** `BEADS_DOLT_PASSWORD` is supplied at
call time by the credential wrapper and is NEVER committed —
`.beads/config.yaml` is tracked precisely because it carries no password
and no per-machine `project_id`. Never echo, log, or print the variable.
If credential presence must be diagnosed, use a probe that cannot reveal
it, such as a byte count:

```bash
/usr/local/bin/with-livespec-env.sh -- sh -c 'printf %s "${BEADS_DOLT_PASSWORD:-}" | wc -c'
```

## The wrapper is not optional

The tenant is server-mode over TCP (`127.0.0.1:3307`, database and user
both `livespec-driver-pi`; see `.beads/config.yaml`). Outside the
credential wrapper the required secret env is simply absent, and the
orchestrator wrappers say so rather than failing obscurely:

```
livespec: required credential env absent; re-invoking under credential_wrapper
```

If the re-invocation itself then fails — typically in a sandbox that
blocks sudo or sets `no_new_privs`, so the wrapper cannot reach the
root-only systemd-creds credstore — run the command with
`/usr/local/bin/with-livespec-env.sh -- …` from an environment that can.
That message is a resolvable environment fact, not a broken tenant.

## Ledger-vs-file authority

Plan handoffs, scope events, and work-item status are LEDGER-held; only
research notes are filesystem-held. When a `plan/<topic>/research/` note
and live tenant state disagree, the tenant is authoritative and the note
is historical record.
