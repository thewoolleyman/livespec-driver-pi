"""Positive control for the `check-shell-quality` gate.

`check-shell-quality` is wired into `check-targets.txt` and CI, and it runs
over this repo's five first-party shell files (`lib/resolve-core-root.sh` plus
the `dev-tooling/` scripts). It is green. Nothing in the repo, until this file,
demonstrated that it CAN be red — and a gate whose failure path is never
exercised is indistinguishable from one that silently inspects nothing. That is
not hypothetical here: `check-skill-invocation-paths` is armed in this same
repo and VACUOUSLY SKIPS, which is why `check-pi-package-structure` had to be
written, and `check-agents-ai-references-resolve` was armed-but-unfirable until
the `.ai/` tree landed.

So both directions are asserted: a conforming shell surface passes, and a
non-conforming one FAILS with the finding that names the reason. Ported from
`livespec-driver-codex` `tests/test_shell_quality_gate.py`; the analogue in
`livespec-driver-claude` is `tests/hooks/test_shell_quality_migration.py`.

The verifier is driven IN-PROCESS (`shell_quality.main()` against a
monkeypatched cwd), per the repo's no-subprocess-spawn test discipline. The
only real subprocess is `git`, building the throwaway fixture repo the
verifier's own repo-scoping needs.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from livespec_dev_tooling.checks import shell_quality

if TYPE_CHECKING:
    import pytest

_CLEAN_SCRIPT = "#!/usr/bin/env bash\nset -euo pipefail\nprintf '%s\\n' clean\n"


def _git(*, cwd: Path, argv: list[str]) -> None:
    _ = subprocess.run(
        ["git", *argv],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_shell_repo(*, repo: Path, justfile: str) -> None:
    """A throwaway repo carrying one clean shell script and the given justfile.

    The script is CLEAN in both cases: the failing case below differs only in
    the justfile, so a red result can only come from the justfile-borne rule
    under test, never from an incidentally sloppy script.
    """
    scripts = repo / "scripts"
    scripts.mkdir()
    (scripts / "clean.sh").write_text(_CLEAN_SCRIPT, encoding="utf-8")
    (repo / "justfile").write_text(justfile, encoding="utf-8")
    _git(cwd=repo, argv=["init"])
    _git(cwd=repo, argv=["add", "scripts/clean.sh"])


def _shell_quality(
    *,
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> tuple[int, str]:
    monkeypatch.chdir(repo)
    rc = shell_quality.main()
    return rc, capsys.readouterr().err


def test_shell_quality_accepts_a_conforming_surface(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write_shell_repo(repo=tmp_path, justfile="check:\n    bash scripts/clean.sh\n")

    rc, stderr = _shell_quality(repo=tmp_path, monkeypatch=monkeypatch, capsys=capsys)

    assert rc == 0, stderr


def test_shell_quality_rejects_just_interpolation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The positive control: a `just` interpolation inside a recipe body.

    Assembled from fragments so this file cannot trip the very rule it asserts
    when the gate scans THIS repo.
    """
    interpolation = "{{" + "args" + "}}"
    _write_shell_repo(repo=tmp_path, justfile=f"check *args:\n    echo {interpolation}\n")

    rc, stderr = _shell_quality(repo=tmp_path, monkeypatch=monkeypatch, capsys=capsys)

    assert rc == 1
    assert '"reason": "just-interpolation"' in stderr
