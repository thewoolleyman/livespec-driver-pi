/**
 * livespec footgun guard — the pi Driver's ONE sanctioned first-party extension.
 *
 * Required by livespec `SPECIFICATION/contracts.md` §"Driver-shipped hooks":
 * the pi Driver MUST register a `tool_call` handler that is the behavioral port
 * of the Claude Driver's footgun guard, blocking a tool call that would
 *
 *   (a) pass `--no-verify` to `git commit` / `git push`,
 *   (b) set `LEFTHOOK=0` / `LEFTHOOK=false` to disable lefthook,
 *   (c) set `core.bare = true` on a checkout, or
 *   (d) edit files at a livespec PRIMARY checkout.
 *
 * It must be in place before any MUTATING operation (`seed`, `propose-change`,
 * `critique`, `revise`, `prune-history`) is exercised. The eight operation
 * bindings themselves stay SKILL.md skills — only the guard is an extension,
 * because a guard IS a hook and each Driver ships its hooks in its runtime's
 * native hook mechanism, which for pi is the extension `tool_call` event.
 *
 * FAIL-OPEN, DELIVERED BY HAND. The contract's fail-open discipline says a
 * guard failure (malformed input, a probe that cannot run) MUST be a silent
 * pass-through, and the guard acts only when it POSITIVELY identifies a
 * forbidden invocation. pi's own default is the OPPOSITE: a `tool_call` handler
 * that throws BLOCKS the tool (fail-closed, observed in pi v0.84.1). So every
 * code path below runs inside a try/catch that swallows and passes through.
 * Inheriting pi's default would turn a guard bug into a wedged session.
 *
 * The commit-refuse hook and branch protection are the real backstops; this
 * guard converts a silent footgun into an actionable, named block.
 */

import { execFileSync } from "node:child_process";
import { existsSync, statSync } from "node:fs";
import { dirname, isAbsolute, resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const NO_VERIFY_REASON =
	"Refusing `--no-verify`: it bypasses the lefthook gates and the family " +
	"commit-refuse hook, which are the only per-commit enforcement this fleet " +
	"has. If a hook fails, fix the cause or halt and report it.";

const LEFTHOOK_OFF_REASON =
	"Refusing a LEFTHOOK=0/false invocation: disabling lefthook silently skips " +
	"the staged-lint, commit-pair, and Red-Green-Replay gates. Fix the failing " +
	"gate instead of switching it off.";

const CORE_BARE_REASON =
	"Refusing `core.bare = true`: setting it on a primary checkout freezes the " +
	"working tree and breaks the commit-refuse-hook invariant that every " +
	"livespec repo depends on.";

const PRIMARY_EDIT_REASON =
	"NEVER edit files directly at a livespec PRIMARY checkout (a repo whose " +
	"`git config --get livespec.primaryPath` equals its own worktree root). " +
	"Direct writes at the primary are refused by the family commit-refuse hook. " +
	"Do edits in a SECONDARY worktree: `git -C <repo> worktree add " +
	"~/.worktrees/<repo>/<branch> -b <branch> origin/master`, then PR, merge, " +
	"cleanup.";

/** Wrappers that merely re-exec another command, with the flags of THEIRS that
 * consume a following argument. Each is a bypass if treated as the invocation
 * instead of stripped: `env -i git commit --no-verify` hides the git call
 * behind `env` while being no less of a bypass. */
const WRAPPER_FLAGS_WITH_ARG: Record<string, readonly string[]> = {
	command: [],
	env: ["-u", "-C", "--unset", "--chdir"],
	exec: ["-a"],
	nice: ["-n", "--adjustment"],
	nohup: [],
	setsid: [],
	stdbuf: ["-i", "-o", "-e", "--input", "--output", "--error"],
	sudo: ["-u", "-g", "-U", "-C", "-p", "--user", "--group", "--prompt"],
	time: ["-o", "-f", "--output", "--format"],
	timeout: ["-s", "-k", "--signal", "--kill-after"],
};

const GIT_GLOBAL_OPTS_WITH_ARG = [
	"-C",
	"-c",
	"--git-dir",
	"--work-tree",
	"--namespace",
	"--exec-path",
];

const ENV_ASSIGN = /^[A-Za-z_][A-Za-z0-9_]*=/;
const LEFTHOOK_OFF = /^LEFTHOOK=(?:0|false|off|no)$/i;
const DURATION = /^[0-9]+(?:\.[0-9]+)?[smhd]?$/;
const HEREDOC = /<<-?\s*['"]?([A-Za-z_][A-Za-z0-9_]*)['"]?/;

export type GuardDecision = { block: true; reason: string } | undefined;

/** Drop here-doc BODIES: they are file data, not executed commands, and
 * analyzing them as commands is a pure false-positive source. */
function stripHeredocBodies(command: string): string {
	const lines = command.split("\n");
	const out: string[] = [];
	let index = 0;
	while (index < lines.length) {
		const line = lines[index];
		out.push(line);
		const match = HEREDOC.exec(line);
		index += 1;
		if (match) {
			const terminator = match[1];
			while (index < lines.length && lines[index].trim() !== terminator) {
				index += 1;
			}
			if (index < lines.length) {
				index += 1;
			}
		}
	}
	return out.join("\n");
}

/** Split into shell segments on UNQUOTED `;` `&&` `||` `|` `&` and newline.
 * Quote state is tracked so a separator inside quotes is never a separator —
 * `echo 'a; git commit --no-verify'` is data, not an invocation. */
export function segments(command: string): string[] {
	const cleaned = stripHeredocBodies(command).replace(/\\\n/g, " ");
	const found: string[] = [];
	let current = "";
	let quote = "";
	let index = 0;
	while (index < cleaned.length) {
		const char = cleaned[index];
		if (quote) {
			current += char;
			if (char === quote) {
				quote = "";
			}
			index += 1;
			continue;
		}
		if (char === "'" || char === '"') {
			quote = char;
			current += char;
			index += 1;
			continue;
		}
		if (char === "\\" && index + 1 < cleaned.length) {
			current += char + cleaned[index + 1];
			index += 2;
			continue;
		}
		if (cleaned.slice(index, index + 2) === "&&" || cleaned.slice(index, index + 2) === "||") {
			found.push(current);
			current = "";
			index += 2;
			continue;
		}
		if (char === ";" || char === "|" || char === "&" || char === "\n") {
			found.push(current);
			current = "";
			index += 1;
			continue;
		}
		current += char;
		index += 1;
	}
	found.push(current);
	return found.map((segment) => segment.trim()).filter((segment) => segment.length > 0);
}

function tokenize(segment: string): string[] {
	return segment
		.split(/\s+/)
		.filter((token) => token.length > 0)
		.map((token) => token.replace(/^['"]|['"]$/g, ""));
}

function skipWrapperArguments(tokens: string[], start: number, base: string): number {
	const flagsWithArg = WRAPPER_FLAGS_WITH_ARG[base];
	let index = start;
	while (index < tokens.length) {
		const token = tokens[index];
		if (ENV_ASSIGN.test(token)) {
			index += 1;
			continue;
		}
		if (token === "--") {
			index += 1;
			break;
		}
		if (!token.startsWith("-") || token === "-") {
			break;
		}
		index += flagsWithArg.includes(token) ? 2 : 1;
	}
	if (base === "timeout" && index < tokens.length && DURATION.test(tokens[index])) {
		index += 1;
	}
	return index;
}

function skipMiseWrapper(tokens: string[], start: number): number {
	let index = start + 1;
	while (
		index < tokens.length &&
		(tokens[index] === "exec" || tokens[index] === "x" || tokens[index].startsWith("-"))
	) {
		index += 1;
	}
	return index;
}

/** Strip leading env-assignments and every wrapper that merely re-execs.
 * Each strip RE-EXAMINES what remains, so stacked wrappers
 * (`sudo env -i timeout 5 git commit`) reduce to the real invocation. */
export function stripLeadingNoise(tokens: string[]): {
	rest: string[];
	lefthookDisabled: boolean;
} {
	let index = 0;
	let changed = true;
	while (changed && index < tokens.length) {
		changed = false;
		while (index < tokens.length && ENV_ASSIGN.test(tokens[index])) {
			index += 1;
			changed = true;
		}
		if (index >= tokens.length) {
			break;
		}
		const base = tokens[index].split("/").pop() ?? "";
		if (base in WRAPPER_FLAGS_WITH_ARG) {
			index = skipWrapperArguments(tokens, index + 1, base);
			changed = true;
			continue;
		}
		if (base === "mise") {
			index = skipMiseWrapper(tokens, index);
			changed = true;
		}
	}
	// The disable can sit at ANY position in the stripped prefix, including
	// inside a wrapper's own environment (`sudo env LEFTHOOK=0 git commit`).
	const lefthookDisabled = tokens.slice(0, index).some((token) => LEFTHOOK_OFF.test(token));
	return { rest: tokens.slice(index), lefthookDisabled };
}

/** If tokens are a git invocation, the subcommand and the args after it. */
export function gitSubcommand(tokens: string[]): { name: string | null; args: string[] } {
	if (tokens.length === 0 || (tokens[0].split("/").pop() ?? "") !== "git") {
		return { name: null, args: [] };
	}
	let index = 1;
	while (index < tokens.length) {
		const token = tokens[index];
		if (token === "--") {
			index += 1;
			break;
		}
		if (!token.startsWith("-")) {
			break;
		}
		index += 1;
		if (GIT_GLOBAL_OPTS_WITH_ARG.includes(token) && index < tokens.length) {
			index += 1;
		}
	}
	if (index >= tokens.length) {
		return { name: null, args: [] };
	}
	return { name: tokens[index], args: tokens.slice(index + 1) };
}

function hasNoVerify(subcommand: string, args: string[]): boolean {
	if (args.includes("--no-verify")) {
		return true;
	}
	// `-n` is `--no-verify` for commit, but `--dry-run` for push — blocking it
	// on push would refuse the safest form of the command.
	return subcommand === "commit" && args.includes("-n");
}

function setsCoreBare(subcommand: string, args: string[]): boolean {
	if (subcommand !== "config") {
		return false;
	}
	const positional = args.filter((arg) => !arg.startsWith("-"));
	const keyIndex = positional.findIndex((arg) => arg.toLowerCase() === "core.bare");
	if (keyIndex === -1) {
		return false;
	}
	const value = (positional[keyIndex + 1] ?? "").toLowerCase();
	return value === "true" || value === "yes" || value === "on" || value === "1";
}

const primaryCheckoutCache = new Map<string, boolean>();

function git(args: string[], cwd: string): string | null {
	try {
		return execFileSync("git", args, {
			cwd,
			encoding: "utf8",
			timeout: 5000,
			stdio: ["ignore", "pipe", "ignore"],
		}).trim();
	} catch {
		return null;
	}
}

/** Is `path` inside a repo that is its OWN declared primary checkout? */
export function isPrimaryCheckout(path: string): boolean {
	let probe = resolve(path);
	while (!existsSync(probe) || !statSync(probe).isDirectory()) {
		const parent = dirname(probe);
		if (parent === probe) {
			return false;
		}
		probe = parent;
	}
	const cached = primaryCheckoutCache.get(probe);
	if (cached !== undefined) {
		return cached;
	}
	const toplevel = git(["rev-parse", "--show-toplevel"], probe);
	const declared = toplevel === null ? null : git(["config", "--get", "livespec.primaryPath"], probe);
	const verdict =
		toplevel !== null && declared !== null && declared !== "" && resolve(declared) === resolve(toplevel);
	primaryCheckoutCache.set(probe, verdict);
	return verdict;
}

/** Candidate write targets in a shell segment: `>`/`>>` redirections, `tee`,
 * `sed -i`, and `dd of=`. Best-effort — an unrecognized write form simply is
 * not caught here, which is the fail-open direction. */
export function writeTargets(segment: string): string[] {
	const targets: string[] = [];
	for (const match of segment.matchAll(/(?:^|\s)>{1,2}\s*([^\s;|&]+)/g)) {
		targets.push(match[1]);
	}
	const tokens = tokenize(segment);
	const base = (tokens[0] ?? "").split("/").pop() ?? "";
	if (base === "tee") {
		targets.push(...tokens.slice(1).filter((token) => !token.startsWith("-")));
	}
	if (base === "sed" && tokens.some((token) => token === "-i" || token.startsWith("-i"))) {
		targets.push(...tokens.slice(1).filter((token) => !token.startsWith("-")).slice(1));
	}
	if (base === "dd") {
		for (const token of tokens) {
			if (token.startsWith("of=")) {
				targets.push(token.slice(3));
			}
		}
	}
	return targets.filter((target) => target.length > 0 && !target.startsWith("&"));
}

function bashDecision(command: string): GuardDecision {
	for (const segment of segments(command)) {
		const { rest, lefthookDisabled } = stripLeadingNoise(tokenize(segment));
		if (lefthookDisabled) {
			return { block: true, reason: LEFTHOOK_OFF_REASON };
		}
		const { name, args } = gitSubcommand(rest);
		if (name !== null) {
			if ((name === "commit" || name === "push") && hasNoVerify(name, args)) {
				return { block: true, reason: NO_VERIFY_REASON };
			}
			if (setsCoreBare(name, args)) {
				return { block: true, reason: CORE_BARE_REASON };
			}
		}
		for (const target of writeTargets(segment)) {
			if (isPrimaryCheckout(target)) {
				return { block: true, reason: PRIMARY_EDIT_REASON };
			}
		}
	}
	return undefined;
}

function pathDecision(path: unknown): GuardDecision {
	if (typeof path !== "string" || path.length === 0) {
		return undefined;
	}
	if (isPrimaryCheckout(isAbsolute(path) ? path : resolve(path))) {
		return { block: true, reason: PRIMARY_EDIT_REASON };
	}
	return undefined;
}

/** The whole decision, exported so a test can drive it without pi's event bus. */
export function decide(toolName: string, input: Record<string, unknown>): GuardDecision {
	if (toolName === "bash") {
		const command = input.command;
		return typeof command === "string" ? bashDecision(command) : undefined;
	}
	if (toolName === "write" || toolName === "edit" || toolName === "multi_edit") {
		return pathDecision(input.path ?? input.file_path);
	}
	return undefined;
}

export default function (pi: ExtensionAPI) {
	pi.on("tool_call", (event) => {
		// The entire body is guarded: pi blocks the tool when a `tool_call`
		// handler throws, and this guard's contract is to fail OPEN.
		try {
			return decide(event.toolName, event.input as Record<string, unknown>);
		} catch {
			return undefined;
		}
	});
}
