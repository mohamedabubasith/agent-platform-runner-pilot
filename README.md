# Agent platform runner pilot

This repository contains the first transport smoke test for a ticket-driven coding platform. A manually started CI job checks the Git revision that its provider scheduled, then writes the provider, run ID and exact commit to the job log. It exercises runner allocation, checkout and the Python entry point. It uses only this pilot repository. The application coordinator and ticket processing are future milestones.

## GitHub Actions

Place the files on the default branch of a private pilot repository with Actions and Linux hosted runners enabled. Select **Actions → Runner smoke → Run workflow** on that branch. A green job includes a JSON line with the same commit as the workflow run. The workflow uses a read-only repository token, removes checkout credentials, and exits after five minutes at the latest (subject to provider cancellation).

## GitLab CI

Place the files on the default branch of a private GitLab project with an available Linux runner using a Docker or Kubernetes executor. Select **Build → Pipelines → New pipeline** on the default branch. The runner pulls the pinned Python image, checks out the pipeline commit and prints the same JSON fields. A project configured with a shell executor needs Python 3.12+ and Git on its host and does not use the pinned image. Protected default branch configuration and access to trigger tokens belong to the project owner.

## Reproduce the runner check locally

Use a Git checkout, Git and Python 3.12+. If starting from the source ZIP, unzip the project, enter its directory, run `git init -b main`, stage the files and make an initial commit first.

```sh
pilot_sha=$(git rev-parse HEAD)
GITHUB_SHA="$pilot_sha" GITHUB_RUN_ID=1 python3 -I scripts/runner_smoke.py github
CI_COMMIT_SHA="$pilot_sha" CI_PIPELINE_ID=2 python3 -I scripts/runner_smoke.py gitlab
```

Change the expected SHA to forty zeroes and repeat either command to check rejection. The script exits with status 1 on a mismatch. See [the runner-first decision record](docs/runner-first.md) for what must be proven before agent jobs are enabled.
