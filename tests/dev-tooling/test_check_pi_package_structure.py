"""Tests for `dev-tooling/check-pi-package-structure`.

Two jobs. First, drive every branch of the check against synthetic package
trees, so the check itself is known to FAIL when it should — a structural gate
that has only ever been run against a conforming tree is an unverified gate.
Second, run it against THIS repository's real tree, which is the assertion that
the shipped pi package actually conforms.
"""

from __future__ import annotations

import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_PATH = REPO_ROOT / "dev-tooling" / "check-pi-package-structure"


def _load() -> ModuleType:
    """Import the extensionless check script as a module.

    The file has no `.py` suffix (it is an executable, matching its sibling in
    `dev-tooling/`), so the ordinary import machinery cannot find it and an
    explicit `SourceFileLoader` is required.
    """
    loader = SourceFileLoader("check_pi_package_structure", str(CHECK_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


CHECK = _load()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(text, encoding="utf-8")


def _skill_text(*, operation: str, extra_frontmatter: str = "", body_extra: str = "") -> str:
    return (
        f"---\nname: livespec-{operation}\n"
        f"description: Drives the {operation} operation.\n"
        f"{extra_frontmatter}---\n\n"
        "Resolve via `lib/resolve-core-root.sh`.\n\n"
        "```bash\n"
        f'python3 "$LIVESPEC_CORE_ROOT/scripts/bin/{operation.replace("-", "_")}.py"\n'
        "```\n"
        f"{body_extra}"
    )


def _conforming_root(tmp_path: Path) -> Path:
    for operation in CHECK.OPERATIONS:
        extra = "disable-model-invocation: true\n" if operation == "prune-history" else ""
        body = "Requires explicit user invocation.\n" if operation == "prune-history" else ""
        _write(
            tmp_path / "skills" / f"livespec-{operation}" / "SKILL.md",
            _skill_text(operation=operation, extra_frontmatter=extra, body_extra=body),
        )
    resolver = tmp_path / "lib" / "resolve-core-root.sh"
    _write(resolver, "#!/usr/bin/env bash\n")
    resolver.chmod(0o755)
    _write(
        tmp_path / "package.json",
        json.dumps(
            {
                "name": "livespec-driver-pi",
                "keywords": ["pi-package"],
                "pi": {"skills": ["./skills"], "extensions": ["./extensions"]},
            }
        ),
    )
    _write(
        tmp_path / "extensions" / "livespec-footgun-guard.ts",
        'pi.on("tool_call", () => {\n'
        "  try { return undefined; } catch { return undefined; }\n"
        "});\n"
        "// --no-verify LEFTHOOK core.bare livespec.primaryPath\n",
    )
    return tmp_path


def test_conforming_synthetic_tree_has_no_violations(tmp_path: Path) -> None:
    assert CHECK.violations(root=_conforming_root(tmp_path)) == []


def test_this_repository_conforms() -> None:
    assert CHECK.violations(root=REPO_ROOT) == []


def test_missing_skill_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    (root / "skills" / "livespec-doctor" / "SKILL.md").unlink()
    assert any(
        "missing SKILL.md for operation 'doctor'" in item for item in CHECK.violations(root=root)
    )


def test_undeclared_skill_directory_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    _write(root / "skills" / "livespec-invented" / "SKILL.md", _skill_text(operation="invented"))
    assert any("undeclared skill" in item for item in CHECK.violations(root=root))


def test_absent_skills_directory_reports_only_missing_files(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    for operation in CHECK.OPERATIONS:
        (root / "skills" / f"livespec-{operation}" / "SKILL.md").unlink()
        (root / "skills" / f"livespec-{operation}").rmdir()
    (root / "skills").rmdir()
    found = CHECK.violations(root=root)
    missing = [item for item in found if "missing SKILL.md" in item]
    assert len(missing) == len(CHECK.OPERATIONS)


def test_frontmatter_tolerates_an_unterminated_block_and_colonless_lines() -> None:
    """Both shapes occur in hand-edited frontmatter, and neither may raise: the
    check reports a defect, it never crashes the gate that would report it."""
    parsed = CHECK.frontmatter(text="---\nname: livespec-seed\nstray line with no colon\n")
    assert parsed == {"name": "livespec-seed"}


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("name: wrong-name\ndescription: x\n", "expected 'livespec-seed'"),
        ("name: livespec-seed\n", "carries no description"),
        ("name: Livespec-Seed\ndescription: x\n", "breaks the Agent Skills name rules"),
    ],
)
def test_frontmatter_defects_are_reported(tmp_path: Path, mutation: str, expected: str) -> None:
    root = _conforming_root(tmp_path)
    path = root / "skills" / "livespec-seed" / "SKILL.md"
    _write(path, f"---\n{mutation}---\n\nlib/resolve-core-root.sh\n")
    assert any(expected in item for item in CHECK.skill_violations(operation="seed", path=path))


def test_no_frontmatter_block_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    path = root / "skills" / "livespec-seed" / "SKILL.md"
    _write(path, "no frontmatter here\nlib/resolve-core-root.sh\n")
    assert CHECK.frontmatter(text=path.read_text(encoding="utf-8")) == {}
    assert CHECK.skill_violations(operation="seed", path=path) != []


def test_claude_plugin_skills_reference_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    path = root / "skills" / "livespec-seed" / "SKILL.md"
    _write(path, _skill_text(operation="seed", body_extra="See .claude-plugin/skills/seed.\n"))
    assert any("references .claude-plugin/skills" in item for item in CHECK.violations(root=root))


def test_inline_resolution_without_the_shared_resolver_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    path = root / "skills" / "livespec-seed" / "SKILL.md"
    _write(path, "---\nname: livespec-seed\ndescription: x\n---\n\nresolve it yourself\n")
    assert any(
        "does not delegate core-root resolution" in item for item in CHECK.violations(root=root)
    )


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ('uv run python3 "$LIVESPEC_CORE_ROOT/scripts/bin/seed.py"', "uses `uv run`"),
        ("python3 .claude-plugin/scripts/bin/seed.py", "hard-codes .claude-plugin/scripts"),
        ("python3 ./scripts/bin/seed.py", "lacks the canonical"),
    ],
)
def test_noncanonical_fenced_invocations_are_reported(
    tmp_path: Path, command: str, expected: str
) -> None:
    root = _conforming_root(tmp_path)
    path = root / "skills" / "livespec-seed" / "SKILL.md"
    _write(
        path,
        "---\nname: livespec-seed\ndescription: x\n---\n\n"
        "lib/resolve-core-root.sh\n\n```bash\n" + command + "\n```\n",
    )
    assert any(expected in item for item in CHECK.skill_violations(operation="seed", path=path))


def test_wrapper_reference_outside_a_fence_is_narration(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    path = root / "skills" / "livespec-seed" / "SKILL.md"
    _write(
        path,
        "---\nname: livespec-seed\ndescription: x\n---\n\n"
        "lib/resolve-core-root.sh\n\nNever call bin/seed.py directly.\n",
    )
    assert CHECK.fenced_invocations(text=path.read_text(encoding="utf-8")) == []
    assert CHECK.skill_violations(operation="seed", path=path) == []


@pytest.mark.parametrize(
    ("extra", "body", "expected"),
    [
        ("", "Requires explicit user invocation.\n", "disable-model-invocation"),
        ("disable-model-invocation: true\n", "", "explicit-user-invocation only"),
    ],
)
def test_prune_history_controls_are_required(
    tmp_path: Path, extra: str, body: str, expected: str
) -> None:
    root = _conforming_root(tmp_path)
    path = root / "skills" / "livespec-prune-history" / "SKILL.md"
    _write(path, _skill_text(operation="prune-history", extra_frontmatter=extra, body_extra=body))
    assert any(expected in item for item in CHECK.violations(root=root))


def test_missing_resolver_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    (root / "lib" / "resolve-core-root.sh").unlink()
    assert any(
        "missing the shared core-root resolver" in item for item in CHECK.violations(root=root)
    )


def test_non_executable_resolver_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    (root / "lib" / "resolve-core-root.sh").chmod(0o644)
    assert any("is not executable" in item for item in CHECK.violations(root=root))


def test_missing_manifest_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    (root / "package.json").unlink()
    assert any("missing pi package manifest" in item for item in CHECK.violations(root=root))


def test_malformed_manifest_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    _write(root / "package.json", "{not json")
    assert any("not valid JSON" in item for item in CHECK.manifest_violations(root=root))


def test_manifest_without_the_pi_package_keyword_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    _write(
        root / "package.json",
        json.dumps({"pi": {"skills": ["./skills"], "extensions": ["./extensions"]}}),
    )
    assert any("must include 'pi-package'" in item for item in CHECK.manifest_violations(root=root))


def test_manifest_without_a_pi_block_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    _write(root / "package.json", json.dumps({"keywords": ["pi-package"]}))
    assert any(
        "carries no `pi` manifest block" in item for item in CHECK.manifest_violations(root=root)
    )


def test_manifest_with_wrong_resource_paths_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    _write(
        root / "package.json",
        json.dumps(
            {
                "keywords": ["pi-package"],
                "pi": {"skills": ["./bindings"], "extensions": ["./extensions"]},
            }
        ),
    )
    assert any(
        "pi.skills is ['./bindings']" in item for item in CHECK.manifest_violations(root=root)
    )


def test_manifest_naming_an_absent_directory_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    (root / "extensions" / "livespec-footgun-guard.ts").unlink()
    (root / "extensions").rmdir()
    assert any("which does not exist" in item for item in CHECK.manifest_violations(root=root))


def test_missing_extension_is_reported(tmp_path: Path) -> None:
    root = _conforming_root(tmp_path)
    (root / "extensions" / "livespec-footgun-guard.ts").unlink()
    assert any(
        "missing the sanctioned tool_call" in item for item in CHECK.extension_violations(root=root)
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("// no registration at all\n", "registers 0 tool_call handlers"),
        (
            'pi.on("tool_call", a);\npi.on("tool_call", b);\n// --no-verify LEFTHOOK core.bare '
            "livespec.primaryPath catch\n",
            "registers 2 tool_call handlers",
        ),
        (
            'pi.on("tool_call", a);\n// LEFTHOOK core.bare livespec.primaryPath catch\n',
            "the --no-verify block",
        ),
        (
            'pi.on("tool_call", a);\n// --no-verify LEFTHOOK core.bare livespec.primaryPath\n',
            "no internal catch",
        ),
    ],
)
def test_extension_defects_are_reported(tmp_path: Path, source: str, expected: str) -> None:
    root = _conforming_root(tmp_path)
    _write(root / "extensions" / "livespec-footgun-guard.ts", source)
    assert any(expected in item for item in CHECK.extension_violations(root=root))


def test_main_exits_zero_and_summarizes_on_a_conforming_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    monkeypatch.chdir(_conforming_root(tmp_path))
    assert CHECK.main() == 0
    assert json.loads(capsys.readouterr().out)["check_id"] == "pi-package-structure-ok"


def test_main_exits_two_and_names_each_violation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    root = _conforming_root(tmp_path)
    (root / "package.json").unlink()
    monkeypatch.chdir(root)
    assert CHECK.main() == 2
    assert "missing pi package manifest" in capsys.readouterr().err
