# Pi settings and account-label preservation Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to execute task-by-task. The user selected direct execution and approved ordinary validation without initializing no-mistakes.

**Goal:** Preserve the current Pi/Herdr settings, account launchers, and the approved per-session account labels in the existing GitHub repositories.

**Architecture:** Copy the live non-secret settings and launcher scripts into the existing chezmoi source worktree. Commit the Herdr display-only change in its existing plugin worktree. Push only the two approved feature branches; do not alter runtime configuration or merge main.

**Tech Stack:** Git, chezmoi, Bash/Python, Rust 1.95.0.

**Spec:** User-approved in-chat plan of 2026-10-06: save the current settings and three account launchers with their two helper scripts, save the approved display labels in the private plugin repository, validate in an isolated HOME, and perform ordinary feature-branch pushes.

## Global Constraints
- Settings and launcher scripts go to the existing public dotfiles repository, branch `feat/pi-herdr-multi-account`.
- Display-only code goes to the existing private plugin repository, branch `fix/pi-own-auth-quota`, remote `private` (not upstream `origin` or obsolete `fork`).
- No auth.json, MCP credentials, tokens, sessions, runtime caches, node_modules or build binaries in commits.
- Preserve pre-existing untracked files unless named in this plan; never use git add -A.
- No main merge, PR creation, force push, installation, production launcher execution, or no-mistakes initialization.
- This is a snapshot of current behavior, not a new environment installer: local Pi package paths still require their own repositories and machine-specific placement.

## Review Focus
- Public snapshots must not expose real authentication material.
- Wrapper arguments containing spaces must survive unchanged.
- rbx/muu must use their own auth files rather than sharing kuno auth.
- Helper scripts must be included when account launchers depend on them.
- A successful local commit must not be reported as a successful push; compare each remote branch SHA.

### Task 1: Save the dotfiles snapshot
**Files:**
- Modify: `dot_pi/agent/settings.json` (copy live file exactly; no behavior edits).
- Add existing: `dot_local/bin/executable_pi-account`, `dot_local/bin/executable_pi-extension-deps-patch`, `dot_local/bin/test_pi_startup_warnings.py`.
- Create: `dot_local/bin/executable_pi-kuno`, `executable_pi-rbx`, `executable_pi-muu`, `executable_pi-hermes-realpath-patch`, `test_pi_account_launchers.py`.
- Preserve tracked Herdr configuration unchanged when it already matches the live file.
**Interfaces:** The three shell launchers call pi-account with kuno/rbx/muu and unchanged arguments. pi-account uses the two saved patch helpers and delegates to pi with profile-local auth.
- [ ] Write a launcher test that runs the actual exported wrappers under a synthetic HOME with fake Pi and local fixtures; watch it fail while wrappers are absent.
- [ ] Copy the settings and missing scripts without changing live files or overwriting unrelated edits.
- [ ] Run Python unittest discovery for `test_pi*.py`, shell syntax checks, JSON parsing and content equality checks. Expected: all pass, no changes to live credential files.
- [ ] Review the selected files for secrets, local-only dependencies and unintended changes.
- [ ] Commit only the explicit task paths and this plan on the existing feature branch.

### Task 2: Save account-label code
**Files:** Plugin worktree `src/herdr.rs` only. Existing `.git-quota-evidence-path` remains untracked.
**Interfaces:** Decorate the final Pi identity token from its original session path; do not change account routing, auth, provider attribution or quota values.
- [ ] Review the display-only diff and its three regression tests.
- [ ] Run cargo +1.95.0 fmt --check, test, clippy --release --all-targets -- -D warnings. Expected: 829 passing tests, zero warnings/errors.
- [ ] Commit only src/herdr.rs on fix/pi-own-auth-quota.

### Task 3: Validate and push
- [ ] Read-only review of both staged changes; preserve unrelated files.
- [ ] Re-confirm the explicit push URLs, target branches, and absence of secrets.
- [ ] Push dotfiles feature branch to origin and plugin feature branch to private using ordinary pushes.
- [ ] Compare each local HEAD to the actual remote branch SHA and report the two branch links. Do not claim a merge or full environment replication.
