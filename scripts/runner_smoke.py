"""Verify the provider's expected revision against the runner's checkout."""
import argparse
import json
import os
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=["github", "gitlab"])
    provider = parser.parse_args().provider
    if sys.version_info < (3, 12):
        parser.exit(1, "Python 3.12 or newer is required\n")

    sha_variable, run_variable = {
        "github": ("GITHUB_SHA", "GITHUB_RUN_ID"),
        "gitlab": ("CI_COMMIT_SHA", "CI_PIPELINE_ID"),
    }[provider]
    expected = os.environ.get(sha_variable, "")
    run_id = os.environ.get(run_variable, "")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", expected):
        parser.exit(1, f"Missing or invalid {sha_variable}\n")
    if not re.fullmatch(r"[1-9][0-9]*", run_id):
        parser.exit(1, f"Missing or invalid {run_variable}\n")

    head = subprocess.check_output(
        ["git", "rev-parse", "--verify", "HEAD^{commit}"], text=True
    ).strip()
    if head != expected:
        parser.exit(1, "Checked-out commit differs from the provider revision\n")
    print(json.dumps({"provider": provider, "run_id": run_id, "commit": head}))


if __name__ == "__main__":
    main()
