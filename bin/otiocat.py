#!/usr/bin/env python2.7

import argparse

import opentimelineio as otio

__doc__ = """ Print the contents of an OTIO file to stdout.  """


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

    return parser.parse_args()


def _cat_otio_file(fpath):
    """Print the JSON for the input file."""

    adapter = otio.adapters.from_name("otio_json")
    return adapter.write_to_string(otio.adapters.read_from_file(fpath))


def main():
    """Parse arguments and call _cat_otio_file."""
    args = _parsed_args()

    for fpath in args.filepath:
        print("fpath: {}".format(fpath))
        print(_cat_otio_file(fpath))


if __name__ == '__main__':
    main()
