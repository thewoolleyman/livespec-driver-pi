"""Tests for `dev-tooling/check-pre-push.sh`, the delegated pre-push gate wiring.

The script is driven for real under `bash`; only its two collaborators, `uv` and
`just`, are replaced by recording stubs placed first on `PATH`, because the real
ones would need a cluster (`uv run ... gate_remote_delegate run`) or the full
aggregate (`just check`). Each stub appends its argv to a log, so the tests
assert which path the script took rather than what it printed.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from livespec_dev_tooling.gate_remote_delegate import delegated_gate_enabled

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "dev-tooling" / "check-pre-push.sh"

_UV_STUB = """#!/usr/bin/env bash
echo "uv $*" >> "$STUB_LOG"
case "$*" in
  *green_token*) exit "${STUB_GREEN_TOKEN_EXIT:-1}" ;;
  *"gate_remote_delegate enabled"*) exit "${STUB_ENABLED_EXIT:-1}" ;;
  *"gate_remote_delegate run"*) exit "${STUB_RUN_EXIT:-0}" ;;
esac
exit 99
"""
_JUST_STUB = """#!/usr/bin/env bash
echo "just $*" >> "$STUB_LOG"
exit "${STUB_JUST_EXIT:-0}"
"""


def _drive(*, tmp_path: Path, **stub_exits: int) -> tuple[int, list[str]]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, body in (("uv", _UV_STUB), ("just", _JUST_STUB)):
        stub = bin_dir / name
        stub.write_text(body)
        stub.chmod(0o755)
    log = tmp_path / "calls.log"
    log.touch()
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "STUB_LOG": str(log),
        **{key: str(value) for key, value in stub_exits.items()},
    }
    completed = subprocess.run(
        ["bash", str(SCRIPT)], env=env, capture_output=True, text=True, check=False
    )
    return completed.returncode, log.read_text().splitlines()


def test_repository_opts_in_to_the_delegated_gate() -> None:
    assert delegated_gate_enabled(repo_root=REPO_ROOT) is True


def test_delegating_host_runs_the_client_in_place_of_just_check(tmp_path: Path) -> None:
    code, calls = _drive(tmp_path=tmp_path, STUB_ENABLED_EXIT=0, STUB_RUN_EXIT=0)
    assert code == 0
    assert any("gate_remote_delegate run" in call for call in calls)
    assert not any(call.startswith("just ") for call in calls)


@pytest.mark.parametrize("client_exit", [1, 2, 99])
def test_delegated_run_without_a_pass_refuses_and_never_runs_the_local_gate(
    tmp_path: Path, client_exit: int
) -> None:
    code, calls = _drive(tmp_path=tmp_path, STUB_ENABLED_EXIT=0, STUB_RUN_EXIT=client_exit)
    assert code == client_exit
    assert not any(call.startswith("just ") for call in calls)


def test_non_delegating_host_gates_locally_with_just_check(tmp_path: Path) -> None:
    code, calls = _drive(tmp_path=tmp_path, STUB_ENABLED_EXIT=1)
    assert code == 0
    assert "just check" in calls
    assert not any("gate_remote_delegate run" in call for call in calls)


def test_green_token_match_skips_both_the_client_and_the_local_gate(tmp_path: Path) -> None:
    code, calls = _drive(tmp_path=tmp_path, STUB_GREEN_TOKEN_EXIT=0, STUB_ENABLED_EXIT=0)
    assert code == 0
    assert not any("gate_remote_delegate" in call for call in calls)
    assert not any(call.startswith("just ") for call in calls)
