#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import argparse
import sys
import copy

import opentimelineio as otio

# on some python interpreters, pkg_resources is not available
try:
    import pkg_resources
except ImportError:
    pkg_resources = None

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
        required=False,
        help='path to input file',
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        required=False,
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
    parser.add_argument(
        '--version',
        default=False,
        action="store_true",
        help=(
            "Print the otio and pkg_resource installed plugin version "
            "information to the commandline and then exit."
        ),
    )

    trim_args = parser.add_argument_group(
        title="Trim Arguments",
        description="Arguments that allow you to trim the OTIO file."
    )
    trim_args.add_argument(
        '--begin',
        type=str,
        default=None,
        help=(
            "Trim out everything in the timeline before this time, in the "
            "global time frame of the timeline.  Argument should be in the form"
            ' "VALUE,RATE", eg: --begin "10,24".  Requires --end argument.'
        ),
    )
    trim_args.add_argument(
        '--end',
        type=str,
        default=None,
        help=(
            "Trim out everything in the timeline after this time, in the "
            "global time frame of the timeline.  Argument should be in the form"
            ' "VALUE,RATE", eg: --begin "10,24".  Requires --begin argument.'
        ),
    )

    result = parser.parse_args()

    # print version information to the shell
    if result.version:
        print(f"OpenTimelineIO version: {otio.__version__}")

        if pkg_resources:
            pkg_resource_plugins = list(
                pkg_resources.iter_entry_points("opentimelineio.plugins")
            )
            if pkg_resource_plugins:
                print("Plugins from pkg_resources:")
                for plugin in pkg_resource_plugins:
                    print(f"   {plugin.dist}")
            else:
                print("No pkg_resource plugins installed.")
        parser.exit()

    if not result.input:
        parser.error("-i/--input is a required argument")
    if not result.output:
        parser.error("-o/--output is a required argument")

    if result.begin is not None and result.end is None:
        parser.error("--begin requires --end.")
    if result.end is not None and result.begin is None:
        parser.error("--end requires --begin.")

    if result.begin is not None:
        try:
            value, rate = result.begin.split(",")
            result.begin = otio.opentime.RationalTime(float(value), float(rate))
        except ValueError:
            parser.error(
                "--begin argument needs to be of the form: VALUE,RATE where "
                "VALUE is the (float) time value of the resulting RationalTime "
                "and RATE is the (float) time rate of the resulting RationalTime,"
                " not '{}'".format(result.begin)
            )

    if result.end is not None:
        try:
            value, rate = result.end.split(",")
            result.end = otio.opentime.RationalTime(float(value), float(rate))
        except ValueError:
            parser.error(
                "--end argument needs to be of the form: VALUE,RATE where "
                "VALUE is the (float) time value of the resulting RationalTime "
                "and RATE is the (float) time rate of the resulting RationalTime,"
                " not '{}'".format(result.begin)
            )

    return result


def main():
    """Parse arguments and convert the files."""

    args = _parsed_args()

    in_adapter = args.input_adapter
    if in_adapter is None:
        in_adapter = otio.adapters.from_filepath(args.input).name

    out_adapter = args.output_adapter
    if out_adapter is None:
        out_adapter = otio.adapters.from_filepath(args.output).name

    media_linker_name = otio.console.console_utils.media_linker_name(
        args.media_linker
    )

    try:
        read_adapter_arg_map = otio.console.console_utils.arg_list_to_map(
            args.adapter_arg,
            "input adapter"
        )
        hooks_args = otio.console.console_utils.arg_list_to_map(
            args.hook_function_arg,
            "hook function"
        )
        ml_args = otio.console.console_utils.arg_list_to_map(
            args.media_linker_arg,
            "media linker"
        )
    except ValueError as exc:
        sys.stderr.write("\n" + str(exc) + "\n")
        sys.exit(1)

    result_tl = otio.adapters.read_from_file(
        args.input,
        in_adapter,
        hook_function_argument_map=hooks_args,
        media_linker_name=media_linker_name,
        media_linker_argument_map=ml_args,
        **read_adapter_arg_map
    )

    if args.tracks:
        result_tracks = copy.deepcopy(otio.schema.Stack())
        del result_tracks[:]
        for track in args.tracks.split(","):
            tr = result_tl.tracks[int(track)]
            del result_tl.tracks[int(track)]
            print(f"track {track} is of kind: '{tr.kind}'")
            result_tracks.append(tr)
        result_tl.tracks = result_tracks

    # handle trim arguments
    if args.begin is not None and args.end is not None:
        result_tl = otio.algorithms.timeline_trimmed_to_range(
            result_tl,
            otio.opentime.range_from_start_end_time(args.begin, args.end)
        )

    try:
        write_adapter_arg_map = otio.console.console_utils.arg_list_to_map(
            args.output_adapter_arg,
            "output adapter"
        )
    except ValueError as exc:
        sys.stderr.write("\n" + str(exc) + "\n")
        sys.exit(1)

    otio.adapters.write_to_file(
        result_tl,
        args.output,
        out_adapter,
        hook_function_argument_map=hooks_args,
        **write_adapter_arg_map
    )


if __name__ == '__main__':
    try:
        main()
    except otio.exceptions.OTIOError as err:
        sys.stderr.write("ERROR: " + str(err) + "\n")
        sys.exit(1)
