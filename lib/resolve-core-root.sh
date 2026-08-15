#!/usr/bin/env bash
#
# resolve-core-root.sh — the single realization of the pi Driver's
# livespec-CORE-root resolution.
#
# Every one of the eight `livespec-<operation>` bindings calls this script
# instead of restating the ordered algorithm inline. The Claude Driver learned
# this the expensive way: eight independently-maintained inline copies are kept
# in agreement only by copying, and that is exactly how one positional defect
# came to live in all eight bindings at once and hard-stopped every spec-side
# operation from an affected project.
#
# This Driver's OWN package root carries no `prose/` and no `scripts/` — it
# ships bindings, this resolver, and one sanctioned extension. The prose and the
# reference spec-side CLIs ship with livespec CORE (`thewoolleyman/livespec`),
# installed alongside as a resource-less pi git package per livespec
# SPECIFICATION/contracts.md §"Plugin distribution".
#
# Ordered algorithm — first hit wins:
#
#   1. $LIVESPEC_CORE_PLUGIN_ROOT when set and non-empty. The explicit operator
#      override; covers nonstandard dev setups such as driving a sibling
#      checkout's core.
#   2. <project-root>/.claude-plugin when it carries prose/ — the governed
#      project IS the livespec core repo itself (dogfooding).
#   3. <project-root>/.pi/git/github.com/thewoolleyman/livespec/.claude-plugin —
#      the PROJECT-scope pi package clone (`pi install ... -l`).
#   4. ~/.pi/agent/git/github.com/thewoolleyman/livespec/.claude-plugin — the
#      USER-scope pi package clone.
#
# Steps 3 and 4 are pi's own documented git-package clone locations. A candidate
# counts as resolved ONLY when it carries a `prose/` directory: a clone that
# exists but is empty or half-fetched must fail loudly rather than resolve to a
# path whose prose reads would each fail separately and confusingly.
#
# On success: writes the resolved absolute path to stdout, exits 0.
# On failure: writes an install diagnostic to stderr, exits 1. The caller MUST
# surface that diagnostic verbatim and stop — never improvise a path, and never
# run an install command the diagnostic did not ask for.
#
# Usage: resolve-core-root.sh [<project-root>]   (default: the current directory)

set -euo pipefail

project_root="${1:-.}"

if ! project_root="$(cd "$project_root" 2>/dev/null && pwd)"; then
    printf 'livespec core resolution failed: project root %s does not exist\n' \
        "${1:-.}" >&2
    exit 1
fi

core_clone_suffix="git/github.com/thewoolleyman/livespec/.claude-plugin"

candidates=()
if [ -n "${LIVESPEC_CORE_PLUGIN_ROOT:-}" ]; then
    candidates+=("$LIVESPEC_CORE_PLUGIN_ROOT")
fi
candidates+=("$project_root/.claude-plugin")
candidates+=("$project_root/.pi/$core_clone_suffix")
candidates+=("${HOME:-}/.pi/agent/$core_clone_suffix")

for candidate in "${candidates[@]}"; do
    if [ -d "$candidate/prose" ]; then
        printf '%s\n' "$candidate"
        exit 0
    fi
done

{
    printf 'livespec core could not be resolved: no candidate carries a prose/ directory.\n'
    printf 'Searched, in order:\n'
    for candidate in "${candidates[@]}"; do
        printf '    %s\n' "$candidate"
    done
    printf '\n'
    if [ -n "${LIVESPEC_CORE_PLUGIN_ROOT:-}" ]; then
        printf 'LIVESPEC_CORE_PLUGIN_ROOT is set to %s but carries no prose/.\n' \
            "$LIVESPEC_CORE_PLUGIN_ROOT"
        printf 'An override that does not resolve is a configuration error, not a\n'
        printf 'missing install — fix or unset it before installing anything.\n\n'
    fi
    printf 'Install livespec core as a project-scope pi package from the repo root:\n'
    printf '    pi install git:github.com/thewoolleyman/livespec@release -l\n\n'
    printf 'pi resolves project packages only after the project is TRUSTED, so a\n'
    printf 'non-interactive run (-p, --mode json, --mode rpc) in an untrusted project\n'
    printf 'silently loads nothing. Establish trust before driving unattended.\n'
} >&2
exit 1
