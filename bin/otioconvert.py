#!/usr/bin/env python2.7

# python
import argparse
import sys

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
        help="Instead of inferring the adapter to use, pick from the list.",
    )
    parser.add_argument(
        '-O',
        '--output-adapter',
        type=str,
        default=None,
        help="Instead of inferring the adapter to use, pick from the list.",
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
        default=None,
        help="Specify a media linker.",
    )

    return parser.parse_args()


def main():
    """ Parse arguments and convert the files. """

    args = _parsed_args()

    in_adapter = args.input_adapter
    if in_adapter is None:
        in_adapter = otio.adapters.from_filepath(args.input).name

    out_adapter = args.output_adapter
    if out_adapter is None:
        out_adapter = otio.adapters.from_filepath(args.output).name

    ml = otio.media_linker.MediaLinkingPolicy.ForceDefaultLinker
    if args.media_linker:
        ml = args.media_linker

    result_tl = otio.adapters.read_from_file(args.input, in_adapter, media_linker_name=ml)

    if args.tracks:
        result_tracks = []
        for track in args.tracks.split(","):
            result_tracks.append(result_tl.tracks[int(track)])
        result_tl.tracks = result_tracks

    otio.adapters.write_to_file(result_tl, args.output, out_adapter)


if __name__ == '__main__':
    try:
        main()
    except otio.exceptions.OTIOError as err:
        sys.stderr.write("ERROR: " + str(err) + "\n")
        sys.exit(1)
