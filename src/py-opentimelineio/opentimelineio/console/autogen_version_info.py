#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Generate the schema-version map for this version of OTIO"""

import os
import argparse
import tempfile

import opentimelineio as otio


LABEL_MAP_TEMPLATE = """{{ "{label}",
        {{
{sv_map}
        }}
    }},
    // {{next}}"""
MAP_ITEM_TEMPLATE = '{indent}{{ "{key}", {value} }},'
INDENT = 12


def _parsed_args():
    """ parse commandline arguments with argparse """

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
        "-o",
        "--output",
        type=str,
        default=None,
        help="Filepath to write result to."
    )

    return parser.parse_args()


def _insert_current_schema_version_map(src_text, label, version_map):
    src_text = src_text.replace("{", "{{").replace("}", "}}")
    src_text = src_text.replace("// {{next}}", "{next}")

    map_text = []
    for key, value in version_map.items():
        map_text.append(
                MAP_ITEM_TEMPLATE.format(
                    indent=' ' * INDENT,
                    key=key,
                    value=value
                )
        )
    map_text = '\n'.join(map_text)

    next_text = LABEL_MAP_TEMPLATE.format(label=label, sv_map=map_text)
    return src_text.format(label=label, next=next_text)


def main():
    """  main entry point  """

    args = _parsed_args()

    dirname = os.path.dirname(__file__)

    with open(os.path.join(dirname, "built_in_version_header.cpp"), 'r') as fi:
        input = fi.read()

    result = _insert_current_schema_version_map(
            input,
            args.label,
            otio.core.type_version_map()
    )

    # print it out somewhere
    if args.dryrun:
        print(result)
        return

    output = args.output
    if not output:
        output = tempfile.NamedTemporaryFile(
            'w',
            suffix="built_in_version_header.cpp",
            delete=False
        ).name

    with open(output, 'w') as fo:
        fo.write(result)

    print("Wrote schema-version map to: '{}'.".format(output))


if __name__ == '__main__':
    main()
