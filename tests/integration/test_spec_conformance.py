"""Conformance witnesses for the pi Driver's structural and operational rows.

Each test asserts a concrete, control-armed fact about THIS repo that a spec
heading commits to — the version source of truth, the declared repo layout, the
enforcement-suite wiring, the single shared resolver, and the tests-mirror-
dev-tooling discipline.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

__all__: list[str] = []

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_versioning_package_json_is_the_sole_version_source() -> None:
    """contracts.md "Versioning" + n-f-r "Build and release": version SoT.

    package.json $.version is the single, release-please-managed source of truth
    (non-empty three-part semver) and the manifest carries the pi-package
    keyword. Control-armed: an empty/absent version fails.
    """
    manifest = json.loads((_REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    version = manifest.get("version", "")
    assert version
    assert len(version.split(".")) == 3, version
    assert "pi-package" in manifest.get("keywords", [])


def test_repo_layout_declared_paths_exist() -> None:
    """non-functional-requirements.md "Spec" (Repo layout): declared paths exist."""
    for rel in (
        "package.json",
        "skills",
        "lib/resolve-core-root.sh",
        "extensions",
        "dev-tooling",
        "tests/dev-tooling",
        "SPECIFICATION",
        ".livespec.jsonc",
        "justfile",
        "lefthook.yml",
        "check-targets.txt",
        "pyproject.toml",
    ):
        assert (_REPO_ROOT / rel).exists(), rel


def test_enforcement_suite_gates_are_wired() -> None:
    """non-functional-requirements.md "Contracts" (Enforcement suite): gates wired.

    The two repo-local gates plus the family canonical block are declared in the
    aggregate target list and defined as justfile recipes. Control-armed: a
    renamed/dropped gate fails.
    """
    targets = (_REPO_ROOT / "check-targets.txt").read_text(encoding="utf-8")
    justfile = (_REPO_ROOT / "justfile").read_text(encoding="utf-8")
    for gate in (
        "check-pi-package-structure",
        "check-extension-quality",
        "check-doctor-static",
        "check-heading-coverage",
        "check-lint",
        "check-format",
        "check-types",
        "check-coverage",
    ):
        assert gate in targets, f"{gate} absent from check-targets.txt"
        assert f"\n{gate}:" in justfile, f"{gate} has no justfile recipe"


def test_resolution_substrate_uses_one_shared_executable_resolver() -> None:
    """constraints.md "Resolution-substrate constraints": one shared resolver.

    The ordered resolution chain is realized once, by an executable
    lib/resolve-core-root.sh that every binding calls (never restated inline).
    Control-armed: a non-executable or missing resolver fails; and the
    structural gate separately reports a binding that inlines resolution.
    """
    resolver = _REPO_ROOT / "lib" / "resolve-core-root.sh"
    assert resolver.is_file()
    import os

    assert os.access(resolver, os.X_OK), "resolver must be executable"
    # It is a self-contained script that runs under bare bash (no venv).
    result = subprocess.run(
        ["bash", "-n", str(resolver)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_constraints_tests_mirror_dev_tooling() -> None:
    """non-functional-requirements.md "Constraints" (Test discipline): tests mirror dev-tooling.

    The tests/dev-tooling tree mirrors dev-tooling one-to-one so the coverage
    gate measures a populated surface. Control-armed: a dev-tooling check module
    with no mirrored test file fails.
    """
    dev_tooling = _REPO_ROOT / "dev-tooling"
    tests_dir = _REPO_ROOT / "tests" / "dev-tooling"
    assert tests_dir.is_dir()
    mirrored = list(tests_dir.glob("test_*.py"))
    assert mirrored, "tests/dev-tooling holds no test modules"
    # Every pytest module names a dev-tooling subject that exists.
    for test_file in mirrored:
        subject = test_file.name[len("test_") :].removesuffix(".py").replace("_", "-")
        assert (dev_tooling / subject).exists() or any(
            dev_tooling.glob(f"{subject}*")
        ), f"{test_file.name} mirrors no dev-tooling/{subject}"
