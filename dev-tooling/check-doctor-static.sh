#!/usr/bin/env bash
#
# check-doctor-static.sh — run livespec CORE's static doctor phase against this
# repo's own SPECIFICATION/ tree.
#
# The checker (`doctor_static.py`) ships with CORE, not with this Driver. This
# Driver's package root deliberately carries no `scripts/` at all, so the gate
# has to find a core payload somewhere on the host. Three sources, in order:
#
#   1. $LIVESPEC_CORE_PLUGIN_ROOT — the explicit override, and the AUTHORITATIVE
#      one. CI sets it to the core checkout it makes at the release tag this repo
#      pins, so CI checks the spec against the contract version the Driver
#      actually claims compatibility with.
#   2. The pi package clones this Driver resolves core from at runtime — the
#      project-scope clone first, then the user-scope one. Sharing the runtime
#      resolver's own locations keeps the gate honest: it checks the same core
#      payload a real pi session would bind.
#   3. A sibling core clone beside this repo's PRIMARY checkout. This is the
#      maintainer-host fallback, and it is why `just check` and the pre-push
#      gate work on a dev box with no pi install. It is derived rather than
#      hardcoded: `--git-common-dir` resolves to the primary checkout's `.git`
#      even when this runs from a secondary worktree, whose own parent
#      directory holds no sibling clones at all.
#
# Sources 2 and 3 are whatever those clones happen to be checked out at, which
# need not be the pinned release. That is acceptable for a local pre-push
# signal; CI is the authoritative run, and it always takes source 1.
#
# A candidate counts only when it actually carries `scripts/bin/doctor_static.py`.
# Resolving to a path whose checker is absent would fail later and more
# confusingly than failing here with an install instruction.
set -euo pipefail

core_clone_suffix="git/github.com/thewoolleyman/livespec/.claude-plugin"

candidates=()
if [ -n "${LIVESPEC_CORE_PLUGIN_ROOT:-}" ]; then
    candidates+=("$LIVESPEC_CORE_PLUGIN_ROOT")
fi
candidates+=(".pi/$core_clone_suffix")
candidates+=("${HOME:-}/.pi/agent/$core_clone_suffix")

if common_dir="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"; then
    candidates+=("$(dirname "$(dirname "$common_dir")")/livespec/.claude-plugin")
fi

core_root=""
for candidate in "${candidates[@]}"; do
    if [ -f "$candidate/scripts/bin/doctor_static.py" ]; then
        core_root="$candidate"
        break
    fi
done

if [ -z "$core_root" ]; then
    {
        printf 'livespec core not found: no candidate carries scripts/bin/doctor_static.py.\n'
        printf 'Searched, in order:\n'
        for candidate in "${candidates[@]}"; do
            printf '    %s\n' "$candidate"
        done
        printf '\n'
        printf 'Set LIVESPEC_CORE_PLUGIN_ROOT to a livespec checkout'"'"'s .claude-plugin, or\n'
        printf 'install core as a project-scope pi package from the repo root:\n'
        printf '    pi install git:github.com/thewoolleyman/livespec@release -l\n'
    } >&2
    exit 1
fi

python3 "$core_root/scripts/bin/doctor_static.py" --project-root .
