"""Integration-tier realizations of the core-root-resolution scenarios.

Node ids live under `tests.integration.` (an allowlisted scenario tier). Each
test drives the real shipped resolver `lib/resolve-core-root.sh` end to end as a
bash subprocess against hermetic fixture trees and a controlled environment,
asserting the observable contract: the resolved absolute path on stdout with
exit 0, or the install/config diagnostic on stderr with exit 1. No live host,
network, or pi runtime is involved.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

__all__: list[str] = []

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESOLVER = _REPO_ROOT / "lib" / "resolve-core-root.sh"
_CORE_CLONE_SUFFIX = "git/github.com/thewoolleyman/livespec/.claude-plugin"


def _run(
    *, project_root: Path, env_home: Path, override: str | None
) -> subprocess.CompletedProcess[str]:
    env = {"PATH": "/usr/bin:/bin", "HOME": str(env_home)}
    if override is not None:
        env["LIVESPEC_CORE_PLUGIN_ROOT"] = override
    return subprocess.run(
        ["bash", str(_RESOLVER), str(project_root)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def _make_prose(*, plugin_dir: Path) -> Path:
    (plugin_dir / "prose").mkdir(parents=True, exist_ok=True)
    (plugin_dir / "prose" / "seed.md").write_text("prose\n", encoding="utf-8")
    return plugin_dir


def test_scenario_resolution_honors_the_operator_override(tmp_path: Path) -> None:
    override = _make_prose(plugin_dir=tmp_path / "override" / ".claude-plugin")
    proj = tmp_path / "proj"
    proj.mkdir()
    result = _run(project_root=proj, env_home=tmp_path / "home", override=str(override))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(override)


def test_scenario_resolution_falls_back_to_governed_project_checkout(tmp_path: Path) -> None:
    proj = tmp_path / "core"
    checkout = _make_prose(plugin_dir=proj / ".claude-plugin")
    result = _run(project_root=proj, env_home=tmp_path / "home", override=None)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(checkout)


def test_scenario_resolution_falls_back_to_project_scope_package_clone(tmp_path: Path) -> None:
    proj = tmp_path / "proj"
    clone = _make_prose(plugin_dir=proj / ".pi" / _CORE_CLONE_SUFFIX)
    result = _run(project_root=proj, env_home=tmp_path / "home", override=None)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(clone)


def test_scenario_resolution_falls_back_to_user_scope_package_clone(tmp_path: Path) -> None:
    proj = tmp_path / "proj"
    proj.mkdir()
    home = tmp_path / "home"
    clone = _make_prose(plugin_dir=home / ".pi" / "agent" / _CORE_CLONE_SUFFIX)
    result = _run(project_root=proj, env_home=home, override=None)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(clone)


def test_scenario_clone_present_but_without_prose_fails_loudly(tmp_path: Path) -> None:
    proj = tmp_path / "proj"
    # A project-scope clone directory that exists but carries no prose/.
    (proj / ".pi" / _CORE_CLONE_SUFFIX).mkdir(parents=True)
    result = _run(project_root=proj, env_home=tmp_path / "home", override=None)
    assert result.returncode == 1
    assert "no candidate carries a prose" in result.stderr


def test_scenario_override_that_resolves_nothing_is_a_configuration_error(tmp_path: Path) -> None:
    proj = tmp_path / "proj"
    proj.mkdir()
    # Override set to a path that carries no prose/, and no other candidate does.
    bogus = tmp_path / "bogus"
    bogus.mkdir()
    result = _run(project_root=proj, env_home=tmp_path / "home", override=str(bogus))
    assert result.returncode == 1
    assert "configuration error" in result.stderr
    # Directs the reader to fix/unset the override rather than to install.
    assert "fix or unset" in result.stderr
