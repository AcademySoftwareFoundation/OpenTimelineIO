#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import argparse
import json
import urllib.request
import os

CONTRIBUTORS_FILE = "CONTRIBUTORS.md"


def parse_args():
    parser = argparse.ArgumentParser(
        description='Fetch a list of contributors for a given GitHub repo.'
    )
    parser.add_argument(
        '--repo',
        required=True,
        help='GitHub Project/Repo name.'
        ' (e.g. "AcademySoftwareFoundation/OpenTimelineIO")'
    )
    parser.add_argument(
        '--token',
        required=False,
        default=None,
        help='GitHub personal access token, used for authorization.'
        ' Get one here: https://github.com/settings/tokens/new'
    )
    return parser.parse_args()


def main():
    args = parse_args()

    token = args.token or os.environ.get("OTIO_RELEASE_GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "Error: a github token is required to run {}.  Either pass it in "
            "via --token or set $OTIO_RELEASE_GITHUB_TOKEN".format(__file__)
        )

    # Note: un-authenticated requests have a strict rate limit.
    # We avoid this by using authentication for all our requests,
    # even the ones that don't need it.
    #
    # You can fetch your limits with this API:
    #
    # request = urllib.request.Request(
    #     "https://api.github.com/rate_limit",
    #     headers = {"Authorization": "token {}".format(token)}
    # )
    # response = urllib.request.urlopen(request).read().decode('utf-8')
    # print("Rate limit: {}".format(response))

    with open(CONTRIBUTORS_FILE) as fi:
        input_contributors = fi.read()

    request = urllib.request.Request(
        f"https://api.github.com/repos/{args.repo}/stats/contributors",
        headers={"Authorization": f"token {args.token}"}
    )
    response = urllib.request.urlopen(request).read().decode('utf-8')

    # this just ensures that response is really waited on so that json.loads
    # works
    print(f"Response size: {len(response)}")

    contributors = json.loads(response[:])

    output_lines = []

    if not contributors:
        print("No contributors found, something likely went wrong.")
        print(response)

    for contributor in contributors:

        login = contributor['author']['login']
        url = contributor['author']['html_url']
        total = contributor['total']

        request = urllib.request.Request(
            f"https://api.github.com/users/{login}",
            headers={"Authorization": f"token {args.token}"}
        )
        response = urllib.request.urlopen(request).read().decode('utf-8')

        user = json.loads(response)
        name = user['name'] or "?"

        if (
            login not in input_contributors
            and name not in input_contributors
            and "?" not in name
        ):
            print(f"Missing: {name} [{login}] # commits: {total}")

            # Print the output in markdown format
            output_lines.append(f"* {name} ([{login}]({url}))")

    if output_lines:
        # split the input_contributors into preamble and contributors list
        split_contribs = input_contributors.split('\n')

        header = []
        body = []
        in_body = False
        for ln in split_contribs:
            if not in_body and ln.startswith("* "):
                in_body = True

            if not in_body:
                header.append(ln)
                continue

            if ln.strip():
                body.append(ln)

        body.extend(output_lines)
        body.sort(key=lambda v: v.lower())

        result = '\n'.join(header + body)

        with open(CONTRIBUTORS_FILE, 'w') as fo:
            fo.write(result)
    else:
        print(f"All contributors present in {CONTRIBUTORS_FILE}")

    # print("\n".join(sorted(output_lines, key=str.casefold)))


if __name__ == '__main__':
    main()
