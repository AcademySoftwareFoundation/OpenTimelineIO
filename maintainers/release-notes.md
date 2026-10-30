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
`changed-files` syntax. Maintainers can apply other category labels, such as
`feat` and `fix`, manually.

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
