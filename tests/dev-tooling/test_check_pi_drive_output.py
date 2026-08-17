"""Tests for `dev-tooling/check-pi-drive-output`."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_PATH = REPO_ROOT / "dev-tooling" / "check-pi-drive-output"


def _load() -> ModuleType:
    assert CHECK_PATH.is_file()
    loader = SourceFileLoader("check_pi_drive_output", str(CHECK_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_zero_exit_pi_model_400_is_classified_as_failed() -> None:
    check = _load()
    transcript = (
        "starting /skill:livespec-doctor\n"
        "Error: model call failed with status 400: Bad Request\n"
    )

    result = check.classify_drive(pi_exit_code=0, stdout=transcript, stderr="")

    assert result == check.DriveClassification(
        ok=False,
        reason="pi-output-model-call-failed",
        matched_line="Error: model call failed with status 400: Bad Request",
    )


def test_nonzero_pi_exit_is_classified_as_failed_without_output_match() -> None:
    check = _load()

    result = check.classify_drive(pi_exit_code=7, stdout="", stderr="")

    assert result == check.DriveClassification(
        ok=False,
        reason="pi-process-exited-nonzero",
        matched_line="pi exited 7",
    )


def test_clean_zero_exit_transcript_is_classified_as_success() -> None:
    check = _load()

    result = check.classify_drive(
        pi_exit_code=0,
        stdout="completed /skill:livespec-help\n",
        stderr="",
    )

    assert result == check.DriveClassification(
        ok=True,
        reason="pi-drive-ok",
        matched_line="",
    )


def test_cli_maps_failure_to_nonzero_and_reports_reason(tmp_path: Path, capsys: Any) -> None:
    check = _load()
    stdout_path = tmp_path / "stdout.txt"
    stderr_path = tmp_path / "stderr.txt"
    _ = stdout_path.write_text("Error: Request failed with status code 400\n", encoding="utf-8")
    _ = stderr_path.write_text("", encoding="utf-8")

    assert (
        check.main(
            argv=[
                "--pi-exit-code",
                "0",
                "--stdout",
                str(stdout_path),
                "--stderr",
                str(stderr_path),
            ]
        )
        == 2
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "pi-output-model-call-failed" in captured.err
