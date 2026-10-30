const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const findPullRequests = require('./pr-labels.cjs');

// Keep rules declarative and dependency-free. Support exact file paths and
// directory/** prefixes (including dotfiles); reject other glob syntax.
function compileRules(config) {
  if (!config || typeof config !== 'object' || Array.isArray(config) ||
      Object.keys(config).length === 0) {
    throw new Error('Expected a nonempty label configuration');
  }
  return Object.entries(config).map(([label, patterns]) => {
    if (!label.trim() || !Array.isArray(patterns) || !patterns.length) {
      throw new Error('Each label must have at least one file pattern');
    }
    const matchers = patterns.map(pattern => {
      if (typeof pattern !== 'string' || !pattern) {
        throw new Error('Expected a nonempty file pattern');
      }
      const directory = pattern.endsWith('/**');
      const literal = directory ? pattern.slice(0, -3) : pattern;
      if (!literal || /[\\*?\[\]{}()!]/.test(literal) ||
          literal.split('/').some(part => !part || part === '.' || part === '..')) {
        throw new Error(`Unsupported file pattern: ${pattern}`);
      }
      return filename => directory
        ? filename.startsWith(`${literal}/`)
        : filename === literal;
    });
    return {label, matches: filename => matchers.some(match => match(filename))};
  });
}

function isEligible(pr, context) {
  return pr.base?.repo?.id === context.payload.repository.id &&
    (pr.state === 'open' ||
     (context.eventName === 'workflow_dispatch' && Boolean(pr.merged_at))) &&
    (context.eventName === 'workflow_dispatch' ||
     pr.head?.sha === context.payload.workflow_run.head_sha);
}

async function syncPullRequestLabels({github, context, core}) {
  // The resolver validates the trigger and default branch before any writes.
  const numbers = await findPullRequests({github, context});
  const rules = compileRules(JSON.parse(readFileSync(
    join(__dirname, '..', 'labeler.json'), 'utf8'
  )));

  for (const number of numbers) {
    const pull = {...context.repo, pull_number: number};
    const issue = {...context.repo, issue_number: number};
    const {data: snapshot} = await github.rest.pulls.get(pull);
    if (!isEligible(snapshot, context)) continue;

    const files = await github.paginate(github.rest.pulls.listFiles, {
      ...pull, per_page: 100,
    });
    // GitHub caps the files endpoint at 3,000 entries. An incomplete diff
    // must not cause us to remove labels for files we could not inspect.
    if (files.length !== snapshot.changed_files) {
      throw new Error(`Incomplete file list for PR #${number}; leaving labels unchanged`);
    }
    const labels = await github.paginate(github.rest.issues.listLabelsOnIssue, {
      ...issue, per_page: 100,
    });
    const existing = new Set(labels.map(label => label.name));
    const wanted = new Set(rules.filter(rule =>
      files.some(file => rule.matches(file.filename))
    ).map(rule => rule.label));

    // Metadata and file reads are not atomic. Skip if the PR moved while we
    // were computing the changes; a later signal can reconcile its labels.
    const {data: current} = await github.rest.pulls.get(pull);
    if (!isEligible(current, context) ||
        current.head.sha !== snapshot.head.sha ||
        current.base.sha !== snapshot.base.sha) {
      core.info(`Skipping PR #${number}: changed during label calculation`);
      continue;
    }

    const additions = [...wanted].filter(label => !existing.has(label));
    if (additions.length) {
      await github.rest.issues.addLabels({...issue, labels: additions});
    }
    for (const {label} of rules) {
      if (!existing.has(label) || wanted.has(label)) continue;
      try {
        await github.rest.issues.removeLabel({...issue, name: label});
      } catch (error) {
        if (error.status !== 404) throw error;
        // Another actor may have removed this label first. Confirm absence
        // through the API so an unrelated 404 is not silently swallowed.
        const latest = await github.paginate(
          github.rest.issues.listLabelsOnIssue, {...issue, per_page: 100}
        );
        if (latest.some(item => item.name === label)) throw error;
      }
    }
    core.info(`Reconciled managed labels on PR #${number}`);
  }
}

module.exports = {syncPullRequestLabels, compileRules};
