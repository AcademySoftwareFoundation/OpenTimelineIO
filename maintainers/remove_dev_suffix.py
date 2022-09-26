#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """Strip or add the .dev1 suffix, part of the release process"""

import argparse
import sys

TARGET_FILES = [
    "setup.py"
]


def _parsed_args():
    parser = argparse.ArgumentParser(
        description='Fetch a list of contributors for a given GitHub repo.'
    )

    op_grp = parser.add_mutually_exclusive_group(required=True)
    op_grp.add_argument(
        "-a",
        "--add",
        default=False,
        action="store_true",
        help="add the dev1 suffix to the version"
    )
    op_grp.add_argument(
        "-r",
        "--remove",
        default=False,
        action="store_true",
        help="remove the dev1 suffix to the version"
    )
    parser.add_argument(
        "-d",
        "--dryrun",
        default=False,
        action="store_true",
        help="Perform actions but modify no files on disk."
    )
    return parser.parse_args()


def _target_version():
    return "0.15.0"


def main():
    args = _parsed_args()

    version = _target_version()

    for fp in TARGET_FILES:
        with open(fp, 'r') as fi:
            content = fi.read()

        if args.add:
            modified = add_suffix(content, version)
        elif args.remove:
            modified = remove_suffix(content, version)

        if modified and not args.dryrun:
            with open(fp, 'w') as fo:
                fo.write(content)
            print("Wrote modified {}.".format(fp))


def add_suffix(content, version):
    if version not in content:
        sys.stderr.write(
            "Version {} not found, suffix may have already been "
            "added.\n".format(version)
        )
        return False

    print("adding suffix, version will be: {}".format(version + ".dev1"))
    content.replace(version, version + ".dev1")
    return True


def remove_suffix(content, version):
    if version+'.dev1' not in content:
        sys.stderr.write(
            "Version+Suffix {} not found, suffix may have already been "
            "removed.\n".format(version+'.dev1')
        )
        return False

    content.replace(version+'.dev1', version)
    return True


if __name__ == "__main__":
    main()
