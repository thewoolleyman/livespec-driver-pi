# livespec-driver-pi — scenarios

Gherkin scenarios for each Driver-owned contract path in `contracts.md`. These
are the worked examples the shared resolver, the guard extension, and the
structural gate are checked against.

Each Gherkin keyword line is preceded and followed by a blank line, so every
step renders as its own paragraph. Fenced code blocks are not used to hold
Gherkin steps.

## Scenario: the installed Driver exposes the eight livespec operations

Given a project whose committed pi settings declare both livespec core and the livespec-driver-pi package

And the project is trusted

When the pi runtime loads the Driver package

Then the eight skills livespec-seed, livespec-propose-change, livespec-critique, livespec-revise, livespec-doctor, livespec-prune-history, livespec-next, and livespec-help are available

And each is invoked as /skill:livespec-<operation>

## Scenario: core-root resolution honors the operator override

Given the environment variable LIVESPEC_CORE_PLUGIN_ROOT is set to a core checkout that carries a prose directory

When a binding resolves the core root through the shared resolver

Then the resolver returns the override path

And it does not consult the governed-project, project-scope, or user-scope candidates

## Scenario: core-root resolution falls back to the governed-project checkout

Given the operator override is unset

And the governed project is the livespec core repo itself, whose own plugin directory carries a prose directory

When a binding resolves the core root

Then the resolver returns the governed project's own plugin directory

And it does not consult the project-scope or user-scope package clones

## Scenario: core-root resolution falls back to the project-scope package clone

Given the operator override is unset

And the governed project is not the livespec core repo

And core is installed as a project-scope pi package whose clone carries a prose directory

When a binding resolves the core root

Then the resolver returns the project-scope clone's plugin directory

And it does not consult the user-scope clone

## Scenario: core-root resolution falls back to the user-scope package clone

Given the operator override is unset

And the governed project is not the livespec core repo

And no project-scope package clone carries a prose directory

And core is installed as a user-scope pi package whose clone carries a prose directory

When a binding resolves the core root

Then the resolver returns the user-scope clone's plugin directory

## Scenario: a clone present but without prose fails loudly rather than resolving

Given every candidate path either is absent or exists without a prose directory

When a binding resolves the core root

Then the resolver exits non-zero

And it names every candidate it searched, in order

And the binding surfaces that diagnostic verbatim and stops

And the binding does not improvise a path or run an install command the diagnostic did not ask for

## Scenario: an override that resolves nothing is reported as a configuration error

Given the operator override is set to a path that carries no prose directory

And no other candidate carries a prose directory

When a binding resolves the core root

Then the diagnostic states that the override is set but does not resolve

And it directs the reader to fix or unset the override rather than to install anything

## Scenario: an untrusted non-interactive invocation resolves nothing

Given a project whose committed pi settings declare both packages

And no trust decision has been established for the project

When a livespec operation is driven by a non-interactive pi invocation

Then pi silently ignores the project-local settings and packages

And no binding and no extension is loaded

And the operation resolves nothing rather than reporting a missing install

And the acceptance bar for claiming pi support is therefore not met by the settings entries alone

## Scenario: the guard blocks a hook-bypassing commit or push

Given a tool call whose executed leading command passes the hook-bypass flag to a git commit or a git push

When the guard's tool_call handler runs

Then it returns a block decision

And the reason names the enforcement the flag would bypass and directs the caller to fix the failing gate

## Scenario: the guard blocks an invocation that disables lefthook

Given a tool call whose executed leading command carries an assignment disabling lefthook, at any position in its environment prefix

When the guard's tool_call handler runs

Then it returns a block decision

And the reason names the gates that would be skipped

## Scenario: the guard blocks setting a checkout bare

Given a tool call whose executed leading command sets the bare configuration key to a true value on a checkout

When the guard's tool_call handler runs

Then it returns a block decision

And the reason names the commit-refuse-hook invariant the setting would break

And a read-only query of the same configuration key is not blocked

## Scenario: the guard blocks a write at a livespec primary checkout

Given a tool call that would write a file at a repository which declares itself its own primary checkout

When the guard's tool_call handler runs

Then it returns a block decision

And the reason directs the caller to a secondary worktree and the pull-request path

## Scenario: the guard passes through a forbidden string carried as data

Given a tool call whose command carries a forbidden string as data rather than as the executed leading command

When the guard's tool_call handler runs

Then it returns no block decision

And the tool call proceeds

## Scenario: a guard error yields a pass-through rather than a block

Given a tool call whose evaluation raises inside the guard, because its input is malformed or a probe cannot run

When the guard's tool_call handler runs

Then the handler catches the error internally

And it returns no block decision

And the tool call proceeds, delivering the fail-open discipline the runtime's own fail-closed default would otherwise invert

## Scenario: prune-history is never auto-activated

Given a session that mentions history generically without invoking the operation

When the model considers which skill to use

Then the prune-history binding is not model-invocable

And the operation runs only on explicit user invocation

## Scenario: a mutating operation stops when the guard is not loaded

Given a session in which the Driver package's extensions are not loaded

When a mutating livespec operation is requested

Then the binding stops and says the guard is not in place

And it does not proceed unguarded

## Scenario: the structural gate rejects a missing or extra binding

Given the skills directory is missing one of the eight bindings, or carries an extra directory

When the structural gate runs

Then it exits non-zero

And it names the missing or unexpected binding directory

## Scenario: the structural gate rejects a non-canonical wrapper invocation

Given a fenced wrapper invocation inside a binding that resolves the wrapper through a literal plugin-scripts path, through this Driver's own package root, or under a project-resolving runner

When the structural gate runs

Then it exits non-zero

And it emits one violation naming the file and the offending invocation

## Scenario: the structural gate rejects a manifest naming an absent resource directory

Given the pi manifest declares a resource directory that the package does not contain

When the structural gate runs

Then it exits non-zero

And it reports that a manifest naming an absent directory loads nothing and reports nothing

## Scenario: a commit at the primary checkout is refused

Given a checkout whose git directory equals its common git directory

When a commit or a push is attempted

Then the commit-refuse hook exits non-zero

And it directs the contributor to use a worktree
