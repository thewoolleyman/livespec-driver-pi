#!/usr/bin/env bash
set -uo pipefail

# Ratified shell-quality deviation: this pre-push gate intentionally does not
# use errexit because a green-token miss should fall through to the full check.
if uv run python -m livespec_dev_tooling.green_token check 2>&1; then
    echo ":: pre-push: green token matched; skipping full aggregate"
    exit 0
fi

# Delegated pre-push gate (SPECIFICATION/non-functional-requirements.md
# §"Spec"). `exec` is load-bearing: once delegation is selected, the client's
# exit status IS the push verdict, and there must be no branch from a
# no-verdict result to the local aggregate below. A host that cannot read the
# gates kubeconfig (a Fabro sandbox) or the gate pod itself makes `enabled`
# exit non-zero, and falls through to the local `just check`.
if uv run python -m livespec_dev_tooling.gate_remote_delegate enabled; then
    echo ":: pre-push: delegating the gate to the remote executor"
    exec uv run python -m livespec_dev_tooling.gate_remote_delegate run
fi

just check
