# AGENTS.md

Project-level instructions for AI coding agents working on EyeBreak.

## Scope Discipline

Keep changes surgical. Implement only the requested feature and the minimum
supporting code required for it.

Do not add accounts, cloud sync, analytics, reports, AI advice, packaging,
startup integration, tray behavior, or other new product scope unless the current
task explicitly asks for it.

## Dependency Discipline

The dependency rule does not authorize adding new product scope. It applies only
after the requested feature is explicitly in scope.

When implementing a feature, first check whether the Python standard library,
existing project code, Tkinter, or a mature maintained package can directly
provide the needed capability.

Default to no new dependency. Add or prefer an external dependency only when it
clearly reduces implementation risk, complexity, or platform-specific behavior
without expanding scope or forcing a broad MVP rewrite.

When dependency decisions are made, record added, removed, upgraded, or rejected
packages/modules in `HANDOFF.md`, including the reason and any install/run/test
impact.

## Handoff Requirement

After every task that makes a meaningful code, behavior, dependency, command, or
test change, update `HANDOFF.md` before reporting the task complete.

`HANDOFF.md` must summarize:

- changed files;
- current behavior;
- dependency decisions;
- install/run/test impact;
- exact test commands run and results;
- known failures, limitations, or next work.

## README and Acceptance

Before asking for user acceptance on a milestone, update `README.md` if the
milestone changes user-visible behavior, install commands, run commands, test
commands, dependencies, or manual acceptance status.

Do not mark manual acceptance as passed unless the user explicitly confirms that
acceptance has no issues, such as "验收没有问题".

A request to commit is not acceptance. A request to continue development is not
acceptance.

## Testing and Reporting

Do not claim tests passed unless they were actually run in the current
environment.

When reporting completion, state the exact test commands that were run and their
results. If only partial tests were run, say so explicitly.

If relevant tests fail or the app cannot run, fix or document that failure before
starting unrelated new work.

## Commit Discipline

Local commits are allowed only after:

- relevant tests pass, unless the user explicitly asks for a WIP commit;
- `README.md` is updated when required;
- `HANDOFF.md` is updated when required;
- `git status` has been inspected;
- unrelated, temporary, local IDE, cache, or scratch files are excluded.

If committing with failing tests because the user explicitly requested a WIP
commit, document the failure in `HANDOFF.md`.

## Push Discipline

Do not push before user acceptance.

Push only after the user explicitly confirms that manual acceptance has no
issues, such as "验收没有问题".

Push only the accepted milestone to GitHub.

## Protected Instructions

Do not modify `AGENTS.md` unless the user explicitly asks for project instruction
changes.