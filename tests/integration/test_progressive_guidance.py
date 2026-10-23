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


def test_actuator_guidance_lists_the_envelope_required_fields() -> None:
    """`.ai/foreman-actuator.md`: the envelope's required fields and the snapshot.

    The envelope is refused field-by-field, so a caller that does not know the
    whole required set pays one refusal per missing field. The three snapshot
    fields are revalidated against a FRESH gather document, and a
    `session_identity` placed at the TOP LEVEL rather than inside `snapshot` is
    silently ignored — which surfaces as `session_identity_changed`, a
    diagnostic that reads as a stale value rather than as a misplaced key.
    Control-armed: dropping any required field, the snapshot triple, or the
    ignored-top-level fact fails.
    """
    text = _actuator_guidance_text()
    for field in (
        "schema_version",
        "action_id",
        "repo",
        "topic",
        "session_name",
        "snapshot",
        "tick_generation",
        "daemon_instance_id",
        "session_identity",
    ):
        assert field in text, f"the envelope field {field} is not named"
    lowered = text.casefold()
    assert "top level" in lowered or "top-level" in lowered, (
        "the misplaced top-level session_identity is not described"
    )
    assert "ignored" in lowered, "that a top-level session_identity is IGNORED is not stated"
    assert "session_identity_changed" in text, (
        "the refusal a top-level session_identity produces is not named"
    )


def test_actuator_guidance_requires_one_credential_wrapper_invocation() -> None:
    """`.ai/foreman-actuator.md`: gather, compose and act in ONE wrapper call.

    Two facts that only make sense together. The ledger subprocess shells a
    bare `bd` with `cwd=repo`, so the credential wrapper is not optional; but
    the wrapper SCRUBS `PATH` and so loses `uv`, which the plugin bin shebangs
    need — hence the `env PATH="$PATH"` re-export. And because the daemon's
    snapshot generation advances every few seconds while the wrapper's
    credstore hop is slow, splitting gather, compose and act across separate
    wrapper invocations loses the race and the actuator refuses with
    `tick_generation_changed`. Control-armed: dropping the wrapper form, the
    PATH-scrub reason, the single-invocation requirement, or the refusal it
    avoids fails.
    """
    text = _actuator_guidance_text()
    lowered = text.casefold()
    assert '/usr/local/bin/with-livespec-env.sh -- env PATH="$PATH"' in text, (
        "the working wrapper form is not given verbatim"
    )
    assert "PATH" in text and "scrub" in lowered, "the PATH scrub is not named as the reason"
    assert "uv" in text, "the tool the PATH scrub loses is not named"
    assert "tick_generation_changed" in text, (
        "the refusal a split invocation produces is not named"
    )
    for stage in ("gather", "compose", "act"):
        assert stage in lowered, f"the {stage} stage is not named"
    assert "one credential-wrapper invocation" in lowered, (
        "that the three stages run inside ONE credential-wrapper invocation is not stated"
    )


def test_actuator_guidance_names_the_dispatch_journal_as_the_audit_trail() -> None:
    """`.ai/foreman-actuator.md`: the journal path, its stage, and what it holds.

    Every actuator attempt is journaled whether it was refused or acted, under
    `stage: foreman-act`, so the journal — not the ledger and not the terminal
    scrollback — is the audit trail, and reading its tail is the fastest way to
    see what a prior session actually tried. Control-armed: naming the path
    without the stage, or without saying it records refused attempts too,
    fails.
    """
    text = _actuator_guidance_text()
    lowered = text.casefold()
    assert "tmp/fabro-dispatch-journal.jsonl" in text, "the journal path is not named"
    assert '"stage": "foreman-act"' in text, "the journal stage is not named as a record field"
    assert "audit trail" in lowered, "the journal is not identified as the audit trail"
    assert "refused or acted" in lowered, (
        "that EVERY attempt is journaled, refused or acted, is not stated"
    )
