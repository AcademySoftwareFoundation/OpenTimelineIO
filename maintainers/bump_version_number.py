#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """Manage and apply the version in the OTIO_VERSION.json file"""

import argparse
import json
import re

OTIO_VERSION_JSON_PATH = "OTIO_VERSION.json"
VERSION_HEADERS = [
    ("src/opentime/version.h", "OPENTIME"),
    ("src/opentimelineio/version.h", "OPENTIMELINEIO"),
]


def version():
    with open(OTIO_VERSION_JSON_PATH) as fi:
        return json.load(fi)['version']


def _parsed_args():
    parser = argparse.ArgumentParser(
        description='Fetch a list of contributors for a given GitHub repo.'
    )

    op_grp = parser.add_mutually_exclusive_group(required=True)
    op_grp.add_argument(
        "-i",
        "--increment",
        type=str,
        default=None,
        choices=("major", "minor", "patch"),
        help="Increment either the major or minor version number."
    )
    op_grp.add_argument(
        "-s",
        "--set",
        type=str,
        default=None,
        nargs=3,
        help="Set the version string, in the form of MAJOR MINOR PATCH"
    )
    op_grp.add_argument(
        "-q",
        "--query",
        default=False,
        action="store_true",
        help="Query/print the current version without changing it"
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

    major, minor, patch = (int(v) for v in version())

    if args.increment == "major":
        major += 1
        minor = 0
        patch = 0
    elif args.increment == "minor":
        minor += 1
        patch = 0
    elif args.increment == "patch":
        patch += 1
    elif args.set:
        major, minor, patch = (int(v) for v in args.set)
    elif args.query:
        print(".".join(str(v) for v in (major, minor, patch)))
        return

    print(f"Setting version to: {major}.{minor}.{patch}")

    # Make all of the changes before writing anything, so that an error
    # does not leave the files with different versions
    changes = [(
        OTIO_VERSION_JSON_PATH,
        json.dumps({"version": [str(v) for v in (major, minor, patch)]})
    )]

    # update the version headers, which CMake also reads the version from.
    # The version and namespace names, for example v0_19_0 and v0_19, are
    # updated along with the numbers.
    for path, prefix in VERSION_HEADERS:
        with open(path) as fi:
            content = fi.read()
        for pattern, value in (
            (r"_VERSION_MAJOR )\d+", major),
            (r"_VERSION_MINOR )\d+", minor),
            (r"_VERSION_PATCH )\d+", patch),
            (r"_VERSION )v\d+_\d+_\d+", f"v{major}_{minor}_{patch}"),
            (r"_VERSION_NS )v\d+_\d+", f"v{major}_{minor}"),
        ):
            content = _replace_once(
                path,
                content,
                r"(#define {}{}".format(prefix, pattern),
                r"\g<1>{}".format(value)
            )
        changes.append((path, content))

    # update the setup.py, keeping the .dev1 suffix if it is there
    with open("setup.py") as fi:
        content = fi.read()
    changes.append(("setup.py", _replace_once(
        "setup.py",
        content,
        r'("version": ")\d+\.\d+\.\d+((\.dev1)?",)',
        r"\g<1>{}.{}.{}\g<2>".format(major, minor, patch)
    )))

    for path, content in changes:
        if not args.dryrun:
            with open(path, "w") as fo:
                fo.write(content)
        print(f"Updated {path}")


def _replace_once(path, content, pattern, replacement):
    content, count = re.subn(pattern, replacement, content)
    if count != 1:
        raise RuntimeError(
            "Expected one match for '{}' in {}, found {}".format(
                pattern, path, count
            )
        )
    return content


if __name__ == "__main__":
    main()
