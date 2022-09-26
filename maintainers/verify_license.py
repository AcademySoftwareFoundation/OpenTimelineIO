#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """The utility script checks to make sure that all of the source
files in the OpenTimelineIO project have the correct license header."""

import argparse
import os
import sys

LICENSES = {
    ".py": """# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project
""",
    ".cpp": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
""",
    ".c": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
""",
    ".h": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
""",
    ".swift": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
""",
    ".mm": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
"""
}

# dependencies and build dir do not need to be checked
SKIP_DIRS = [
    os.path.join("src", "deps"),
    "build",
    ".git",
]


def _parsed_args():
    """ parse commandline arguments with argparse """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-s',
        '--start-dir',
        default='.',
        type=str,
        help=("Directory to start searching for files in.")
    )
    parser.add_argument(
        '-f',
        '--fix',
        default=False,
        action="store_true",
        help="Fix licenses in place when possible"
    )

    return parser.parse_args()


def main():
    correct_license = 0
    incorrect_license = 0
    total = 0

    args = _parsed_args()

    for root, dirs, files in os.walk(args.start_dir):
        for filename in files:
            # make sure the dependencies aren't checked
            if any(d in root for d in SKIP_DIRS):
                continue
            fullpath = os.path.join(root, filename)
            for ext, lic in LICENSES.items():
                if filename.endswith(ext):
                    total += 1
                    try:
                        content = open(fullpath).read()
                    except Exception as ex:
                        sys.stderr.write(
                            "ERROR: Unable to read file: {}\n{}".format(
                                fullpath,
                                ex
                            )
                        )
                        continue

                    if len(content) > 0 and lic not in content:
                        print(f"MISSING: {os.path.relpath(fullpath)}")
                        if args.fix:
                            content = LICENSES[os.path.splitext(fullpath)[1]]
                            with open(fullpath) as fi:
                                content += fi.read()
                            with open(fullpath, 'w') as fo:
                                fo.write(content)
                            print(
                                "...FIXED: {}".format(
                                    os.path.relpath(fullpath)
                                )
                            )
                        incorrect_license += 1
                    else:
                        correct_license += 1

    print(
        "{} of {} files have the correct license.".format(
            correct_license,
            total
        )
    )

    if incorrect_license != 0:
        if not args.fix:
            raise RuntimeError(
                "ERROR: {} files do NOT have the correct license.\n".format(
                    incorrect_license
                )
            )
        else:
            print(
                "{} files had the correct license added.".format(
                    incorrect_license
                )
            )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as err:
        sys.stderr.write(err.args[0])
        sys.exit(1)
