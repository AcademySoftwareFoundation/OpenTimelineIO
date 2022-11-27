#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Print statistics about the otio file, including validation information."""

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
        help='files to operate on'
    )

    return parser.parse_args()


TESTS = []


def stat_check(name):
    def real_stat_check(fn):
        TESTS.append((name, fn))
        return fn
    return real_stat_check


@stat_check("parsed")
def _did_parse(input):
    return input and True or False


@stat_check("top level object")
def _top_level_object(input):
    return f"{input.schema_name()}.{input.schema_version()}"


@stat_check("number of tracks")
def _num_tracks(input):
    try:
        return len(input.tracks)
    except AttributeError:
        return 0


@stat_check("Tracks are the same length")
def _equal_length_tracks(tl):
    if not tl.tracks:
        return True
    for i, track in enumerate(tl.tracks):
        if track.duration() != tl.tracks[0].duration():
            raise RuntimeError(
                "track {} is not the same duration as the other tracks."
                " Track {} duration, vs: {}".format(
                    i,
                    track.duration(),
                    tl.tracks[0].duration()
                )
            )
    return True


@stat_check("deepest nesting")
def _deepest_nesting(input):
    def depth(parent):
        if not isinstance(parent, otio.core.Composition):
            return 1
        d = 0
        for child in parent:
            d = max(d, depth(child) + 1)
        return d
    if isinstance(input, otio.schema.Timeline):
        return depth(input.tracks) + 1
    else:
        return depth(input)


@stat_check("number of clips")
def _num_clips(input):
    return len(list(input.find_clips()))


@stat_check("total duration")
def _total_duration(input):
    try:
        return input.tracks.duration()
    except AttributeError:
        return "n/a"


@stat_check("total duration in timecode")
def _total_duration_timecode(input):
    try:
        d = input.tracks.duration()
        return otio.opentime.to_timecode(d, d.rate)
    except AttributeError:
        return "n/a"


@stat_check("top level rate")
def _top_level_rate(input):
    try:
        return input.tracks.duration().rate
    except AttributeError:
        return "n/a"


@stat_check("clips with cdl data")
def _clips_with_cdl_data(input):
    return len(list(c for c in input.find_clips() if 'cdl' in c.metadata))


@stat_check("Tracks with non standard types")
def _sequences_with_non_standard_types(input):
    return len(
        list(
            c
            for c in input.find_children(descended_from_type=otio.schema.Track)
            if c.kind not in (otio.schema.TrackKind.__dict__)
        )
    )


def _stat_otio(input_otio):
    for (test, testfunc) in TESTS:
        try:
            print(f"{test}: {testfunc(input_otio)}")
        except (otio.exceptions.OTIOError) as e:
            sys.stderr.write(
                "There was an OTIO Error: "
                " {}\n".format(e),
            )
            continue
        except (Exception) as e:
            sys.stderr.write(f"There was a system error: {e}\n")
            continue


def main():
    """  main entry point  """
    args = _parsed_args()

    for fp in args.filepath:
        try:
            parsed_otio = otio.adapters.read_from_file(fp)
        except (otio.exceptions.OTIOError) as e:
            sys.stderr.write(
                "The file did not successfully parse, with error:"
                " {}\n".format(e),
            )
            continue
        except (Exception) as e:
            sys.stderr.write(f"There was a system error: {e}\n")
            continue

        _stat_otio(parsed_otio)


if __name__ == '__main__':
    main()
