# Release notes and PR labels

The **Release Preview** workflow generates draft release notes using
`.github/release-drafter.yml`. Its categories use the labels on merged PRs.
Run it manually as before to create a release branch and optionally announce
the preview.

The **Pull Request Tools** workflow restores the file-based labeling previously
disabled in #1996 and removed in #1999, without a `pull_request_target` trigger.
It applies `.github/labeler.json` and removes labels from that configuration when
their file patterns no longer match. Each rule lists exact file paths or
`directory/**` prefixes, which also match dotfiles; other glob syntax is rejected.
The updater adds missing matching labels and removes individual stale managed
labels through GitHub's API. It never replaces the entire label list, so
concurrent additions or removals of unrelated labels are preserved.
Maintainers can apply other category labels, such as `feat` and `fix`, manually.
Labels listed in the configuration remain owned by the automation even when
applied manually. Concurrent edits to those same managed labels are not atomic;
the next run reconciles them against the file rules.

## Trust boundary

1. **Pull Request Label Signal** runs on PR opens, edits, updates, reopens, and
   transitions out of draft. It has no token permissions and does not check out
   code, use secrets, or produce artifacts.
2. **Pull Request Tools** runs after that signal succeeds, using the workflow
   definition and code from the default branch. Only this job can write PR
   labels; it has no release or other contents write permission.
3. The job checks out the default-branch commit (`github.sha`), with persisted
   credentials disabled. It never checks out the triggering run's `head_sha`.
   The checkout and GitHub Script actions are pinned to full commit hashes.
4. The resolver queries the base repository's open PRs through GitHub's API and
   matches the signal's head SHA to their current heads. This works for forks
   even when `workflow_run.pull_requests` is empty, and skips superseded runs.
   PR code, artifacts, caches, titles, and bodies are never executed or used as
   scripts. The updater reads file paths from the API and trusted configuration,
   and rechecks the PR's head and base before writing labels. A successful signal
   is a notification, not an assertion that its code is trusted.

Both workflows must be merged into the default branch before automatic labeling
works. A fork PR may still need the normal GitHub Actions approval before its
signal runs. Unmerged changes to the labeling rules do not affect live labeling.
Keep all executable code and label configuration in the privileged job on the
default-branch commit; do not add PR checkouts, artifact downloads, or cache
restores to it. See GitHub's
[workflow security guidance](https://docs.github.com/en/actions/reference/security/secure-use).

## Backfill and validation

To label an existing open or merged PR, run **Pull Request Tools** from the
default branch and enter its number. Closed, unmerged PRs are skipped. This can
also recover a missed signal or label a PR merged before automatic labeling
finished. Then rerun **Release Preview** to refresh the draft notes.

Run the resolver and incremental updater tests locally with:

```sh
node --test .github/scripts/tests/*.test.cjs
```

They also run in the main CI workflow. After merging, verify a fork PR that
changes `docs/` receives `documentation`, and one that changes `.github/`
receives `ci`. Revert those changes and check that the corresponding labels
are removed while unrelated labels remain. These integration checks require
GitHub Actions; local tests use mocked API responses and do not write labels.
