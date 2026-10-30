// Resolve PRs using GitHub metadata, never artifacts or code from a PR.
module.exports = async function findPullRequests({github, context}) {
  const repository = context.payload.repository;
  if (context.ref !== `refs/heads/${repository.default_branch}`) {
    throw new Error('Labeling must run from the default branch');
  }

  let candidates;
  let headSha;
  if (context.eventName === 'workflow_dispatch') {
    const input = context.payload.inputs?.['pull-request'];
    if (!/^[1-9][0-9]*$/.test(input ?? '') ||
        !Number.isSafeInteger(Number(input))) {
      throw new Error('Expected a positive integer PR number');
    }
    const {data: pr} = await github.rest.pulls.get({
      ...context.repo,
      pull_number: Number(input),
    });
    candidates = [pr];
  } else {
    const run = context.payload.workflow_run;
    if (context.eventName !== 'workflow_run' ||
        run?.event !== 'pull_request' ||
        run.conclusion !== 'success' ||
        run.path !== '.github/workflows/pr-labels.yml' ||
        run.repository?.id !== repository.id ||
        !/^[0-9a-f]{40}$/.test(run.head_sha ?? '')) {
      throw new Error('Unexpected labeling signal');
    }
    headSha = run.head_sha;

    // workflow_run.pull_requests can be empty for forks. Query the base
    // repository instead and match the current head SHA. This also ignores
    // delayed runs after a force-push, without trusting a supplied PR number.
    candidates = await github.paginate(github.rest.pulls.list, {
      ...context.repo,
      state: 'open',
      per_page: 100,
    });
  }

  return candidates.filter(pr =>
    Number.isSafeInteger(pr.number) && pr.number > 0 &&
    pr.base?.repo?.id === repository.id &&
    (pr.state === 'open' || pr.merged_at) &&
    (!headSha || pr.head?.sha === headSha)
  ).map(pr => pr.number);
};
