# livespec-driver-pi

pi Driver plugin for [livespec](https://github.com/thewoolleyman/livespec) —
thin SKILL.md bindings over livespec core's harness-neutral operation prose
and spec-side CLIs, for the pi coding agent runtime. The analogue of
[livespec-driver-claude](https://github.com/thewoolleyman/livespec-driver-claude)
and [livespec-driver-codex](https://github.com/thewoolleyman/livespec-driver-codex).

Bootstrap in progress (plan `bootstrap-pi-driver`, epic `livespec-g5h5ff` in
the livespec core ledger). Per livespec core's ratified v208 contracts
(`SPECIFICATION/contracts.md` §"Plugin distribution", §"Driver-shipped hooks";
`non-functional-requirements.md` §"pi dogfooding compatibility/contracts/constraints"),
this repo will ship:

- eight thin pi skills — `livespec-seed`, `livespec-propose-change`,
  `livespec-critique`, `livespec-revise`, `livespec-doctor`,
  `livespec-prune-history`, `livespec-next`, `livespec-help` — invoked as
  `/skill:livespec-<operation>`;
- the pi footgun guard (`tool_call`-blocking pi extension), required before
  any mutating operation is claimed;
- full driver-plugin fleet membership (own SPECIFICATION/, beads tenant,
  shim workflows, release automation).

Fleet-manifest registration deliberately happens LAST, once this repo is
fully done.
