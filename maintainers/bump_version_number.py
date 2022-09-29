#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """Manage and apply the version in the OTIO_VERSION.json file"""

import argparse
import sys
import json

OTIO_VERSION_JSON_PATH = "OTIO_VERSION.json"


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
        major, minor, patch = args.set
    elif args.query:
        print(".".join(str(v) for v in (major, minor, patch)))
        return

    print(f"Setting version to: {major}.{minor}.{patch}")

    # update the OTIO_VERSION file
    with open(OTIO_VERSION_JSON_PATH, "w") as fo:
        fo.write(
            json.dumps({"version": [str(v) for v in (major, minor, patch)]})
        )
    print(f"Updated {OTIO_VERSION_JSON_PATH}")

    #  update the CMakeLists.txt
    with open("CMakeLists.txt") as fi:
        cmake_input = fi.read()

    cmake_output = []
    key_map = {"MAJOR": major, "MINOR": minor, "PATCH": patch}
    for ln in cmake_input.split("\n"):
        for label, new_value in key_map.items():
            if f"set(OTIO_VERSION_{label} \"" in ln:
                cmake_output.append(
                    f"set(OTIO_VERSION_{label} \"{new_value}\")"
                )
                break
        else:
            cmake_output.append(ln)

    with open("CMakeLists.txt", 'w') as fo:
        fo.write("\n".join(cmake_output))
    print("Updated {}".format("CMakeLists.txt"))

    # update the setup.py
    with open("setup.py") as fi:
        setup_input = fi.read()

    setup_output = []
    for ln in setup_input.split("\n"):
        if "\"version\": " in ln:

            setup_output.append(
                "    \"version\": \"{}.{}.{}{}\",".format(
                    major,
                    minor,
                    patch,
                    (".dev1" in ln) and ".dev1" or ""
                )
            )
        else:
            setup_output.append(ln)

    with open("setup.py", 'w') as fo:
        fo.write("\n".join(setup_output))
    print("Updated {}".format("setup.py"))


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
    if version + '.dev1' not in content:
        sys.stderr.write(
            "Version+Suffix {} not found, suffix may have already been "
            "removed.\n".format(version + '.dev1')
        )
        return False

    content.replace(version + ' .dev1', version)
    return True


if __name__ == "__main__":
    main()
