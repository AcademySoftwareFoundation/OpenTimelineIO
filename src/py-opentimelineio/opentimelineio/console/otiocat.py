#!/usr/bin/env python
#
# Copyright Contributors to the OpenTimelineIO project
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""Print the contents of an OTIO file to stdout."""

import argparse
import sys

import opentimelineio as otio


def _parsed_args():
    """ parse commandline arguments with argparse """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'filepath',
        type=str,
        nargs='+',
        help='files to print the contents of'
    )
    parser.add_argument(
        '-a',
        '--adapter-arg',
        type=str,
        default=[],
        action='append',
        help='Extra arguments to be passed to input adapter in the form of '
        'key=value. Values are strings, numbers or Python literals: True, '
        'False, etc. Can be used multiple times: -a burrito="bar" -a taco=12.'
    )
    parser.add_argument(
        '-m',
        '--media-linker',
        type=str,
        default="Default",
        help=(
            "Specify a media linker.  'Default' means use the "
            "$OTIO_DEFAULT_MEDIA_LINKER if set, 'None' or '' means explicitly "
            "disable the linker, and anything else is interpreted as the name"
            " of the media linker to use."
        )
    )
    parser.add_argument(
        '-H',
        '--hook-function-arg',
        type=str,
        default=[],
        action='append',
        help='Extra arguments to be passed to the hook functions in the form of '
        'key=value. Values are strings, numbers or Python literals: True, '
        'False, etc. Can be used multiple times: -H burrito="bar" -H taco=12.'
    )
    parser.add_argument(
        '-M',
        '--media-linker-arg',
        type=str,
        default=[],
        action='append',
        help='Extra arguments to be passed to the media linker in the form of '
        'key=value. Values are strings, numbers or Python literals: True, '
        'False, etc. Can be used multiple times: -M burrito="bar" -M taco=12.'
    )

    return parser.parse_args()


def _otio_compatible_file_to_json_string(
        fpath,
        media_linker_name,
        hooks_args,
        media_linker_argument_map,
        adapter_argument_map
):
    """Read the file at fpath with the default otio adapter and return the json
    as a string.
    """

    adapter = otio.adapters.from_name("otio_json")
    return adapter.write_to_string(
        otio.adapters.read_from_file(
            fpath,
            hook_function_argument_map=hooks_args,
            media_linker_name=media_linker_name,
            media_linker_argument_map=media_linker_argument_map,
            **adapter_argument_map
        )
    )


def main():
    """Parse arguments and call _otio_compatible_file_to_json_string."""

    args = _parsed_args()

    media_linker_name = otio.console.console_utils.media_linker_name(
        args.media_linker
    )

    try:
        read_adapter_arg_map = otio.console.console_utils.arg_list_to_map(
            args.adapter_arg,
            "adapter"
        )
        hooks_args = otio.console.console_utils.arg_list_to_map(
            args.hook_function_arg,
            "hook function"
        )
        media_linker_argument_map = otio.console.console_utils.arg_list_to_map(
            args.media_linker_arg,
            "media linker"
        )
    except ValueError as exc:
        sys.stderr.write("\n" + str(exc) + "\n")
        sys.exit(1)

    for fpath in args.filepath:
        print(
            _otio_compatible_file_to_json_string(
                fpath,
                media_linker_name,
                hooks_args,
                media_linker_argument_map,
                read_adapter_arg_map
            )
        )


if __name__ == '__main__':
    main()
