"""Tests for `dev-tooling/check-spec-governance-default-block`.

The check is a thin adapter: it calls the shared
`livespec_runtime.spec_governance` verifier and maps the Result onto a process
exit code. The verifier itself is the runtime library's own tested surface, so
these tests substitute a fake for it and assert only the mapping — success
prints the payload and exits 0, failure prints the reason and exits 2, and
anything that is neither is an internal error rather than a silent pass.

Each fake echoes the `path` it was handed into its own return value, so the
tests also pin the argument the adapter passes: the check must verify
`.livespec.jsonc` relative to the invocation directory, and a fake that ignored
the path could not tell a correct call from one aimed at the wrong file.
"""

from __future__ import annotations

import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from returns.result import Failure, Result, Success

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_PATH = REPO_ROOT / "dev-tooling" / "check-spec-governance-default-block"


def _load() -> ModuleType:
    """Import the extensionless check script as a module (no `.py` suffix)."""
    loader = SourceFileLoader("check_spec_governance_default_block", str(CHECK_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


CHECK = _load()


def _succeeds(*, path: Path) -> Result[dict[str, object], str]:
    return Success({"key_count": 9, "path": str(path)})


def _fails(*, path: Path) -> Result[dict[str, object], str]:
    return Failure(f"block-drifted at {path}")


def _returns_neither(*, path: Path) -> object:
    """Neither track — the shape an upstream contract change could introduce."""
    return {"path": str(path)}


def test_success_prints_the_payload_and_exits_zero(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    monkeypatch.setattr(CHECK, "verify_livespec_jsonc_default_block", _succeeds)
    assert CHECK.main() == 0
    assert json.loads(capsys.readouterr().out) == {
        "key_count": 9,
        "path": ".livespec.jsonc",
    }


def test_failure_prints_the_reason_and_exits_two(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    monkeypatch.setattr(CHECK, "verify_livespec_jsonc_default_block", _fails)
    assert CHECK.main() == 2
    assert capsys.readouterr().err.strip() == "block-drifted at .livespec.jsonc"


def test_a_result_that_is_neither_track_is_an_internal_error(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    """The fall-through arm is unreachable through the real verifier, and that is
    exactly why it is worth pinning: it exists so an upstream contract change
    surfaces as a named internal error instead of a silent exit 0."""
    monkeypatch.setattr(CHECK, "verify_livespec_jsonc_default_block", _returns_neither)
    assert CHECK.main() == 2
    assert "internal-error" in capsys.readouterr().err
