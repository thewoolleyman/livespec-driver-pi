/**
 * Behavioral suite for the sanctioned `tool_call` footgun-guard extension.
 *
 * WHY THIS EXISTS. `check-pi-package-structure`'s `extension_violations()`
 * asserts over the guard's TEXT — one `pi.on("tool_call")` registration, the
 * four predicate tokens, an internal `catch`. Every one of those assertions
 * still passes if the guard's logic is INVERTED, because the tokens are still
 * in the file. The four blocks required by livespec
 * `SPECIFICATION/contracts.md` §"Driver-shipped hooks" are behavior, so they
 * are tested as behavior here.
 *
 * The guard exports `decide` precisely so a test can drive the whole decision
 * without pi's event bus, which is why this suite needs no pi runtime, no live
 * model, and no credentials. That is what separates it from the CLI-end-to-end
 * harness this repo deliberately does NOT ship (AGENTS.md: a mocked pi CLI
 * would verify only the mock) — there is nothing mocked below.
 *
 * FAIL-OPEN IS ALSO BEHAVIOR. pi blocks a tool when a `tool_call` handler
 * throws, so the guard's contract inverts pi's default: anything it does not
 * POSITIVELY identify must pass through. The negative cases below are
 * therefore load-bearing assertions, not filler — a guard that blocks
 * `git push -n` or a quoted string mentioning `--no-verify` is a wedged
 * session, which is the failure mode this suite exists to prevent.
 */

import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";
import { after, describe, it } from "node:test";
import {
	decide,
	gitSubcommand,
	isPrimaryCheckout,
	segments,
	stripLeadingNoise,
	writeTargets,
} from "../../extensions/livespec-footgun-guard.ts";

/** `decide` for a bash tool call — the shape pi hands the `tool_call` event. */
function bash(command: string): ReturnType<typeof decide> {
	return decide("bash", { command });
}

function blocked(command: string): boolean {
	return bash(command)?.block === true;
}

function reason(command: string): string {
	const decision = bash(command);
	assert.ok(decision, `expected a block for: ${command}`);
	return decision.reason;
}

describe("--no-verify block", () => {
	it("blocks the bare forms on commit and push", () => {
		assert.ok(blocked("git commit --no-verify -m wip"));
		assert.ok(blocked("git push --no-verify"));
	});

	it("blocks `-n` on commit, where it MEANS --no-verify", () => {
		assert.ok(blocked("git commit -n -m wip"));
	});

	it("does NOT block `-n` on push, where it means --dry-run", () => {
		// Blocking here would refuse the SAFEST form of the command — the
		// asymmetry is deliberate, so it is pinned.
		assert.equal(blocked("git push -n origin master"), false);
	});

	it("sees through stacked wrappers that merely re-exec", () => {
		assert.ok(blocked("sudo env -i timeout 5 git commit --no-verify"));
		assert.ok(blocked("mise exec -- git commit --no-verify"));
		assert.ok(blocked("nice -n 10 nohup git push --no-verify"));
		assert.ok(blocked("/usr/bin/git commit --no-verify"));
	});

	it("sees through git's own global options", () => {
		assert.ok(blocked("git -C /tmp/repo commit --no-verify"));
		assert.ok(blocked("git -c user.name=x commit --no-verify"));
	});

	it("names the enforcement it protects", () => {
		assert.match(reason("git commit --no-verify"), /lefthook|commit-refuse/i);
	});

	it("does not fire on unrelated subcommands or plain prose", () => {
		assert.equal(blocked("git status"), false);
		assert.equal(blocked("git log --oneline -n 5"), false);
		assert.equal(blocked("echo hello"), false);
	});
});

describe("LEFTHOOK=0/false block", () => {
	it("blocks every off-spelling", () => {
		for (const value of ["0", "false", "off", "no", "FALSE", "Off"]) {
			assert.ok(blocked(`LEFTHOOK=${value} git commit -m wip`), `LEFTHOOK=${value}`);
		}
	});

	it("blocks it inside a wrapper's own environment", () => {
		assert.ok(blocked("sudo env LEFTHOOK=0 git commit -m wip"));
	});

	it("does NOT block a legitimate LEFTHOOK value", () => {
		assert.equal(blocked("LEFTHOOK=1 git commit -m wip"), false);
		assert.equal(blocked("LEFTHOOK_VERBOSE=1 git commit -m wip"), false);
	});
});

describe("core.bare=true block", () => {
	it("blocks the truthy spellings", () => {
		for (const value of ["true", "yes", "on", "1", "TRUE"]) {
			assert.ok(blocked(`git config core.bare ${value}`), `core.bare ${value}`);
		}
	});

	it("does NOT block reading it, or setting it false", () => {
		assert.equal(blocked("git config --get core.bare"), false);
		assert.equal(blocked("git config core.bare false"), false);
	});
});

describe("quoting and here-doc discipline (the fail-open direction)", () => {
	it("treats a quoted mention as data, not an invocation", () => {
		assert.equal(blocked("echo 'a; git commit --no-verify'"), false);
		assert.equal(blocked('printf "%s" "git push --no-verify"'), false);
	});

	it("treats a here-doc BODY as file data", () => {
		const command = ["cat > /tmp/notes.md <<'EOF'", "git commit --no-verify", "EOF"].join("\n");
		assert.equal(blocked(command), false);
	});

	it("still inspects every segment of a real chain", () => {
		assert.ok(blocked("cd /tmp && git commit --no-verify -m wip"));
		assert.ok(blocked("true; git push --no-verify"));
	});
});

describe("malformed input passes through (pi fails CLOSED; the guard must not)", () => {
	it("ignores a non-string command and unknown tools", () => {
		assert.equal(decide("bash", {}), undefined);
		assert.equal(decide("bash", { command: 42 }), undefined);
		assert.equal(decide("read", { path: "/etc/hosts" }), undefined);
		assert.equal(decide("write", {}), undefined);
		assert.equal(decide("write", { path: "" }), undefined);
	});
});

describe("primary-checkout edit block", () => {
	const roots: string[] = [];

	function makeRepo({ primary }: { primary: boolean }): string {
		const root = mkdtempSync(join(tmpdir(), "livespec-guard-"));
		roots.push(root);
		const run = (args: string[]): void => {
			execFileSync("git", args, { cwd: root, stdio: "ignore" });
		};
		run(["init", "--quiet"]);
		if (primary) {
			// The guard's definition of a primary checkout: a repo whose
			// `livespec.primaryPath` equals its own worktree root.
			const toplevel = execFileSync("git", ["rev-parse", "--show-toplevel"], {
				cwd: root,
				encoding: "utf8",
			}).trim();
			run(["config", "livespec.primaryPath", toplevel]);
		}
		return root;
	}

	after(() => {
		// Left in tmpdir deliberately: removing them would be the only
		// destructive act in this suite, and the OS reclaims tmp.
	});

	it("identifies a repo that declares ITSELF primary", () => {
		assert.equal(isPrimaryCheckout(makeRepo({ primary: true })), true);
	});

	it("does not mistake an ordinary repo, or a non-repo, for one", () => {
		assert.equal(isPrimaryCheckout(makeRepo({ primary: false })), false);
		assert.equal(isPrimaryCheckout(mkdtempSync(join(tmpdir(), "livespec-plain-"))), false);
	});

	it("blocks a write tool aimed INTO a primary checkout", () => {
		const primary = makeRepo({ primary: true });
		const target = join(primary, "AGENTS.md");
		writeFileSync(target, "x");
		assert.equal(decide("write", { path: target })?.block, true);
		assert.equal(decide("edit", { file_path: target })?.block, true);
		assert.equal(decide("multi_edit", { path: target })?.block, true);
		assert.match(decide("write", { path: target })?.reason ?? "", /secondary worktree/i);
	});

	it("blocks a shell REDIRECTION into a primary checkout", () => {
		const primary = makeRepo({ primary: true });
		mkdirSync(join(primary, "sub"), { recursive: true });
		assert.ok(blocked(`echo x > ${join(primary, "sub", "note.txt")}`));
		assert.ok(blocked(`echo x | tee ${join(primary, "note.txt")}`));
	});

	it("leaves writes to an ordinary worktree alone", () => {
		const ordinary = makeRepo({ primary: false });
		assert.equal(decide("write", { path: join(ordinary, "file.txt") }), undefined);
		assert.equal(blocked(`echo x > ${join(ordinary, "file.txt")}`), false);
	});
});

describe("exported helpers (the parsing the four blocks all stand on)", () => {
	it("splits on UNQUOTED separators only", () => {
		assert.deepEqual(segments("a && b; c | d"), ["a", "b", "c", "d"]);
		assert.deepEqual(segments("echo 'a; b'"), ["echo 'a; b'"]);
	});

	it("strips env-assignments and wrappers down to the real invocation", () => {
		const stripped = stripLeadingNoise(["sudo", "env", "-i", "timeout", "5", "git", "commit"]);
		assert.deepEqual(stripped.rest, ["git", "commit"]);
		assert.equal(stripped.lefthookDisabled, false);
		assert.equal(stripLeadingNoise(["env", "LEFTHOOK=0", "git", "commit"]).lefthookDisabled, true);
	});

	it("finds the git subcommand past global options", () => {
		assert.deepEqual(gitSubcommand(["git", "-C", "/tmp", "commit", "-m", "x"]), {
			name: "commit",
			args: ["-m", "x"],
		});
		assert.equal(gitSubcommand(["ls", "-la"]).name, null);
		assert.equal(gitSubcommand([]).name, null);
	});

	it("recognizes the write forms it claims to recognize", () => {
		assert.deepEqual(writeTargets("echo x > out.txt"), ["out.txt"]);
		assert.deepEqual(writeTargets("echo x >> out.txt"), ["out.txt"]);
		// Fed a SEGMENT, as `bashDecision` feeds it: `segments()` has already
		// split on the pipe, so `tee` is the segment's own command word. The
		// end-to-end pipe case is covered by the redirection block above.
		assert.deepEqual(writeTargets("tee out.txt"), ["out.txt"]);
		assert.deepEqual(writeTargets("dd if=/dev/zero of=out.img"), ["out.img"]);
		assert.deepEqual(writeTargets("sed -i s/a/b/ out.txt"), ["out.txt"]);
		assert.deepEqual(writeTargets("cat out.txt"), []);
	});
});
