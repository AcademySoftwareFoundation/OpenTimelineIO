const assert = require('node:assert/strict');
const {test} = require('node:test');
const {syncPullRequestLabels, compileRules} = require('../sync-pr-labels.cjs');
const config = require('../../labeler.json');

function fixture({filenames = ['docs/guide.md'], labels = ['ci', 'bug']} = {}) {
  const pr = {
    number: 42,
    state: 'open',
    merged_at: null,
    changed_files: filenames.length,
    head: {sha: 'a'.repeat(40), repo: {id: 456}},
    base: {sha: 'b'.repeat(40), repo: {id: 123}},
  };
  const context = {
    eventName: 'workflow_run',
    ref: 'refs/heads/main',
    repo: {owner: 'AcademySoftwareFoundation', repo: 'OpenTimelineIO'},
    payload: {
      repository: {id: 123, default_branch: 'main'},
      workflow_run: {
        event: 'pull_request', conclusion: 'success',
        path: '.github/workflows/pr-labels.yml', repository: {id: 123},
        head_sha: pr.head.sha, pull_requests: [],
      },
      inputs: {'pull-request': '42'},
    },
  };
  const f = {
    pr, context, labels: new Set(labels), writes: [], reads: [], messages: [],
    beforeWrite: () => {},
    afterLabelRead: () => {},
    beforeGet: () => {},
    getCount: 0,
  };
  const issues = {
    listLabelsOnIssue: Symbol('listLabelsOnIssue'),
    addLabels: async args => {
      f.beforeWrite(args);
      f.writes.push({add: args});
      args.labels.forEach(label => f.labels.add(label));
    },
    removeLabel: async args => {
      f.beforeWrite(args);
      f.writes.push({remove: args});
      if (!f.labels.delete(args.name)) {
        throw Object.assign(new Error('Label not found'), {status: 404});
      }
    },
    setLabels: () => assert.fail('Must never replace the label list'),
    removeAllLabels: () => assert.fail('Must never remove all labels'),
  };
  const pulls = {
    list: Symbol('list'),
    listFiles: Symbol('listFiles'),
    get: async () => {
      f.beforeGet(++f.getCount);
      return {data: structuredClone(pr)};
    },
  };
  const github = {
    rest: {issues, pulls},
    paginate: async (method, args) => {
      f.reads.push({method, args});
      if (method === pulls.list) return [structuredClone(pr)];
      if (method === pulls.listFiles) return filenames.map(filename => ({filename}));
      if (method === issues.listLabelsOnIssue) {
        const result = [...f.labels].map(name => ({name}));
        f.afterLabelRead();
        return result;
      }
      assert.fail('Unexpected API read');
    },
  };
  f.github = github;
  f.core = {info: message => f.messages.push(message)};
  return f;
}

test('adds and removes only managed labels with incremental API calls', async () => {
  const f = fixture();
  await syncPullRequestLabels(f);
  assert.deepEqual([...f.labels].sort(), ['bug', 'documentation']);
  assert.deepEqual(f.writes, [
    {add: {...f.context.repo, issue_number: 42, labels: ['documentation']}},
    {remove: {...f.context.repo, issue_number: 42, name: 'ci'}},
  ]);
});

test('preserves concurrent additions and removals of unrelated labels', async () => {
  const f = fixture();
  f.afterLabelRead = () => {
    f.labels.add('reviewed');
    f.labels.delete('bug');
  };
  await syncPullRequestLabels(f);
  assert.deepEqual([...f.labels].sort(), ['documentation', 'reviewed']);
});

test('tolerates another run removing a stale managed label first', async () => {
  const f = fixture();
  f.beforeWrite = args => {
    if (args.name === 'ci') f.labels.delete('ci');
  };
  await syncPullRequestLabels(f);
  assert.deepEqual([...f.labels].sort(), ['bug', 'documentation']);
  assert.equal(f.reads.filter(r =>
    r.method === f.github.rest.issues.listLabelsOnIssue
  ).length, 2);
});

test('does not swallow a 404 when the label is still present', async () => {
  const f = fixture();
  f.github.rest.issues.removeLabel = async () => {
    throw Object.assign(new Error('API failure'), {status: 404});
  };
  await assert.rejects(syncPullRequestLabels(f), /API failure/);
});

test('propagates add and remove API failures', async () => {
  for (const method of ['addLabels', 'removeLabel']) {
    const f = fixture();
    f.github.rest.issues[method] = async () => {
      throw Object.assign(new Error('API unavailable'), {status: 503});
    };
    await assert.rejects(syncPullRequestLabels(f), /API unavailable/);
  }
});

test('makes no writes when labels already match and remains idempotent', async () => {
  const f = fixture();
  await syncPullRequestLabels(f);
  f.writes.length = 0;
  await syncPullRequestLabels(f);
  assert.deepEqual(f.writes, []);
});

test('uses pagination for files and labels', async () => {
  const f = fixture({
    filenames: [...Array.from({length: 100}, (_, i) => `examples/${i}`),
      'docs/guide.md'],
  });
  await syncPullRequestLabels(f);
  assert(f.labels.has('documentation'));
  for (const method of [f.github.rest.pulls.listFiles,
    f.github.rest.issues.listLabelsOnIssue]) {
    assert.equal(f.reads.find(r => r.method === method).args.per_page, 100);
  }
});

test('leaves labels unchanged when GitHub returns an incomplete diff', async () => {
  const f = fixture();
  f.pr.changed_files = 3001;
  await assert.rejects(syncPullRequestLabels(f), /Incomplete file list/);
  assert.deepEqual(f.writes, []);
});

test('skips a PR if its head, base, or eligibility changes before writing', async () => {
  for (const change of [
    pr => { pr.head.sha = 'c'.repeat(40); },
    pr => { pr.base.sha = 'c'.repeat(40); },
    pr => { pr.state = 'closed'; },
    pr => { pr.base.repo.id = 999; },
  ]) {
    const f = fixture();
    f.beforeGet = count => { if (count === 2) change(f.pr); };
    await syncPullRequestLabels(f);
    assert.deepEqual(f.writes, []);
  }
});

test('skips a PR superseded immediately after resolution', async () => {
  const f = fixture();
  f.beforeGet = () => { f.pr.head.sha = 'c'.repeat(40); };
  await syncPullRequestLabels(f);
  assert.deepEqual(f.writes, []);
  assert(!f.reads.some(r => r.method === f.github.rest.pulls.listFiles));
});

test('rejects untrusted triggers before reaching mutation APIs', async () => {
  for (const change of [
    c => { c.ref = 'refs/heads/attacker'; },
    c => { c.eventName = 'pull_request'; },
    c => { c.payload.workflow_run.path = '.github/workflows/attacker.yml'; },
  ]) {
    const f = fixture();
    change(f.context);
    await assert.rejects(syncPullRequestLabels(f));
    assert.deepEqual(f.reads, []);
    assert.deepEqual(f.writes, []);
  }
});

test('manual dispatch still labels merged PRs', async () => {
  const f = fixture();
  f.context.eventName = 'workflow_dispatch';
  f.pr.state = 'closed';
  f.pr.merged_at = '2026-10-01T00:00:00Z';
  await syncPullRequestLabels(f);
  assert(f.labels.has('documentation'));
});

test('file names including shell syntax remain data', async () => {
  const f = fixture({filenames: ['docs/$(touch pwned);.md']});
  await syncPullRequestLabels(f);
  assert(f.labels.has('documentation'));
  assert.deepEqual(f.writes[0].add.labels, ['documentation']);
});

test('all existing file rules retain their matches, including dotfiles', () => {
  const rules = compileRules(config);
  const cases = {
    'CHANGELOG.md': ['release-candidate'],
    'src/deps/pybind11': ['submodules'],
    'pyproject.toml': ['dependencies'],
    '.github/workflows/pr-tools.yml': ['ci'],
    'docs/.hidden/file': ['documentation'],
    'src/opentime/timeRange.cpp': ['opentime', 'time calculations'],
    'src/py-opentimelineio/opentimelineio/__init__.py': ['python-bindings'],
    'docs-other/file': [],
    'subdir/pyproject.toml': [],
    'README.md': [],
  };
  for (const [filename, expected] of Object.entries(cases)) {
    assert.deepEqual(rules.filter(r => r.matches(filename)).map(r => r.label),
      expected, filename);
  }
  const [rule] = compileRules({docs: ['docs/**', 'README.md']});
  assert(rule.matches('README.md'));
  assert(rule.matches('docs/guide.md'));
});

test('rejects invalid configurations instead of treating them as no matches', () => {
  for (const invalid of [null, [], {}, {docs: []}, {docs: [null]},
    {docs: ['']}, {'': ['docs/**']}, {docs: ['docs/*.md']},
    {docs: ['../docs/**']}, {docs: ['/docs/**']}, {docs: ['docs//**']},
    {docs: ['**']}]) {
    assert.throws(() => compileRules(invalid));
  }
});
