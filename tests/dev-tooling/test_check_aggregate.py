"""Regression checks for the repository check-aggregate runner."""

from __future__ import annotations

from pathlib import Path

from livespec_dev_tooling.check_purity import audit_check_purity
from returns.unsafe import unsafe_perform_io

__all__: list[str] = []

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_every_aggregate_member_declares_its_purity() -> None:
    """A token memoizes only members whose declaration makes that sound."""
    targets = tuple(
        line.split("#", maxsplit=1)[0].strip()
        for line in (_REPO_ROOT / "check-targets.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )

    audit = unsafe_perform_io(audit_check_purity(targets=targets, repo_root=_REPO_ROOT).unwrap())

    assert not audit.undeclared, audit.undeclared
