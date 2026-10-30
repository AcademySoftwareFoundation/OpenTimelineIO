const assert = require('node:assert/strict');
const {test} = require('node:test');
const findPullRequests = require('../pr-labels.cjs');

const headSha = 'a'.repeat(40);

function fixture({eventName = 'workflow_run', candidates = []} = {}) {
  const calls = [];
  const context = {
    eventName,
    ref: 'refs/heads/main',
    repo: {owner: 'AcademySoftwareFoundation', repo: 'OpenTimelineIO'},
    payload: {
      repository: {id: 123, default_branch: 'main'},
      inputs: {'pull-request': '42'},
      workflow_run: {
        event: 'pull_request',
        conclusion: 'success',
        path: '.github/workflows/pr-labels.yml',
        repository: {id: 123},
        head_sha: headSha,
        pull_requests: [],
      },
    },
  };
  const github = {
    rest: {pulls: {
      list: Symbol('pulls.list'),
      get: async args => {
        calls.push(args);
        return {data: candidates[0]};
      },
    }},
    paginate: async (method, args) => {
      assert.equal(method, github.rest.pulls.list);
      calls.push(args);
      return candidates;
    },
  };
  return {github, context, calls};
}

function pullRequest(overrides = {}) {
  return {
    number: 42,
    state: 'open',
    merged_at: null,
    base: {repo: {id: 123}},
    head: {sha: headSha, repo: {id: 456}},
    ...overrides,
  };
}

test('finds fork PRs even when the event contains no PR association', async () => {
  const f = fixture({candidates: [pullRequest()]});
  assert.deepEqual(await findPullRequests(f), [42]);
  assert.deepEqual(f.calls, [{...f.context.repo, state: 'open', per_page: 100}]);
});

test('labels every matching PR returned by pagination', async () => {
  const f = fixture({candidates: [pullRequest(), pullRequest({number: 43})]});
  assert.deepEqual(await findPullRequests(f), [42, 43]);
});

test('skips stale, foreign, closed, and invalid PRs', async () => {
  const f = fixture({candidates: [
    pullRequest({head: {sha: 'b'.repeat(40)}}),
    pullRequest({base: {repo: {id: 999}}}),
    pullRequest({state: 'closed'}),
    pullRequest({number: '42\n43'}),
    pullRequest({number: -1}),
  ]});
  assert.deepEqual(await findPullRequests(f), []);
});

test('does not use PR numbers supplied by the triggering workflow', async () => {
  const f = fixture();
  f.context.payload.workflow_run.pull_requests = [{number: 999}];
  assert.deepEqual(await findPullRequests(f), []);
});

test('rejects unexpected triggers before contacting GitHub', async t => {
  for (const [key, value] of Object.entries({
    event: 'push',
    conclusion: 'failure',
    path: '.github/workflows/untrusted.yml',
    repository: {id: 999},
    head_sha: '$(touch /tmp/unsafe)',
  })) {
    await t.test(key, async () => {
      const f = fixture();
      f.context.payload.workflow_run[key] = value;
      await assert.rejects(findPullRequests(f), /Unexpected labeling signal/);
      assert.deepEqual(f.calls, []);
    });
  }
  const f = fixture({eventName: 'pull_request'});
  await assert.rejects(findPullRequests(f), /Unexpected labeling signal/);
  assert.deepEqual(f.calls, []);
});

test('manual dispatch supports both open and merged PRs', async () => {
  for (const pr of [pullRequest(), pullRequest({
    state: 'closed', merged_at: '2026-10-01T00:00:00Z',
  })]) {
    const f = fixture({eventName: 'workflow_dispatch', candidates: [pr]});
    assert.deepEqual(await findPullRequests(f), [42]);
    assert.deepEqual(f.calls, [{...f.context.repo, pull_number: 42}]);
  }
});

test('manual dispatch rejects malformed numbers before contacting GitHub', async () => {
  for (const value of ['', '0', '-1', '42\n43', '42; echo unsafe', '1.5',
    '9007199254740992', undefined]) {
    const f = fixture({eventName: 'workflow_dispatch'});
    f.context.payload.inputs['pull-request'] = value;
    await assert.rejects(findPullRequests(f), /positive integer/);
    assert.deepEqual(f.calls, []);
  }
});

test('manual dispatch skips closed unmerged and foreign PRs', async () => {
  for (const pr of [pullRequest({state: 'closed'}),
    pullRequest({base: {repo: {id: 999}}})]) {
    const f = fixture({eventName: 'workflow_dispatch', candidates: [pr]});
    assert.deepEqual(await findPullRequests(f), []);
  }
});

test('refuses to run code from a non-default branch', async () => {
  for (const eventName of ['workflow_run', 'workflow_dispatch']) {
    const f = fixture({eventName});
    f.context.ref = 'refs/heads/untrusted';
    await assert.rejects(findPullRequests(f), /default branch/);
    assert.deepEqual(f.calls, []);
  }
});

test('API failures fail the workflow', async () => {
  const f = fixture();
  f.github.paginate = async () => { throw new Error('API unavailable'); };
  await assert.rejects(findPullRequests(f), /API unavailable/);
});
