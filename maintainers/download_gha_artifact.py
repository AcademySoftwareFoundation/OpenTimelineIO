#!/usr/bin/env python3
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
    "Authorization": "token {args.token}".format(args=args),
}

if os.path.exists(args.directory) and os.listdir(args.directory):
    sys.stderr.write(
        "{0!r} directory contains files. It should be empty.".format(args.directory)
    )
    sys.exit(1)

if not os.path.exists(args.directory):
    os.makedirs(args.directory)

request = urllib.request.Request(
    "https://api.github.com/repos/PixarAnimationStudios/OpenTimelineIO/actions/runs?status=success",  # noqa: E501
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
        "No run for a workflow named {0!r} found for commit {1!r}.".format(
            args.workflow, args.sha
        )
    )
    sys.exit(1)


print("Found workflow:")
print("  Name:       {0}".format(workflow_run["name"]))
print("  Branch:     {0}".format(workflow_run["head_branch"]))
print("  Commit:     {0}".format(workflow_run["head_sha"]))
print("  Committer:  {0}".format(workflow_run["head_commit"]["committer"]))
print("  Run Number: {0}".format(workflow_run["run_number"]))
print("  Status:     {0}".format(workflow_run["status"]))
print("  Conclusion: {0}".format(workflow_run["conclusion"]))
print("  URL:        {0}".format(workflow_run["html_url"]))


print("Getting list of artifacts")
request = urllib.request.Request(workflow_run["artifacts_url"], headers=headers)
response = urllib.request.urlopen(request).read()
artifacts = json.loads(response)["artifacts"]
for artifact in artifacts:
    if artifact["name"] == args.artifact:
        artifact_download_url = artifact["archive_download_url"]
        break
else:
    sys.stderr.write("No artifact named {0!r} found.".format(args.artifact))
    sys.exit(1)

print(
    "Downloading {0!r} artifact and unzipping to {1!r}".format(
        args.artifact, args.directory
    )
)

request = urllib.request.Request(artifact_download_url, headers=headers)
file_content = urllib.request.urlopen(request).read()

zip_file = zipfile.ZipFile(io.BytesIO(file_content))
for zip_info in zip_file.infolist():
    output_path = os.path.join(args.directory, zip_info.filename)

    print("Writing {0!r} to {1!r}".format(zip_info.filename, output_path))
    with open(output_path, "wb") as fd:
        fd.write(zip_file.open(zip_info).read())

    # Keep the timestamp!
    date_time = time.mktime(zip_info.date_time + (0, 0, -1))
    os.utime(output_path, (date_time, date_time))
