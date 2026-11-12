#!/usr/bin/env bash
set -uo pipefail

# Ratified shell-quality deviation: this aggregate intentionally does not use
# errexit because it must run every target and report the complete failure set.
# check-targets.txt keeps the canonical block visible to the shared aggregate
# verifier while this runner stays ShellCheck-governed.
# Arguments name targets to skip. The `check` recipe passes the fleet's
# SKIP_TARGETS list here; a run that skipped anything writes no green token.
skip_targets=("$@")

targets=()
while IFS= read -r line; do
    target="${line%%#*}"
    target="${target#"${target%%[![:space:]]*}"}"
    target="${target%"${target##*[![:space:]]}"}"
    if [[ -n "$target" ]]; then
        targets+=("$target")
    fi
done < check-targets.txt

# The green token is keyed only by the committed tree, so it may memoize a
# member only when that member declares whether it reads outside that tree.
# Refuse before dispatch: a late finding would waste a full aggregate run and
# a token from it would imply a verdict the aggregate refuses to report.
if ! undeclared_members=$(uv run python -m livespec_dev_tooling.green_token undeclared "${targets[@]}"); then
    printf 'ERROR: these check aggregate members carry no purity declaration: %s\n' \
        "${undeclared_members//$'\n'/ }" >&2
    exit 1
fi

failed=()
coverage_ran=0
for target in "${targets[@]}"; do
    skip_this=0
    for skipped in "${skip_targets[@]}"; do
        if [[ "$target" = "$skipped" ]]; then
            skip_this=1
        fi
    done
    if [[ "$skip_this" -eq 1 ]]; then
        echo "::: just ${target} (skipped)"
        continue
    fi
    if [[ "$target" = "check-coverage" && "$coverage_ran" -eq 1 ]]; then
        continue
    fi
    echo "=== just ${target} ==="
    if ! just "${target}"; then
        failed+=("${target}")
    fi
    if [ "$target" = "check-per-file-coverage" ]; then
        coverage_ran=1
    fi
done

if [ "${#failed[@]}" -gt 0 ]; then
    echo "FAILED targets: ${failed[*]}" >&2
    exit 1
fi

if [ "${#skip_targets[@]}" -gt 0 ]; then
    echo ":: skipped ${skip_targets[*]}: no green token written"
    exit 0
fi

if ! uv run python -m livespec_dev_tooling.green_token write; then
    :
fi
