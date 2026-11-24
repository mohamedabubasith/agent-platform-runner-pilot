# ADR 001 — Start with runner transport

**Status** Pilot selected on 24 November 2026. The remaining platform design is proposed.

**Decision** Use one private repository for trusted workflow definitions. Exercise GitHub Actions first and GitLab CI with the same Python entry point. Each smoke job runs on demand, reads only the pilot checkout and verifies the provider-supplied commit. This first checkpoint needs neither an inference account nor a running coordinator. The smoke job never runs code from tickets or target projects.

**Next checkpoint** Develop the coordinator locally using SQLite WAL on local disk, starting with an opt-in ticket, a versioned plan and a fake runner. Persist plan digest, ticket revision, base commit and authorized human approval transactionally. Test redelivery, stale approvals, cancellation and lease recovery. After these pass, connect one GitHub dispatch and one GitLab trigger to authenticated job claims. A live coordinator will require a provider-reachable HTTPS endpoint. Its hosting is a separate decision.

**Trust boundary** The coordinator supplies a job ID. A CI job exchanges provider-issued OIDC for a short-lived claim. Verify issuer, audience, expiry, project/repository ID and trusted ref, bind to an expected execution, and deduplicate claims/results. The coordinator authorizes each write stage and rechecks approval and base before publishing. Approval waits release the runner. Keep Git write credentials in a separate publisher. Validate provider-specific claims for the chosen GitLab version and GitHub workflow before enabling callbacks.

**Execution limits** Initial target is one job at a time. Each smoke job has a five-minute timeout. Its network dependencies are Git checkout and, for container executors, image pull. Future model jobs require approved inference egress, isolated workspaces, credential separation and an independently tested sandbox. A CLI permission flag or passing smoke test alone cannot establish isolation. GitHub's ubuntu-24.04 runner label receives image updates. GitLab requires a runner matching the project's executor and access rules. Verify provider minutes, branch protection and required human merge review on the selected projects before processing real tickets.

## Dependency checks on Linux x86-64

| Component | Evidence |
| --- | --- |
| Python 3.12.14, SQLite 3.53.1 | Enabled WAL on a temporary database, created an FTS5 table, committed a row, reopened the file and retrieved the row with MATCH. |
| Codex CLI 0.172.0 | Ran the pinned npm binary. Help lists noninteractive exec, stdin, JSON events, output schema, read-only/workspace-write sandbox modes and API key login. Package declares Apache-2.0. |
| Claude Code 2.1.331 | Ran the pinned native Linux binary. Help lists print mode, JSON output/schema, permission modes and tool selection. npm refers to its own license terms. Proposed unattended auth is an organization-managed Anthropic API key. Confirm organization terms and data handling before model use. |
| CI configurations | GitHub workflow passes actionlint 1.7.7. GitLab YAML passes the GitLab 18.5.0 editor JSON schema. Provider-side rules, image/runner availability, branch permissions and billable execution require live runs. |
| CLI behavior | Version and help probes only. Real authentication, model output, schema enforcement, sandbox restrictions, usage accounting and cancellation remain to be exercised on disposable jobs. |

## Reproduce the CLI probes

In a disposable directory on Linux x86-64 with Node 22+ and npm, run the following. Installation runs the vendor packaging scripts. Version and help probes require no model credentials.

```sh
npm install --save-exact @openai/codex@0.172.0 @anthropic-ai/claude-code@2.1.331
./node_modules/.bin/codex --version
./node_modules/.bin/codex exec --help
./node_modules/.bin/claude --version
./node_modules/.bin/claude --help
```

The [pilot README](../README.md) contains the two smoke-test entry points.

## Provider references

- [GitHub workflow dispatch](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch)
- [GitHub OpenID Connect](https://docs.github.com/en/actions/reference/security/oidc)
- [GitLab pipeline triggers](https://docs.gitlab.com/api/pipeline_triggers/)
- [GitLab CI ID tokens](https://docs.gitlab.com/ci/secrets/id_token_authentication/)
