#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""
This script downloads an artifact from a GitHub Action workflow run,
unzips and and stores the files in a directory of your choice.

Use cases:
* You want to locally test or inspect the generated artifact.
* You want to upload the artifact to a remote repository (test.pypi.org for example)
  before a release.
"""
import io
import os
import sys
import json
import time
import zipfile
import argparse

import urllib.request

parser = argparse.ArgumentParser(
    description="Download an artifact from a GitHub Action workflow run."
)
parser.add_argument("sha", help="Commit hash")
parser.add_argument("token", help="GitHub Personal Access Token.")
parser.add_argument(
    "-w",
    "--workflow",
    default="OpenTimelineIO",
    help="Name of the workflow to download artifact from.",
)
parser.add_argument(
    "-a", "--artifact", default="wheels", help="Artifact name to download."
)
parser.add_argument(
    "-d", "--directory", default="dist", help="Directory where to write the artifact."
)

args = parser.parse_args()

headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {args.token}",
}

if os.path.exists(args.directory) and os.listdir(args.directory):
    sys.stderr.write(
        f"{args.directory!r} directory contains files. It should be empty."
    )
    sys.exit(1)

if not os.path.exists(args.directory):
    os.makedirs(args.directory)

request = urllib.request.Request(
    "https://api.github.com/repos/AcademySoftwareFoundation/OpenTimelineIO/actions/runs?status=success",  # noqa: E501
    headers=headers,
)
response = urllib.request.urlopen(request).read()
workflow_runs = json.loads(response)["workflow_runs"]
for run in workflow_runs:
    if run["head_sha"] == args.sha and run["name"] == args.workflow:
        workflow_run = run
        break
else:
    sys.stderr.write(
        "No run for a workflow named {!r} found for commit {!r}.".format(
            args.workflow, args.sha
        )
    )
    sys.exit(1)


print("Found workflow:")
print("  Name:       {}".format(workflow_run["name"]))
print("  Branch:     {}".format(workflow_run["head_branch"]))
print("  Commit:     {}".format(workflow_run["head_sha"]))
print("  Committer:  {}".format(workflow_run["head_commit"]["committer"]))
print("  Run Number: {}".format(workflow_run["run_number"]))
print("  Status:     {}".format(workflow_run["status"]))
print("  Conclusion: {}".format(workflow_run["conclusion"]))
print("  URL:        {}".format(workflow_run["html_url"]))


print("Getting list of artifacts")
request = urllib.request.Request(workflow_run["artifacts_url"], headers=headers)
response = urllib.request.urlopen(request).read()
artifacts = json.loads(response)["artifacts"]
for artifact in artifacts:
    if artifact["name"] == args.artifact:
        artifact_download_url = artifact["archive_download_url"]
        break
else:
    sys.stderr.write(f"No artifact named {args.artifact!r} found.")
    sys.exit(1)

print(
    "Downloading {!r} artifact and unzipping to {!r}".format(
        args.artifact, args.directory
    )
)

request = urllib.request.Request(artifact_download_url, headers=headers)
file_content = urllib.request.urlopen(request).read()

zip_file = zipfile.ZipFile(io.BytesIO(file_content))
for zip_info in zip_file.infolist():
    output_path = os.path.join(args.directory, zip_info.filename)

    print(f"Writing {zip_info.filename!r} to {output_path!r}")
    with open(output_path, "wb") as fd:
        fd.write(zip_file.open(zip_info).read())

    # Keep the timestamp!
    date_time = time.mktime(zip_info.date_time + (0, 0, -1))
    os.utime(output_path, (date_time, date_time))
