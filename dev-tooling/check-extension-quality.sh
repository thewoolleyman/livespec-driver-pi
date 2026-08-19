#!/usr/bin/env bash
#
# check-extension-quality.sh — the quality gate over this repo's FIRST-PARTY
# TypeScript: `extensions/livespec-footgun-guard.ts`, the ONE sanctioned pi
# extension livespec `SPECIFICATION/contracts.md` §"Driver-shipped hooks"
# requires this Driver to ship.
#
# WHY A SECOND GATE OVER A FILE THAT ALREADY HAS ONE. The guard's existing
# gate — `extension_violations()` in `check-pi-package-structure` — asserts
# over the file's TEXT: exactly one `pi.on("tool_call")` registration, the four
# predicate tokens, an internal `catch`. Those assertions are the right ones for
# a structural check and they cannot, even in principle, notice that the file no
# longer compiles or that a predicate returns the opposite of what it did
# yesterday: the tokens are all still in the file. Both mutations were confirmed
# to survive it and to be killed by the suite this gate runs.
#
# The sibling Drivers get this for free — their guards are Python, so they ride
# `check-lint` / `check-format` / `check-types` / `check-coverage` and carry
# behavioral suites under `check-hooks`. A TypeScript guard rides none of the
# Python gates, so the equivalent coverage is wired here explicitly.
#
# TWO LEGS, both of which need NO live model and NO credentials — which is what
# distinguishes this from the CLI-end-to-end harness this repo deliberately does
# not ship (AGENTS.md: a mocked pi CLI would verify only the mock):
#
#   1. `tsc --noEmit` over the extension AND its suite. `tsconfig.json` sets
#      `erasableSyntaxOnly`, so this also proves the guard stays loadable under
#      Node's type stripping — a non-erasable construct fails here instead of at
#      runtime in a live pi session.
#   2. `node --test` over `tests/extensions/`, driving the guard's exported
#      `decide()` directly. No pi event bus, nothing mocked.
#
# Dependencies come from `package-lock.json` via `npm ci` — the npm analogue of
# `uv sync` against the pinned `pyproject.toml`. The install is skipped when the
# materialized tree is already newer than the lockfile, so the common local
# `just check` run pays only the two legs.
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

if [ ! -f package-lock.json ]; then
    echo "check-extension-quality: package-lock.json is missing — run 'npm install' and commit it." >&2
    exit 1
fi

# `node_modules/.package-lock.json` is npm's own record of what it materialized;
# comparing against it (rather than the directory mtime, which any tool can
# touch) is what makes the skip trustworthy.
if [ ! -f node_modules/.package-lock.json ] || [ package-lock.json -nt node_modules/.package-lock.json ]; then
    echo "=== npm ci (node_modules is absent or older than the lockfile) ==="
    npm ci --no-audit --no-fund
fi

echo "=== tsc --noEmit (extension + suite) ==="
npx --no-install tsc --noEmit

echo "=== node --test tests/extensions ==="
# The glob is QUOTED so node's own test-runner glob expands it. An unquoted
# shell glob would hand node a bare directory, which it rejects as a module
# path — a failure mode that looks like a broken suite rather than a broken
# invocation.
node --test "tests/extensions/*.test.ts"
