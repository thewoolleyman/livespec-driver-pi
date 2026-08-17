# justfile — livespec-driver-pi task runner.
#
# Family conventions, scaled to this repo's content. At the current
# bootstrap stage that content is the toolchain, the enforcement wiring,
# the fleet shim workflows, and the repo-local structural check; the
# eight thin pi SKILL.md bindings, the sanctioned TypeScript
# footgun-guard pi extension, and the dogfooded SPECIFICATION/ tree land
# in later passes (see AGENTS.md §"Bootstrap status"). Each of those
# passes brings its OWN gate with it — the gates guarding a subject are
# wired in the same change that creates the subject, never before.
#
# Authority: livespec/SPECIFICATION/non-functional-requirements.md
#   §"Enforcement-suite invocation" — `just` is the canonical entry
#   point for every dev-tooling invocation. Lefthook and CI MUST
#   delegate to `just <target>`; direct tool invocations in hook/CI
#   configs are banned.
#
# Authority: livespec/SPECIFICATION/contracts.md
#   §"Pre-commit step ordering" — the gates wired here mirror the
#   spec-required ordering: 00-lint-autofix-staged, 01-commit-pairs-
#   source-and-test, 02-check-pre-commit at pre-commit;
#   no-commit-on-master + red-green-replay at commit-msg.
#
# The Red→Green→Replay ritual IS enforced here (epic livespec-gcp2:
# red-green-replay is enforced fleet+adopter-wide, regardless of any
# repo's product-Python footprint). The gate only fires on a
# `feat:`/`fix:` commit that stages a `.py` file, so it simply does not
# fire while this repo carries no product Python — the wiring is armed
# either way.

# Default to listing targets when no recipe is invoked.
default:
    @just --list

# ---------------------------------------------------------------
# First-time setup.
# ---------------------------------------------------------------

# Worktree-discipline pack recipe fragments — OPTIONAL imports (`import?`, NOT
# plain `import`): the fragments are gitignored-and-installed by
# `just install-worktree-pack` (run from the `worktree-pack` LOCAL obligation
# row that `bootstrap` walks), so they are ABSENT in a fresh clone until then. A
# plain `import` of a missing file makes `just` fail to parse the ENTIRE
# justfile, which would brick `just bootstrap` on a fresh clone; the optional
# `import?` silently no-ops while the file is absent — the `worktree-*` and
# `branch-protection-*` recipes simply are not available until the fragments are
# materialized — and resolves once installed.
import? 'dev-tooling/worktree.just'
import? 'dev-tooling/branch-protection.just'

# First-touch setup — a THIN delegator to the shipped LOCAL first-touch
# reconcile verb (`livespec_dev_tooling.fleet.local_reconcile`). Reuse-first:
# NO copied logic — the verb walks the LOCAL obligation partition
# (`contract.LOCAL_OBLIGATION_ROWS`): mise trust/install, uv sync, the
# canonical worktree-discipline pack, the structural commit-refuse hooks
# (subsuming `lefthook install` — the canonical hook overwrites the lefthook
# stubs and delegates to `lefthook run`), the advisory `refs/notes/*` refspec,
# the worktree-root mise-trust entry, the beads tenant-dir hardening, the
# beads-runtime detect-and-guide probes, and project-scoped plugin
# registration. The plugin rows delegate back to THIS repo's own
# `ensure-plugins` recipe below. The verb resolves shared-state rows
# worktree-safely via `git rev-parse --git-common-dir`, so invoking from a
# linked worktree still provisions the primary checkout's shared state. The
# `worktree-pack` row is the ONE exception: the pack lives in each checkout's
# own `dev-tooling/` and the `import?` lines above resolve relative to the
# worktree you stand in, so that row targets the INVOKED worktree.
bootstrap:
    uv run python -m livespec_dev_tooling.fleet.local_reconcile

# Install the canonical livespec commit-refuse hook by REUSING the shared
# livespec-dev-tooling installer module (the SINGLE source of the structural
# hook body; pinned in pyproject.toml). NOT re-implemented in this Driver repo.
# Idempotent; worktree-safe (resolves the primary's shared .git/hooks).
install-commit-refuse-hooks:
    uv run python -m livespec_dev_tooling.install_commit_refuse_hooks

# Install (or idempotently re-install) the canonical worktree-discipline pack —
# FOUR files: `worktree-lib.sh` + `branch-protection.sh` (executable) and
# `worktree.just` + `branch-protection.just` (imported above, not executable) —
# into the current checkout's `dev-tooling/` directory. The livespec-dev-tooling
# installer module is the single canonical-body carrier. The pack files are
# GITIGNORED-AND-MATERIALIZED, never tracked. `bootstrap` covers this
# automatically via the `worktree-pack` LOCAL obligation row, so this recipe is
# the standalone repair path.
install-worktree-pack:
    uv run python -m livespec_dev_tooling.install_worktree_pack

# The standard shared derive-from-settings wrapper: reads the committed
# `.claude/settings.json` (`extraKnownMarketplaces` incl. ref, `enabledPlugins`)
# at runtime and issues the marketplace add / install / update commands for
# exactly what it finds — one source of truth, recipe-content drift structurally
# impossible. Registers this repo's full project-scope Claude plugin set; the
# SessionStart hook in `.claude/settings.json` runs this recipe so each new
# session's project-scope plugins are current. Core + the Claude Driver MUST be
# present for agents doing Claude-side work in this repo, even though this
# repo's own published surface is the pi Driver.
ensure-plugins:
    mise exec -- uv run --no-sync python -m livespec_dev_tooling.fleet.ensure_plugins

# ---------------------------------------------------------------
# Enforcement aggregate.
# ---------------------------------------------------------------

check:
    bash dev-tooling/check-aggregate.sh

# Factory-branch guard: implementation branches must not carry workflow edits.
# Maintainer-side workflow diffs are reported out-of-band instead of landing
# from Fabro slices.
check-no-workflow-edits:
    bash dev-tooling/check-no-workflow-edits.sh

# Conformance-Pattern baseline Verifier (shipped by livespec-dev-tooling):
# the cross-harness plugin-resolution concern (concern #2). It reads the
# `harnesses` declaration in `.livespec.jsonc` and, in mock mode, asserts
# declaration integrity (every declared harness has a valid status; an
# exempt harness carries a reason). This repo declares its own `pi`
# harness SUPPORTED (the shared Verifier's known-harness set includes it
# as of livespec-dev-tooling v1.28.x) and declares claude and codex
# EXEMPT — each of those surfaces ships from its own Driver repo.
# Authority: livespec/SPECIFICATION/
# non-functional-requirements.md §"Conformance Pattern".
check-plugin-resolution:
    uv run python -m livespec_dev_tooling.checks.plugin_resolution

check-lint:
    uv run ruff check .

check-format:
    uv run ruff format --check .

# `check-types` — the pyright tool-backed gate (fixed fleet policy: every
# consumer wires check-lint / check-format / check-types / check-coverage,
# enforced by check-tool-backed-check-completeness). Scoped via
# [tool.pyright] in pyproject.toml to `dev-tooling/`, this repo's only
# first-party Python surface at the current bootstrap stage.
check-types:
    uv run pyright

# `check-coverage` — the aggregate `fail_under = 100` coverage gate (the
# fourth tool-backed check). Measures the covered source the SAME clean way a
# standalone CI job would: COVERAGE_FILE UNSET (`env -u`) so no exported
# per-target namespace can leniently green-light self-referential lines.
check-coverage:
    env -u COVERAGE_FILE uv run pytest tests/ --cov --cov-branch --cov-config=pyproject.toml --cov-report=term-missing

# Spec heading-coverage gate (shipped by livespec-dev-tooling): every
# `## ` H2 in each SPECIFICATION/ NLSpec file MUST have an entry in
# tests/heading-coverage.json. This keeps the coverage map in lockstep
# with the spec — adding or renaming a spec H2 without updating the
# registry fails the check. TODO entries (no per-heading test yet) warn
# locally and fail only when LIVESPEC_FAIL_IF_HEADING_COVERAGE_TODOS_EXIST
# is set; this binding repo leaves it UNSET.
check-heading-coverage:
    uv run python -m livespec_dev_tooling.checks.heading_coverage

# ---------------------------------------------------------------
# Applies-to-all structural coverage checks (fleet-check-coverage,
# livespec epic livespec-i5ebqd). Each derives its file universe from
# the SAME root-anchored git index (`resolve_check_universe`).
# ---------------------------------------------------------------

check-all-declared:
    uv run python -m livespec_dev_tooling.checks.all_declared

check-assert-never-exhaustiveness:
    uv run python -m livespec_dev_tooling.checks.assert_never_exhaustiveness

check-comment-line-anchors:
    uv run python -m livespec_dev_tooling.checks.comment_line_anchors

check-file-lloc:
    uv run python -m livespec_dev_tooling.checks.file_lloc

check-global-writes:
    uv run python -m livespec_dev_tooling.checks.global_writes

check-keyword-only-args:
    uv run python -m livespec_dev_tooling.checks.keyword_only_args

check-main-guard:
    uv run python -m livespec_dev_tooling.checks.main_guard

check-match-keyword-only:
    uv run python -m livespec_dev_tooling.checks.match_keyword_only

check-no-inheritance:
    uv run python -m livespec_dev_tooling.checks.no_inheritance

check-no-lloc-soft-warnings:
    uv run python -m livespec_dev_tooling.checks.no_lloc_soft_warnings

check-no-write-direct:
    uv run python -m livespec_dev_tooling.checks.no_write_direct

check-partition-completeness:
    uv run python -m livespec_dev_tooling.checks.partition_completeness

check-private-calls:
    uv run python -m livespec_dev_tooling.checks.private_calls

check-rop-pipeline-shape:
    uv run python -m livespec_dev_tooling.checks.rop_pipeline_shape

# ---------------------------------------------------------------
# Red→Green→Replay ritual gates (epic livespec-gcp2). Shared from
# livespec-dev-tooling. The gate only fires on a `feat:`/`fix:` commit
# that stages a `.py` file — a `ci:` / `docs:` / `chore:` changeset
# rides through untouched.
# ---------------------------------------------------------------

# Trailer-based Red→Green replay verification (hard gate). Invoked by
# the lefthook commit-msg stage with the commit-message file path as
# argv[1] (the load-bearing per-commit verifier). The no-arg variant
# (e.g. from `just check`) DERIVES the message from `git log -1
# --format=%B` (HEAD) and validates it.
[positional-arguments]
check-red-green-replay *args:
    uv run python -m livespec_dev_tooling.checks.red_green_replay "$@"

# Commit-pair gate: every commit touching source files also touches
# tests. Lefthook pre-commit is the load-bearing per-commit invocation.
# The source-tree role keys come from this repo's `[tool.livespec_dev_
# tooling]` block in pyproject.toml.
check-commit-pairs-source-and-test:
    uv run python -m livespec_dev_tooling.checks.commit_pairs_source_and_test

# ---------------------------------------------------------------
# Pre-commit auxiliary gates.
# ---------------------------------------------------------------

# Ruff fix + format on staged .py files BEFORE the rest of the
# pre-commit gate runs. Non-blocking — unfixable issues fall through
# to check-lint / check-format inside `just check` later. Re-stages
# post-autofix bytes. `--force-exclude` on BOTH ruff invocations so the
# explicit-path runs honor pyproject's `extend-exclude` (ruff otherwise
# honors it only for directory-walked paths).
lint-autofix-staged:
    bash dev-tooling/lint-autofix-staged.sh

# Fast pre-commit subset (no test run; pre-push runs the full
# aggregate).
check-pre-commit: check-lint check-format

check-pre-push:
    bash dev-tooling/check-pre-push.sh

check-agents-ai-references-resolve:
    uv run python -m livespec_dev_tooling.checks.agents_ai_references_resolve

check-aggregate-completeness:
    uv run python -m livespec_dev_tooling.checks.aggregate_completeness

check-branch-protection-alignment:
    uv run python -m livespec_dev_tooling.checks.branch_protection_alignment

check-canonical-recipe-fidelity:
    uv run python -m livespec_dev_tooling.checks.canonical_recipe_fidelity

check-check-coverage-incremental:
    uv run python -m livespec_dev_tooling.checks.check_coverage_incremental

check-check-mutation:
    uv run python -m livespec_dev_tooling.checks.check_mutation

check-check-tools:
    uv run python -m livespec_dev_tooling.checks.check_tools

check-ci-matrix-completeness:
    uv run python -m livespec_dev_tooling.checks.ci_matrix_completeness

check-claude-md-coverage:
    uv run python -m livespec_dev_tooling.checks.claude_md_coverage

check-fleet-marketplace-relative-sources:
    uv run python -m livespec_dev_tooling.checks.fleet_marketplace_relative_sources

check-master-ci-green:
    uv run python -m livespec_dev_tooling.checks.master_ci_green

check-newtype-domain-primitives:
    uv run python -m livespec_dev_tooling.checks.newtype_domain_primitives

check-no-direct-destructive-cli:
    uv run python -m livespec_dev_tooling.checks.no_direct_destructive_cli

check-no-direct-tool-invocation:
    uv run python -m livespec_dev_tooling.checks.no_direct_tool_invocation

check-no-except-outside-io:
    uv run python -m livespec_dev_tooling.checks.no_except_outside_io

check-no-fmt-directives:
    uv run python -m livespec_dev_tooling.checks.no_fmt_directives

check-no-raise-outside-io:
    uv run python -m livespec_dev_tooling.checks.no_raise_outside_io

check-no-todo-registry:
    uv run python -m livespec_dev_tooling.checks.no_todo_registry

check-pbt-coverage-pure-modules:
    uv run python -m livespec_dev_tooling.checks.pbt_coverage_pure_modules

# Coverage CONSUMER (livespec-dev-tooling-yilyxr.8, dev-tooling PR #1462
# design). The former `check-coverage` dependency re-ran the whole suite
# in this target's own just invocation (a separate process from the
# aggregate's earlier check-coverage run, so no dedup applied): the
# aggregate paid the suite twice. check-coverage (which the serial
# aggregate runs first) is the clean-env producer; this target reads
# its repo-root `.coverage` once and DELETES it (consume-once — a later
# standalone run can never report from stale data); absent the file
# (standalone/CI) it runs the clean suite itself first.
# No-errexit deviation: explicit exit handling preserves the consume-once
# cleanup on failure (errexit would skip the rm and strand stale data).
check-per-file-coverage:
    #!/usr/bin/env bash
    set -uo pipefail
    if [[ ! -f .coverage ]]; then
        echo ":: check-per-file-coverage: no .coverage present (standalone run); running the clean suite"
        env -u COVERAGE_FILE uv run pytest tests/ --cov --cov-branch --cov-config=pyproject.toml --cov-report=term-missing || exit $?
    else
        echo ":: check-per-file-coverage: reading .coverage from check-coverage's clean run (no duplicate suite run)"
    fi
    env -u COVERAGE_FILE uv run python -m livespec_dev_tooling.checks.per_file_coverage || { rm -f .coverage; exit 2; }
    rm -f .coverage

check-primary-checkout-commit-refuse-hook-installed:
    uv run python -m livespec_dev_tooling.checks.primary_checkout_commit_refuse_hook_installed

check-public-api-result-typed:
    uv run python -m livespec_dev_tooling.checks.public_api_result_typed

check-skill-invocation-paths:
    uv run python -m livespec_dev_tooling.checks.skill_invocation_paths

check-supervisor-discipline:
    uv run python -m livespec_dev_tooling.checks.supervisor_discipline

check-tests-mirror-pairing:
    uv run python -m livespec_dev_tooling.checks.tests_mirror_pairing

check-tests-no-subprocess-spawn:
    uv run python -m livespec_dev_tooling.checks.tests_no_subprocess_spawn

check-tool-backed-check-completeness:
    uv run python -m livespec_dev_tooling.checks.tool_backed_check_completeness

check-vendor-manifest:
    uv run python -m livespec_dev_tooling.checks.vendor_manifest

check-wrapper-shape:
    uv run python -m livespec_dev_tooling.checks.wrapper_shape

check-no-shadow-ledger-body-identical:
    uv run python -m livespec_dev_tooling.checks.no_shadow_ledger_body_identical

install-no-shadow-ledger:
    uv run python -m livespec_dev_tooling.install_no_shadow_ledger

check-local-memory-drift-audit:
    uv run python -m livespec_dev_tooling.checks.local_memory_drift_audit

check-handoff-dispatch-routing:
    uv run python -m livespec_dev_tooling.checks.handoff_dispatch_routing

check-self-hosted-routing:
    uv run python -m livespec_dev_tooling.checks.self_hosted_routing

check-shell-quality:
    uv run python -m livespec_dev_tooling.checks.shell_quality

check-source-trees-scoped-to-consumer:
    uv run python -m livespec_dev_tooling.checks.source_trees_scoped_to_consumer

check-spec-governance-default-block:
    uv run python dev-tooling/check-spec-governance-default-block

# Structural gate over the shipped pi package: all eight `livespec-<operation>`
# SKILL.md bindings present with conforming frontmatter, no binding pointing at
# `.claude-plugin/skills/*`, canonical `$LIVESPEC_CORE_ROOT` wrapper
# invocations, prune-history still explicit-user-invocation only, a well-formed
# `pi` manifest, and the sanctioned footgun-guard extension carrying its four
# block predicates plus its own catch. This is the pi analogue of the shared
# `check-skill-invocation-paths` Verifier, which is scoped to
# `.claude-plugin/skills/` and therefore VACUOUSLY SKIPS in a pi package.
check-pi-package-structure:
    uv run python dev-tooling/check-pi-package-structure

# Regression gate for pi's unreliable raw exit status: unattended drives must
# classify captured stdout/stderr and trust this tool's exit code instead of
# `pi -p`'s own status when a model-call failure is printed.
check-pi-drive-output:
    uv run pytest tests/dev-tooling/test_check_pi_drive_output.py

# livespec core's STATIC doctor phase over this repo's own SPECIFICATION/ tree.
# Its own dedicated CI job rather than a matrix leg, because it is the one
# target needing a SECOND checkout — livespec core, at the release tag
# .livespec.jsonc pins — so the spec is checked against the contract version
# this Driver claims compatibility with.
check-doctor-static:
    bash dev-tooling/check-doctor-static.sh

# Retired: plan anchors are now ledger-held (plan_slug metadata), not git
# anchor files. Kept as a no-op passthrough for canonical-slug completeness;
# the surviving invariant lives in check-plan-epic-parity.
check-plan-anchor-declared:
    uv run python -m livespec_dev_tooling.checks.plan_anchor_declared

check-plan-epic-parity:
    uv run python -m livespec_dev_tooling.checks.plan_epic_parity

# Plan-lifecycle tombstone ban: a topic must not exist at BOTH
# plan/<topic>/ and plan/archive/<topic>/. Fail-closed with no opt-in
# lever and no credential requirement.
check-plan-no-tombstone:
    uv run python -m livespec_dev_tooling.checks.plan_no_tombstone

check-no-shadow-ledger-body-typechecks:
    uv run python -m livespec_dev_tooling.checks.no_shadow_ledger_body_typechecks

check-required-role-keys-declared:
    uv run python -m livespec_dev_tooling.checks.required_role_keys_declared

check-hook-trees-not-io-exempt:
    uv run python -m livespec_dev_tooling.checks.hook_trees_not_io_exempt
