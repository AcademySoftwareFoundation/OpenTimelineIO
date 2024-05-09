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


def fetch_plat_map():
    # HACK: pull the image version corresponding to -latest out of the
    #       README.md for the github repo where they are stored
    request = urllib.request.Request(GITHUB_README_URL)
    response = urllib.request.urlopen(request).read().decode('utf-8')

    def md_row_fields(md_row):
        # Split on |, discard the empty entries from leading and trailing |
        return [
            col.strip() for col in md_row.split("|")[1:-1]
        ]

    # First, just strip the readme down the platform image table
    lines = response.split("\n")
    table_lines = []
    in_images_section = False
    for line in lines:
        if not in_images_section and line.startswith("## Available Images"):
            in_images_section = True
            continue
        elif in_images_section and line.startswith("#"):
            break
        elif not in_images_section:
            continue

        if line.startswith("|"):
            table_lines.append(line.strip())

    # Extract the table column labels
    plat_col_labels = md_row_fields(table_lines[0])

    platform_name_re = re.compile(r"`([^`]*)`")
    entries = {}
    for line in table_lines[2:]:
        col_data = md_row_fields(line)
        plat_entry = dict(zip(plat_col_labels, col_data))
        raw_labels = plat_entry["YAML Label"]
        available_labels = platform_name_re.findall(raw_labels)
        try:
            next(
                label for label in available_labels
                if label.split("-")[-1] == "latest"
            )
        except StopIteration:
            # not a latest label
            continue

        label = next(
            label for label in available_labels
            if label.split("-")[-1] not in {"xl", "xlarge", "latest"}
        )
        platform = label.split("-")[0]
        if platform not in PLATFORMS:
            continue
        entries[platform] = label

    return entries


def main():
    args = _parsed_args()

    plat_map = fetch_plat_map()

    if args.freeze:
        freeze_ci(plat_map, args.dryrun)

    if args.unfreeze:
        unfreeze_ci(plat_map, args.dryrun)


def freeze_ci(plat_map, dryrun=False):
    modified = False
    with open(CI_WORKFLOW_FP) as fi:
        output_content = fi.read()

    for plat in plat_map:
        plat_latest = plat + "-latest"
        if plat_latest not in output_content:
            print(f"Platform {plat} appears to already be frozen.")
            continue

        output_content = output_content.replace(plat_latest, plat_map[plat])
        modified = True
        print(f"Platform {plat} frozen to version: {plat_map[plat]}")

    if modified and not dryrun:
        with open(CI_WORKFLOW_FP, 'w') as fo:
            fo.write(output_content)
        return True

    return False


def unfreeze_ci(plat_map, dryrun=False):
    modified = False
    with open(CI_WORKFLOW_FP) as fi:
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
        print(f"Platform {plat} unfrozen back to: {plat_latest}")

    if modified and not dryrun:
        with open(CI_WORKFLOW_FP, 'w') as fo:
            fo.write(output_content)
        return True

    return False


if __name__ == "__main__":
    main()
