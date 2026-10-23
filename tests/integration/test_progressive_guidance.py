"""Conformance witnesses for this repo's `.ai/` progressive-guidance tree.

`AGENTS.md` section "Progressive guidance" is the mechanism that makes a
`.ai/<topic>.md` file something a future session READS BEFORE acting, and
`check-agents-ai-references-resolve` is what keeps each such reference from
dangling. These tests witness the foreman/actuator mechanics file and the two
`AGENTS.md` facts that carry it, so a later edit that drops a mechanic — or
unroutes the file — fails here rather than costing another session the five
`foreman-act` refusals that produced it (work-item `livespec-driver-pi-ulvjs2`).

Each test reads the committed bytes, not a fixture: the assertion under grade
is about what THIS repository ships, so a fixture would witness the fixture.
"""

from __future__ import annotations

from pathlib import Path

__all__: list[str] = []

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ACTUATOR_GUIDANCE = _REPO_ROOT / ".ai" / "foreman-actuator.md"


def _actuator_guidance_text() -> str:
    """The committed `.ai/foreman-actuator.md`, asserted present before reading.

    The presence assertion is deliberately the FIRST thing every test does: an
    absent file must fail as a genuine assertion naming the missing path, never
    as a `FileNotFoundError` from a read whose failure says nothing about which
    guidance mechanic is owed.
    """
    assert _ACTUATOR_GUIDANCE.is_file(), f"{_ACTUATOR_GUIDANCE} does not exist"
    return _ACTUATOR_GUIDANCE.read_text(encoding="utf-8")


def test_actuator_guidance_states_proposal_takes_a_file_path() -> None:
    """`.ai/foreman-actuator.md`: `--proposal` takes a path, not inline JSON.

    The first of the five measured refusals that produced this file. Passing the
    envelope as an inline JSON argument does not fail validation — it fails in
    `pathlib`, with a `FileNotFoundError` whose text names the JSON itself, so
    the diagnostic reads as a missing file rather than as a wrong argument
    shape. Control-armed: a file that names the flag without stating the
    path-not-JSON fact, or without naming the error it actually raises, fails.
    """
    text = _actuator_guidance_text()
    lowered = text.casefold()
    assert "--proposal" in text, "the proposal flag is not named"
    assert "file path" in lowered, "the file-path requirement is not stated"
    assert "inline json" in lowered, "the inline-JSON mistake is not named"
    assert "FileNotFoundError" in text, "the error inline JSON actually raises is not named"
