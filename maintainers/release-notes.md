# Release notes and PR labels

**Release Preview** continues to generate draft release notes using
`.github/release-drafter.yml`. Its categories use the labels on merged PRs.
Run it manually as before to create a release branch and optionally announce
the preview.

**Pull Request Tools** restores the file-based labeling introduced in
[#1689](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/pull/1689),
disabled in [#1996](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/pull/1996),
and removed in [#1999](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/pull/1999).
It uses GitHub's `actions/labeler` and `.github/labeler.yml` with the modern
`changed-files` syntax. All automatically managed labels already exist in the
repository and are mapped to Release Drafter sections:

| Labels | Automatic matching | Release section |
| --- | --- | --- |
| `documentation` | Docs, Doxygen, Markdown, and reStructuredText files | Documentation |
| `ci`, `github_actions` | CI configuration and GitHub Actions workflows, scripts, and configuration | Maintenance |
| `build`, `cmake` | Build, packaging, and CMake files | Maintenance |
| `wheels` | Python packaging files and wheel/publishing workflows | Maintenance |
| `dependencies`, `submodules` | Dependency declarations, requirements, and submodules | Maintenance |
| `maintenance` | Maintainer tools or changes entirely within `tests/` | Maintenance |
| `python`, `python-bindings` | Python files and Python package/binding sources | Python & Bindings |
| `opentime`, `time calculations` | OpenTime sources, bindings, and tests | Time |
| `color` | Color implementation, Python wrapper, and tests | Color |

The existing `enhancement` label also maps to Features. Intent and triage labels
such as `bug`, `enhancement`, `security`, `good first issue`, and `WIP` stay manual:
file paths alone cannot reliably determine them. The external `Adapters`,
`AAF`, `otioview`, and `PySide6` labels have no dedicated source paths in this
repository and are not automatically managed.

Release Drafter v7.1.1 can list a PR in multiple matching sections, for example
Bug Fixes and Python & Bindings. Component labels do not imply that a change is
a feature or a bug fix. The inactive Release Drafter `autolabeler` block is removed;
`.github/labeler.yml` is the single source for automatic rules.

## Security boundary

- **Pull Request Label Signal** runs on PR updates with `permissions: {}`. It
  checks out no code, uses no secrets, and produces no artifacts or caches.
- **Pull Request Tools** runs from the default branch after the signal succeeds.
  It validates the event, workflow path, and repository. Its only token
  permissions are `contents: read` and `pull-requests: write`.
- A short inline API lookup finds current PR heads in the base repository.
  It handles fork runs with empty PR associations and skips superseded heads.
  PRs over GitHub's 3,000-file API limit are skipped to avoid incomplete matches.
- The job performs no checkout or package install and consumes no artifacts or
  caches. GitHub Script fetches only the YAML configuration from `github.sha`,
  the trusted default-branch commit, into a runner temporary file. This avoids
  the pinned labeler's remote configuration-path encoding bug. File paths are
  read through GitHub's API, never executed.
- Both actions are pinned to full commit hashes. The labeler pin deliberately
  includes [the incremental-update fix in #957](https://github.com/actions/labeler/pull/957),
  which is newer than the `v7.0.0` release. Keep that fix when updating the pin.
  It adds matching labels and removes only stale configured labels, preserving
  concurrent edits to unrelated labels. Configured labels remain owned by the
  automation, including when applied manually; edits to those same labels are
  not transactional.

`workflow_run` is privileged, so a successful signal is not evidence that PR
code is trusted. Do not add PR checkouts, artifact execution, or cache restores
to the privileged job. See GitHub's
[secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).

## Backfill and rollout

Run **Pull Request Tools** from the default branch with a PR number to label an
existing open or merged PR. Closed, unmerged PRs are skipped. Then rerun
**Release Preview** to refresh the draft notes.

Both workflows must exist on the default branch before automatic labeling works.
A fork PR may still need normal GitHub Actions approval before its signal runs.
After merging, verify that a fork PR changing `docs/` receives `documentation`,
then loses that label when the change is reverted, while unrelated labels remain.
