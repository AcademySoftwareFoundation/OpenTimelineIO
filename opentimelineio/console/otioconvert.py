#!/usr/bin/env python
#
# Copyright 2017 Pixar Animation Studios
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

import argparse
import sys
import ast
import copy

import opentimelineio as otio

__doc__ = """ Python wrapper around OTIO to convert timeline files between \
formats.

Available adapters: {}
""".format(otio.adapters.available_adapter_names())


def _parsed_args():
    """ parse commandline arguments with argparse """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i',
        '--input',
        type=str,
        required=True,
        help='path to input file',
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        required=True,
        help='path to output file',
    )
    parser.add_argument(
        '-I',
        '--input-adapter',
        type=str,
        default=None,
        help="Explicitly use this adapter for reading the input file",
    )
    parser.add_argument(
        '-O',
        '--output-adapter',
        type=str,
        default=None,
        help="Explicitly use this adapter for writing the output file",
    )
    parser.add_argument(
        '-T',
        '--tracks',
        type=str,
        default=None,
        help="Pick one or more tracks, by 0-based index, separated by commas.",
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
        '-A',
        '--output-adapter-arg',
        type=str,
        default=[],
        action='append',
        help='Extra arguments to be passed to output adapter in the form of '
        'key=value. Values are strings, numbers or Python literals: True, '
        'False, etc. Can be used multiple times: -A burrito="bar" -A taco=12.'
    )

    return parser.parse_args()


def main():
    """Parse arguments and convert the files."""

    args = _parsed_args()

    in_adapter = args.input_adapter
    if in_adapter is None:
        in_adapter = otio.adapters.from_filepath(args.input).name

    out_adapter = args.output_adapter
    if out_adapter is None:
        out_adapter = otio.adapters.from_filepath(args.output).name

    # allow user to explicitly set or pass to default or disable the linker.
    if args.media_linker.lower() == 'default':
        ml = otio.media_linker.MediaLinkingPolicy.ForceDefaultLinker
    elif args.media_linker.lower() in ['none', '']:
        ml = otio.media_linker.MediaLinkingPolicy.DoNotLinkMedia
    else:
        ml = args.media_linker

    argument_map = {}
    for pair in args.adapter_arg:
        if '=' in pair:
            key, val = pair.split('=', 1)  # only split on the 1st '='
            try:
                # Sometimes we need to pass a bool, int, list, etc.
                parsed_value = ast.literal_eval(val)
            except (ValueError, SyntaxError):
                # Fall back to a simple string
                parsed_value = val
            argument_map[key] = parsed_value
        else:
            print(
                "error: adapter arguments must be in the form key=value"
                " got: {}".format(pair)
            )
            sys.exit(1)

    result_tl = otio.adapters.read_from_file(
        args.input,
        in_adapter,
        media_linker_name=ml,
        **argument_map
    )

    if args.tracks:
        result_tracks = copy.deepcopy(otio.schema.Stack())
        del result_tracks[:]
        for track in args.tracks.split(","):
            tr = result_tl.tracks[int(track)]
            del result_tl.tracks[int(track)]
            print("track {0} is of kind: '{1}'".format(track, tr.kind))
            result_tracks.append(tr)
        result_tl.tracks = result_tracks

    argument_map = {}
    for pair in args.output_adapter_arg:
        if '=' in pair:
            key, val = pair.split('=', 1)  # only split on the 1st '='
            try:
                # Sometimes we need to pass a bool, int, list, etc.
                parsed_value = ast.literal_eval(val)
            except (ValueError, SyntaxError):
                # Fall back to a simple string
                parsed_value = val
            argument_map[key] = parsed_value
        else:
            print(
                "error: adapter arguments must be in the form key=value"
                " got: {}".format(pair)
            )
            sys.exit(1)

    otio.adapters.write_to_file(
        result_tl,
        args.output,
        out_adapter,
        **argument_map
    )


if __name__ == '__main__':
    try:
        main()
    except otio.exceptions.OTIOError as err:
        sys.stderr.write("ERROR: " + str(err) + "\n")
        sys.exit(1)
