# Commissioning the plan archive completeness reviewer

Read this before commissioning the independent completeness reviewer that
satisfies Gate 2 of the livespec plan archive (independent
completeness-review evidence) from a Claude Code session.

## Spawn the reviewer without a `name`

Spawn the reviewer subagent WITHOUT the Agent tool's `name` parameter, for
example `Agent(subagent_type: "general-purpose", model: "opus", prompt:
<adversarial brief>)`.

Passing `name` routes the spawn onto the teammate path. A named agent reports
through `SendMessage`, signals an idle notification, and waits to be
addressed; its final message is not returned to the caller. An unnamed spawn
runs as a background subagent whose final message IS the return value and
arrives as a completion notification, which is what the evidence record needs.

## Do not synthesize a missing verdict

The archive validator requires `attests-complete-requirement-coverage: true`
from a reviewer identity other than the archive actor. A verdict the archiving
session writes itself is exactly the self-review the gate forbids, so if no
reviewer verdict arrives, the archive waits.

## Brief the reviewer so it cannot go quiet

- Tell the reviewer explicitly that its final message is the return value.
- Give it a tool-call budget.
- Instruct it to emit a PARTIAL report rather than stop without one.

## Provenance

Recorded 2026-10-18 from a session note. The named-spawn failure burned two
full attempts across two sessions on epic `livespec-driver-pi-jvvhxi`
(2026-08-20 and 2026-08-21); both sessions correctly refused to fabricate the
missing verdict.
