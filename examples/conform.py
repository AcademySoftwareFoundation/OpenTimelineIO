#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Example OTIO script that reads a timeline and then relinks clips
to movie files found in a given folder, based on matching clip names to filenames.

Demo:

% ls -1R
editorial_cut.otio
media/
    shot1.mov
    shot17.mov
    shot99.mov

% conform.py -i editorial_cut.otio -f media -o conformed.otio
Relinked 3 clips to new media.
Saved conformed.otio with 100 clips.

% diff editorial_cut.otio conformed.otio
...

"""

import argparse
from argparse import RawTextHelpFormatter
import glob
import os

import opentimelineio as otio


def parse_args():
    """ parse arguments out of sys.argv """
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        '-i',
        '--input',
        type=str,
        required=True,
        help='Timeline file to read. Supported formats: {adapters}'
             ''.format(adapters=otio.adapters.available_adapter_names())
    )
    parser.add_argument(
        '-f',
        '--folder',
        type=str,
        required=True,
        help='Folder to look for media in.'
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        required=True,
        help="Timeline file to write out."
    )
    return parser.parse_args()


def _find_matching_media(name, folder):
    """Look for media with this name in this folder."""

    # This function is an example which searches the file system for matching media.
    # A real world studio implementation would likely look in an asset management system
    # and use studio-specific metadata in the clip's metadata dictionary instead
    # of matching the clip name.
    # For example:
    # shot = asset_database.find_shot(clip.metadata['mystudio']['shotID'])
    # new_media = shot.latest_render(format='mov')

    matches = glob.glob(f"{folder}/{name}.*")
    matches = list(map(os.path.abspath, matches))

    if not matches:
        # print "DEBUG: No match for clip '{0}'".format(name)
        return None
    if len(matches) == 1:
        return matches[0]
    print(
        "WARNING: {} matches found for clip '{}', using '{}'".format(
            len(matches),
            name,
            matches[0]
        )
    )
    return matches[0]


def _conform_timeline(timeline, folder):
    """ Look for replacement media for each clip in the given timeline.

    The clips are relinked in place if media with a matching name is found.
    """

    count = 0

    for clip in timeline.find_clips():
        # look for a media file that matches the clip's name
        new_path = _find_matching_media(clip.name, folder)

        # if no media is found, keep going
        if not new_path:
            continue

        # relink to the found path
        clip.media_reference = otio.schema.ExternalReference(
            target_url="file://" + new_path,
            available_range=None  # the available range is unknown without
                                  # opening the file
        )
        count += 1

    return count


def main():
    args = parse_args()

    timeline = otio.adapters.read_from_file(args.input)
    count = _conform_timeline(timeline, args.folder)
    print(f"Relinked {count} clips to new media.")
    otio.adapters.write_to_file(timeline, args.output)
    print(
        "Saved {} with {} clips.".format(
            args.output,
            len(list(timeline.find_clips()))
        )
    )


if __name__ == '__main__':
    main()
