const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const {parseDocument} = require('yaml');
const findPullRequests = require('./pr-labels.cjs');

// Keep rules declarative. Support exact file paths and
// directory/** prefixes (including dotfiles); reject other glob syntax.
function compileRules(config) {
  if (!config || typeof config !== 'object' || Array.isArray(config) ||
      Object.keys(config).length === 0) {
    throw new Error('Expected a nonempty label configuration');
  }
  return Object.entries(config).map(([label, entries]) => {
    if (!label.trim() || !Array.isArray(entries) || !entries.length) {
      throw new Error('Each label must have at least one file pattern');
    }
    const patterns = entries.flatMap(entry => {
      if (typeof entry === 'string') return [entry];
      if (entry && typeof entry === 'object' &&
          Object.keys(entry).length === 1 &&
          Array.isArray(entry.any) && entry.any.length) return entry.any;
      throw new Error('Expected a file pattern or a nonempty any list');
    });
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

function parseRules(source) {
  // The core schema reads data only; unknown tags and duplicate keys fail
  // validation rather than silently changing which labels we manage.
  const document = parseDocument(source, {schema: 'core', uniqueKeys: true});
  const problems = [...document.errors, ...document.warnings];
  if (problems.length) throw new Error(`Invalid label YAML: ${problems[0].message}`);
  return compileRules(document.toJS({maxAliasCount: 50}));
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
  const rules = parseRules(readFileSync(
    join(__dirname, '..', 'labeler.yml'), 'utf8'
  ));

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

module.exports = {syncPullRequestLabels, compileRules, parseRules};
