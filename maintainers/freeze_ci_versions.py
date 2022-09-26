#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """Freeze and unfreeze image versions for CI, part of the release
process.

"""

import argparse
import re
import urllib.request

CI_WORKFLOW_FP = ".github/workflows/python-package.yml"
GITHUB_README_URL = (
    "https://raw.githubusercontent.com/actions/runner-images/main/README.md"
)
PLATFORMS = ["ubuntu", "macos", "windows"]


def _parsed_args():
    parser = argparse.ArgumentParser(
        description='Fetch a list of contributors for a given GitHub repo.'
    )

    op_grp = parser.add_mutually_exclusive_group(required=True)
    op_grp.add_argument(
        "-f",
        "--freeze",
        default=False,
        action="store_true",
        help="freeze the ci version from latest to their version."
    )
    op_grp.add_argument(
        "-u",
        "--unfreeze",
        default=False,
        action="store_true",
        help="unfreeze the ci version from the version back to latest."
    )
    parser.add_argument(
        "-d",
        "--dryrun",
        default=False,
        action="store_true",
        help="Perform actions but modify no files on disk."
    )
    return parser.parse_args()


def main():
    args = _parsed_args()

    request = urllib.request.Request(GITHUB_README_URL)
    response = urllib.request.urlopen(request).read().decode('utf-8')

    # HACK: pull the image version corresponding to -latest out of the
    #       README.md for the github repo where they are stored
    lines = response.split("\n")
    plat_map = {}
    for plat in PLATFORMS:
        plat_latest = plat + "-latest"
        for ln in lines:
            if plat_latest not in ln:
                continue
            plat_map[plat] = (
                re.match(".*(" + plat + "-.*)`.*", ln).groups(0)[0]
            )

    if args.freeze:
        freeze_ci(plat_map, args.dryrun)

    if args.unfreeze:
        unfreeze_ci(plat_map, args.dryrun)


def freeze_ci(plat_map, dryrun=False):
    modified = False
    with open(CI_WORKFLOW_FP, 'r') as fi:
        output_content = fi.read()

    for plat in plat_map:
        plat_latest = plat + "-latest"
        if plat_latest not in output_content:
            print("Platform {} appears to already be frozen.".format(plat))
            continue

        output_content = output_content.replace(plat_latest, plat_map[plat])
        modified = True
        print("Platform {} frozen to version: {}".format(plat, plat_map[plat]))

    if modified and not dryrun:
        with open(CI_WORKFLOW_FP, 'w') as fo:
            fo.write(output_content)
        return True

    return False


def unfreeze_ci(plat_map, dryrun=False):
    modified = False
    with open(CI_WORKFLOW_FP, 'r') as fi:
        output_content = fi.read()

    for plat, plat_current in plat_map.items():
        plat_latest = plat + "-latest"
        if plat_current not in output_content:
            print(
                "Platform {} appears to already be set to -latest.".format(
                    plat
                )
            )
            continue

        output_content = output_content.replace(plat_current, plat_latest)
        modified = True
        print("Platform {} unfrozen back to: {}".format(plat, plat_latest))

    if modified and not dryrun:
        with open(CI_WORKFLOW_FP, 'w') as fo:
            fo.write(output_content)
        return True

    return False


if __name__ == "__main__":
    main()
