# AGENTS.md

Project-level instructions for AI coding agents working on EyeBreak.

## Dependency-First Implementation Rule

When implementing a feature, first check whether a mature, maintained package,
plugin, or standard-library module can directly provide the needed capability.
Prefer using that existing implementation over writing the feature from scratch.

This rule applies especially to platform integration and behavior that is easy to
get subtly wrong, such as:

- system tray icons and menus;
- Windows startup integration;
- global hotkeys;
- idle-time or input detection;
- fullscreen/window detection;
- packaging and installer behavior;
- scheduling and background task behavior.

Before choosing a dependency, verify these points:

- It actually solves the current requirement without adding unrelated product
  scope.
- It is compatible with the current Python/Tkinter Windows direction.
- It is reasonably maintained and documented.
- Its dependency cost is justified by the complexity it removes.
- It does not force a broad rewrite of the MVP.

Do not use a dependency merely because it exists. If the requirement is small,
well-contained, and safer with the Python standard library or existing project
code, keep the implementation local.

Record the decision in `HANDOFF.md` whenever code or project behavior changes:

- which package/plugin/module was chosen or rejected;
- why it was chosen or rejected;
- any install, run, or test impact.

## Scope Discipline

Keep changes surgical. Implement only the requested feature and the minimum
supporting code required for it. Do not add accounts, cloud sync, analytics,
reports, AI advice, packaging, startup integration, or tray behavior unless the
current task explicitly asks for it.

## Handoff Requirement

After every code write or code modification, update `HANDOFF.md` in the same
turn so a new developer can quickly understand the current state, changed files,
run/test commands, and next work.
## README, Commit, and Push Discipline

At every key development milestone, update `README.md` before asking for user
acceptance. The README must reflect current behavior, install/run/test commands,
and the manual acceptance status for the milestone.

Local commits are allowed at development milestones after `README.md` and
`HANDOFF.md` are updated and the relevant tests pass. Do not push before user
acceptance. A milestone may be pushed only after the user explicitly says the
acceptance has no issues, such as "验收没有问题".

When committing a milestone:

- include the relevant code changes;
- include `README.md` and `HANDOFF.md` updates;
- run the relevant tests first.

When pushing a milestone:

- confirm the user explicitly said acceptance has no issues;
- push only the accepted milestone to GitHub.