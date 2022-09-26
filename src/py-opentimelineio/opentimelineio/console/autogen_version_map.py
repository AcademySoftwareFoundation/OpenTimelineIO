#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Generate the CORE_VERSION_MAP for this version of OTIO"""

import argparse
import tempfile

import opentimelineio as otio


LABEL_MAP_TEMPLATE = """{{ "{label}",
      {{
{sv_map}
      }} }},
    // {{next}}"""
MAP_ITEM_TEMPLATE = '{indent}{{ "{key}", {value} }},'
INDENT = 10


def _parsed_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-d",
        "--dryrun",
        default=False,
        action="store_true",
        help="write to stdout instead of printing to file."
    )
    parser.add_argument(
        "-l",
        "--label",
        default=otio.__version__,
        # @TODO - should we strip the .dev1 label?  that would probably be
        #         more consistent since we don't do sub-beta releases
        help="Version label to assign this schema map to."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=None,
        required=True,
        help="Path to CORE_VERSION_MAP.last.cpp"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to where CORE_VERSION_MAP.cpp should be written to."
    )

    return parser.parse_args()


def generate_core_version_map(src_text, label, version_map):
    # turn the braces in the .cpp file into python-format template compatible
    # form ({{ }} where needed)
    src_text = src_text.replace("{", "{{").replace("}", "}}")
    src_text = src_text.replace("// {{next}}", "{next}")

    # iterate over the map and print the template out
    map_text = []
    for key, value in sorted(version_map.items()):
        map_text.append(
            MAP_ITEM_TEMPLATE.format(
                indent=' ' * INDENT,
                key=key,
                value=value
            )
        )
    map_text = '\n'.join(map_text)

    # assemble the result
    next_text = LABEL_MAP_TEMPLATE.format(label=label, sv_map=map_text)
    return src_text.format(label=label, next=next_text)


def main():
    args = _parsed_args()

    with open(args.input) as fi:
        input = fi.read()

    result = generate_core_version_map(
        input,
        args.label,
        otio.core.type_version_map()
    )

    if args.dryrun:
        print(result)
        return

    output = args.output
    if not output:
        output = tempfile.NamedTemporaryFile(
            'w',
            suffix="CORE_VERSION_MAP.cpp",
            delete=False
        ).name

    with open(output, 'w', newline="\n") as fo:
        fo.write(result)

    print(f"Wrote CORE_VERSION_MAP to: '{output}'.")


if __name__ == '__main__':
    main()
