#!/usr/bin/env python2.7
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

"""Print the contents of an OTIO file to stdout."""

import argparse

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

    return parser.parse_args()


def _otio_compatible_file_to_json_string(fpath):
    """Read the file at fpath with the default otio adapter and return the json
    as a string.
    """

    adapter = otio.adapters.from_name("otio_json")
    return adapter.write_to_string(otio.adapters.read_from_file(fpath))


def main():
    """Parse arguments and call _otio_compatible_file_to_json_string."""

    args = _parsed_args()

    for fpath in args.filepath:
        print(_otio_compatible_file_to_json_string(fpath))


if __name__ == '__main__':
    main()
