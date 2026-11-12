"""Regression checks for the repository check-aggregate runner."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from livespec_dev_tooling.check_purity import audit_check_purity
from returns.unsafe import unsafe_perform_io

__all__: list[str] = []

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CHECK_AGGREGATE = _REPO_ROOT / "dev-tooling" / "check-aggregate.sh"

_UV_STUB = """#!/usr/bin/env bash
printf 'uv %s\\n' "$*" >> "$STUB_LOG"
case "$*" in
    *"green_token undeclared"*)
        printf '%s\\n' "${UNDECLARED_MEMBER:-}"
        test -z "${UNDECLARED_MEMBER:-}" && exit 0
        exit 1
        ;;
esac
exit 0
"""

_JUST_STUB = """#!/usr/bin/env bash
printf 'just %s\\n' "$*" >> "$STUB_LOG"
exit 0
"""


def test_every_aggregate_member_declares_its_purity() -> None:
    """A token memoizes only members whose declaration makes that sound."""
    targets = tuple(
        line.split("#", maxsplit=1)[0].strip()
        for line in (_REPO_ROOT / "check-targets.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )

    audit = unsafe_perform_io(audit_check_purity(targets=targets, repo_root=_REPO_ROOT).unwrap())

    assert not audit.undeclared, audit.undeclared


def test_aggregate_refuses_an_undeclared_member_before_dispatching_checks(
    *, tmp_path: Path
) -> None:
    """A missing declaration names the member and prevents an invalid token."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, body in (("uv", _UV_STUB), ("just", _JUST_STUB)):
        executable = bin_dir / name
        executable.write_text(body, encoding="utf-8")
        executable.chmod(0o755)
    (tmp_path / "check-targets.txt").write_text(
        "check-fixture-pure  # purity: tree-pure\\n" "check-fixture-bare  # purity: tree-pure\\n",
        encoding="utf-8",
    )
    log = tmp_path / "invocations.log"
    completed = subprocess.run(
        ["bash", str(_CHECK_AGGREGATE)],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "STUB_LOG": str(log),
            "UNDECLARED_MEMBER": "check-fixture-bare",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout + completed.stderr
    invoked = log.read_text(encoding="utf-8").splitlines() if log.is_file() else []

    assert completed.returncode != 0
    assert "check-fixture-bare" in output
    assert any("green_token undeclared" in command for command in invoked)
    assert not any(command.startswith("just ") for command in invoked)
    assert not any("green_token write" in command for command in invoked)
