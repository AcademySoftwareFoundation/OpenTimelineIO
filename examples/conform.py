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

"""Example OTIO script that reads a timeline and then relinks clips
to movie files found in a given folder, based on matching names.

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
import glob
import os

import opentimelineio as otio


def parse_args():
    """ parse arguments out of sys.argv """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'input',
        type=str,
        required=True,
        help='Timeline file(s) to read. Any format supported by OTIO will'
        ' work.'
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

    # In this case we're looking in the filesystem.
    # In your case, you might want to look in your asset management system
    # and you might want to use studio-specific metadata in the clip instead
    # of just the clip name.
    # Something like this:
    # shot = asset_database.find_shot(clip.metadata['mystudio']['shotID'])
    # new_media = shot.latest_render(format='mov')

    matches = glob.glob("{0}/{1}.*".format(folder, name))
    matches = map(os.path.abspath, matches)

    if len(matches) == 0:
        # print "DEBUG: No match for clip '{0}'".format(name)
        return None
    if len(matches) == 1:
        return matches[0]
    else:
        print(
            "WARNING: {0} matches found for clip '{1}', using '{2}'".format(
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

    for clip in timeline.each_clip():
        # look for a media file that matches the clip's name
        new_path = _find_matching_media(clip.name, folder)

        # if no media is found, keep going
        if not new_path:
            continue

        # if we found one, then relink to the new path
        clip.media_reference = otio.schema.ExternalReference(
            target_url="file://" + new_path,
            available_range=None    # we don't know the available range
        )
        count += 1

    return count


def main():
    args = parse_args()

    timeline = otio.adapters.read_from_file(args.input)
    count = _conform_timeline(timeline, args.folder)
    print("Relinked {0} clips to new media.".format(count))
    otio.adapters.write_to_file(timeline, args.output)
    print(
        "Saved {} with {} clips.".format(
            args.output,
            len(list(timeline.each_clip()))
        )
    )


if __name__ == '__main__':
    main()
