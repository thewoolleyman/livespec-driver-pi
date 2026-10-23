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
