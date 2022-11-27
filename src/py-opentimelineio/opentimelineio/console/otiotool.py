#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""otiotool is a multipurpose command line tool for inspecting,
modifying, combining, and splitting OTIO files.

Each of the many operations it can perform is provided by a
small, simple utility function. These functions also serve
as concise examples of how OTIO can be used to perform common
workflow tasks."""

import argparse
import os
import pathlib
import re
import sys

from urllib.request import urlopen

from copy import deepcopy

import opentimelineio as otio


def main():
    """otiotool main program.
    This function is resposible for executing the steps specified
    by all of the command line arguments in the right order.
    """

    args = parse_arguments()

    # Phase 1: Input...

    # Most of this function will operate on this list of timelines.
    # Often there will be just one, but this tool in general enough
    # to operate on several. This is essential when the --stack or
    # --concatenate arguments are used.
    timelines = read_inputs(args.input)

    # Phase 2: Filter (remove stuff)...

    if args.video_only:
        for timeline in timelines:
            keep_only_video_tracks(timeline)

    if args.audio_only:
        for timeline in timelines:
            keep_only_audio_tracks(timeline)

    if args.remove_transitions:
        timelines = filter_transitions(timelines)

    if args.only_tracks_with_name or args.only_tracks_with_index:
        timelines = filter_tracks(
            args.only_tracks_with_name,
            args.only_tracks_with_index,
            timelines
        )

    if args.only_clips_with_name or args.only_clips_with_name_regex:
        timelines = filter_clips(
            args.only_clips_with_name,
            args.only_clips_with_name_regex,
            timelines
        )

    if args.trim:
        for timeline in timelines:
            trim_timeline(args.trim[0], args.trim[1], timeline)

    # Phase 3: Combine timelines

    if args.stack:
        timelines = [stack_timelines(timelines)]

    if args.concat:
        timelines = [concatenate_timelines(timelines)]

    # Phase 4: Combine (or add) tracks

    if args.flatten:
        for timeline in timelines:
            flatten_timeline(
                timeline,
                which_tracks=args.flatten,
                keep=args.keep_flattened_tracks
            )

    # Phase 5: Relinking media

    if args.relink_by_name:
        for timeline in timelines:
            for folder in args.relink_by_name:
                relink_by_name(timeline, folder)

    if args.copy_media_to_folder:
        for timeline in timelines:
            copy_media_to_folder(timeline, args.copy_media_to_folder)

    # Phase 6: Redaction

    if args.redact:
        for timeline in timelines:
            redact_timeline(timeline)

    # Phase 7: Inspection

    if args.stats:
        for timeline in timelines:
            print_timeline_stats(timeline)

    if args.inspect:
        for timeline in timelines:
            inspect_timelines(args.inspect, timeline)

    should_summarize = (args.list_clips or
                        args.list_media or
                        args.verify_media or
                        args.list_tracks or
                        args.list_markers)
    if should_summarize:
        for timeline in timelines:
            summarize_timeline(
                args.list_tracks,
                args.list_clips,
                args.list_media,
                args.verify_media,
                args.list_markers,
                timeline)

    # Final Phase: Output

    if args.output:
        # Gather all of the timelines under one OTIO object
        # in preparation for final output
        if len(timelines) > 1:
            output = otio.schema.SerializableCollection()
            output.extend(timelines)
        else:
            output = timelines[0]

        write_output(args.output, output)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="""
otiotool = a multi-purpose command line utility for working with OpenTimelineIO.

This tool works in phases, as follows:
1. Input
    Input files provided by the "--input <filename>" argument(s) are read into
    memory. Files may be OTIO format, or any format supported by adapter
    plugins.

2. Filtering
    Options such as --video-only, --audio-only, --only-tracks-with-name,
    -only-tracks-with-index, --only-clips-with-name,
    --only-clips-with-name-regex, --remove-transitions, and --trim will remove
    content. Only the tracks, clips, etc. that pass all of the filtering options
    provided are passed to the next phase.

3. Combine
    If specified, the --stack, --concat, and --flatten operations are
    performed (in that order) to combine all of the input timeline(s) into one.

4. Relink
    The --relink-by-name option, will scan the specified folder(s) looking for
    files which match the name of each clip in the input timeline(s).
    If matching files are found, clips will be relinked to those files (using
    file:// URLs). Clip names are matched to filenames ignoring file extension.
    If specified, the --copy-media-to-folder option, will copy or download
    all linked media, and relink the OTIO to reference the local copies.

5. Redact
    If specified, the --redact option, will remove all metadata and rename all
    objects in the OTIO with generic names (e.g. "Track 1", "Clip 17", etc.)

6. Inspect
    Options such as --stats, --list-clips, --list-tracks, --list-media,
    --verify-media, --list-markers, and --inspect will examine the OTIO and
    print information to standard output.

7. Output
    Finally, if the "--output <filename>" option is specified, the resulting
    OTIO will be written to the specified file. The extension of the output
    filename is used to determine the format of the output (e.g. OTIO or any
    format supported by the adapter plugins.)
""".strip(),
        epilog="""Examples:

Combine multiple files into one, by joining them end-to-end:
otiotool -i titles.otio -i feature.otio -i credits.otio --concat -o full.otio

Layer multiple files on top of each other in a stack:
otiotool -i background.otio -i foreground.otio --stack -o composite.otio

Verify that all referenced media files are accessible:
otiotool -i playlist.otio --verify-media

Inspect specific audio clips in detail:
otiotool -i playlist.otio --only-audio --list-tracks --inspect "Interview"
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Input...
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        nargs='+',
        required=True,
        metavar='PATH(s)',
        help="""Input file path(s). All formats supported by adapter plugins
        are supported. Use '-' to read OTIO from standard input."""
    )

    # Filter...
    parser.add_argument(
        "-v",
        "--video-only",
        action='store_true',
        help="Output only video tracks"
    )
    parser.add_argument(
        "-a",
        "--audio-only",
        action='store_true',
        help="Output only audio tracks"
    )
    parser.add_argument(
        "--only-tracks-with-name",
        type=str,
        nargs='+',
        metavar='NAME(s)',
        help="Output tracks with these name(s)"
    )
    parser.add_argument(
        "--only-tracks-with-index",
        type=int,
        nargs='+',
        metavar='INDEX(es)',
        help="Output tracks with these indexes"
        " (1 based, in same order as --list-tracks)"
    )
    parser.add_argument(
        "--only-clips-with-name",
        type=str,
        nargs='+',
        metavar='NAME(s)',
        help="Output only clips with these name(s)"
    )
    parser.add_argument(
        "--only-clips-with-name-regex",
        type=str,
        nargs='+',
        metavar='REGEX(es)',
        help="Output only clips with names matching the given regex"
    )
    parser.add_argument(
        "--remove-transitions",
        action='store_true',
        help="Remove all transitions"
    )
    parser.add_argument(
        "-t",
        "--trim",
        type=str,
        nargs=2,
        metavar=('START', 'END'),
        help="Trim from <start> to <end> as HH:MM:SS:FF timecode or seconds"
    )

    # Combine...
    parser.add_argument(
        "-f",
        "--flatten",
        choices=['video', 'audio', 'all'],
        metavar='TYPE',
        help="Flatten multiple tracks into one."
    )
    parser.add_argument(
        "--keep-flattened-tracks",
        action='store_true',
        help="""When used with --flatten, the new flat track is added above the
        others instead of replacing them."""
    )
    parser.add_argument(
        "-s",
        "--stack",
        action='store_true',
        help="Stack multiple input files into one timeline"
    )
    parser.add_argument(
        "-c",
        "--concat",
        action='store_true',
        help="Concatenate multiple input files end-to-end into one timeline"
    )

    # Relink
    parser.add_argument(
        "--relink-by-name",
        type=str,
        nargs='+',
        metavar='FOLDER(s)',
        help="""Scan the specified folder looking for filenames which match
        each clip's name. If found, clips are relinked to those files."""
    )
    parser.add_argument(
        "--copy-media-to-folder",
        type=str,
        metavar='FOLDER',
        help="""Copy or download all linked media to the specified folder and
        relink all media references to the copies"""
    )

    # Redact
    parser.add_argument(
        "--redact",
        action='store_true',
        help="""Remove all metadata, names, etc. leaving only the timeline
        structure"""
    )

    # Inspect...
    parser.add_argument(
        "--stats",
        action='store_true',
        help="""List statistics about the result, including start, end, and
        duration"""
    )
    parser.add_argument(
        "--list-clips",
        action='store_true',
        help="List each clip's name"
    )
    parser.add_argument(
        "--list-tracks",
        action='store_true',
        help="List each track's name"
    )
    parser.add_argument(
        "--list-media",
        action='store_true',
        help="List each referenced media URL"
    )
    parser.add_argument(
        "--verify-media",
        action='store_true',
        help="""Verify that each referenced media URL exists (for local media
        only)"""
    )
    parser.add_argument(
        "--list-markers",
        action='store_true',
        help="List summary of all markers"
    )
    parser.add_argument(
        "--inspect",
        type=str,
        nargs='+',
        metavar='NAME(s)',
        help="Inspect details of clips with names matching the given regex"
    )

    # Output...
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        metavar='PATH',
        help="""Output file. All formats supported by adapter plugins
        are supported. Use '-' to write OTIO to standard output."""
    )

    args = parser.parse_args()

    # Some options cannot be combined.

    if args.video_only and args.audio_only:
        parser.error("Cannot use --video-only and --audio-only at the same time.")

    if args.stack and args.concat:
        parser.error("Cannot use --stack and --concat at the same time.")

    if args.keep_flattened_tracks and not args.flatten:
        parser.error("Cannot use --keep-flattened-tracks without also using --flatten.")

    return args


def read_inputs(input_paths):
    """Read one or more timlines from the list of file paths given.
    If a file path is '-' then a timeline is read from stdin.
    """
    timelines = []
    for input_path in input_paths:
        if input_path == '-':
            text = sys.stdin.read()
            timeline = otio.adapters.read_from_string(text, 'otio_json')
        else:
            timeline = otio.adapters.read_from_file(input_path)
        timelines.append(timeline)
    return timelines


def keep_only_video_tracks(timeline):
    """Remove all tracks except for video tracks from a timeline."""
    timeline.tracks[:] = timeline.video_tracks()


def keep_only_audio_tracks(timeline):
    """Remove all tracks except for audio tracks from a timeline."""
    timeline.tracks[:] = timeline.audio_tracks()


def filter_transitions(timelines):
    """Return a copy of the input timelines with all transitions removed.
    The overall duration of the timelines should not be affected."""
    def _f(item):
        if isinstance(item, otio.schema.Transition):
            return None
        return item
    return [otio.algorithms.filtered_composition(t, _f) for t in timelines]


def _filter(item, names, patterns):
    """This is a helper function that returns the input item if
    its name matches the list of names given (if any), or matches any of the
    patterns given (if any). If the item's name does not match any of the
    given names or patterns, then None is returned."""
    if names and item.name in names:
        return item
    if patterns:
        for pattern in patterns:
            if re.search(pattern, item.name):
                return item
    return None

    # TODO: Should this return a same-duration Gap instead?
    # gap = otio.schema.Gap(source_range=item.trimmed_range())
    # return gap


def filter_tracks(only_tracks_with_name, only_tracks_with_index, timelines):
    """Return a copy of the input timelines with only tracks that match
    either the list of names given, or the list of track indexes given."""

    # Use a variable saved within this function so that the closure
    # below can modify it.
    # See: https://stackoverflow.com/questions/21959985/why-cant-python-increment-variable-in-closure   # noqa: E501
    filter_tracks.index = 0

    def _f(item):
        if not isinstance(item, otio.schema.Track):
            return item
        filter_tracks.index = filter_tracks.index + 1
        if only_tracks_with_index and filter_tracks.index not in only_tracks_with_index:
            return None
        if only_tracks_with_name and item.name not in only_tracks_with_name:
            return None
        return item

    return [otio.algorithms.filtered_composition(t, _f) for t in timelines]


def filter_clips(only_clips_with_name, only_clips_with_name_regex, timelines):
    """Return a copy of the input timelines with only clips with names
    that match either the given list of names, or regular expression patterns."""

    def _f(item):
        if not isinstance(item, otio.schema.Clip):
            return item
        return _filter(item, only_clips_with_name, only_clips_with_name_regex)

    return [otio.algorithms.filtered_composition(t, _f) for t in timelines]


def stack_timelines(timelines):
    """Return a single timeline with all of the tracks from all of the input
    timelines stacked on top of each other. The resulting timeline should be
    as long as the longest input timeline."""
    name = f"Stacked {len(timelines)} Timelines"
    stacked_timeline = otio.schema.Timeline(name)
    for timeline in timelines:
        stacked_timeline.tracks.extend(deepcopy(timeline.tracks[:]))
    return stacked_timeline


def concatenate_timelines(timelines):
    """Return a single timeline with all of the input timelines concatenated
    end-to-end. The resulting timeline should be as long as the sum of the
    durations of the input timelines."""
    name = f"Concatenated {len(timelines)} Timelines"
    concatenated_track = otio.schema.Track()
    for timeline in timelines:
        concatenated_track.append(deepcopy(timeline.tracks))
    concatenated_timeline = otio.schema.Timeline(
        name=name,
        tracks=[concatenated_track]
    )
    return concatenated_timeline


def flatten_timeline(timeline, which_tracks='video', keep=False):
    """Replace the tracks of this timeline with a single track by flattening.
    If which_tracks is specified, you may choose 'video', 'audio', or 'all'.
    If keep is True, then the old tracks are retained and the new one is added
    above them instead of replacing them. This can be useful to see and
    understand how flattening works."""

    # Make two lists: tracks_to_flatten and other_tracks
    # Note: that we take care to NOT assume that there are only two kinds
    # of tracks.
    if which_tracks == 'all':
        tracks_to_flatten = timeline.tracks
        other_tracks = []
        kind = tracks_to_flatten[0].kind
    elif which_tracks == 'video':
        tracks_to_flatten = timeline.video_tracks()
        other_tracks = [t for t in timeline.tracks if t not in tracks_to_flatten]
        kind = otio.schema.TrackKind.Video
    elif which_tracks == 'audio':
        tracks_to_flatten = timeline.audio_tracks()
        other_tracks = [t for t in timeline.tracks if t not in tracks_to_flatten]
        kind = otio.schema.TrackKind.Audio
    else:
        raise ValueError(
            "Invalid choice {} for which_tracks argument"
            " to flatten_timeline.".format(which_tracks)
        )

    flat_track = otio.algorithms.flatten_stack(tracks_to_flatten[:])
    flat_track.kind = kind

    if keep:
        timeline.tracks.append(flat_track)
    else:
        timeline.tracks[:] = other_tracks + [flat_track]


def time_from_string(text, rate):
    """This helper function turns a string into a RationalTime. It accepts
    either a timecode string (e.g. "HH:MM:SS:FF") or a string with a floating
    point value measured in seconds. The second argument to this function
    specifies the rate for the returned RationalTime."""
    if ":" in text:
        return otio.opentime.from_timecode(text, rate)
    else:
        return otio.opentime.from_seconds(float(text), rate)


def trim_timeline(start, end, timeline):
    """Return a copy of the input timeline trimmed to the start and end
    times given. Each of the start and end times can be specified as either
    a timecode string (e.g. "HH:MM:SS:FF") or a string with a floating
    point value measured in seconds."""
    if timeline.global_start_time is not None:
        rate = timeline.global_start_time.rate
    else:
        rate = timeline.duration().rate
    try:
        start_time = time_from_string(start, rate)
        end_time = time_from_string(end, rate)
    except Exception:
        raise ValueError("Start and end arguments to --trim must be "
                         "either HH:MM:SS:FF or a floating point number of"
                         " seconds, not '{}' and '{}'".format(start, end))
    trim_range = otio.opentime.range_from_start_end_time(start_time, end_time)
    timeline.tracks[:] = [
        otio.algorithms.track_trimmed_to_range(t, trim_range)
        for t in timeline.tracks
    ]


# Used only within _counter() to keep track of object indexes
__counters = {}


def _counter(name):
    """This is a helper function for returning redacted names, based on a name."""
    counter = __counters.get(name, 0)
    counter += 1
    __counters[name] = counter
    return counter


def redact_timeline(timeline):
    """Remove all metadata, names, or other identifying information from this
    timeline. Only the structure, schema and timing will remain."""

    counter = _counter(timeline.schema_name())
    timeline.name = f"{timeline.schema_name()} #{counter}"
    timeline.metadata.clear()

    for child in [timeline.tracks] + list(timeline.all_children()):
        counter = _counter(child.schema_name())
        child.name = f"{child.schema_name()} #{counter}"
        child.metadata.clear()
        if hasattr(child, 'markers'):
            for marker in child.markers:
                counter = _counter(marker.schema_name())
                marker.name = f"{marker.schema_name()} #{counter}"
                marker.metadata.clear()
        if hasattr(child, 'effects'):
            for effect in child.effects:
                counter = _counter(effect.schema_name())
                effect.name = f"{effect.schema_name()} #{counter}"
                effect.metadata.clear()
        if hasattr(child, 'media_reference'):
            media_reference = child.media_reference
            if media_reference:
                counter = _counter(media_reference.schema_name())
                has_target_url = hasattr(media_reference, 'target_url')
                if has_target_url and media_reference.target_url:
                    media_reference.target_url = f"URL #{counter}"
                media_reference.metadata.clear()


def copy_media(url, destination_path):
    if url.startswith("/"):
        print(f"COPYING: {url}")
        data = open(url, "rb").read()
    else:
        print(f"DOWNLOADING: {url}")
        data = urlopen(url).read()
    open(destination_path, "wb").write(data)
    return destination_path


def relink_by_name(timeline, path):
    """Relink clips in the timeline to media files discovered at the
    given folder path."""

    def _conform_path(p):
        # Turn absolute paths into file:// URIs
        if os.path.isabs(p):
            return pathlib.Path(p).as_uri()
        else:
            # Leave relative paths as-is
            return p

    count = 0
    if os.path.isdir(path):
        name_to_url = dict([
            (
                os.path.splitext(x)[0],
                _conform_path(os.path.join(path, x))
            )
            for x in os.listdir(path)
        ])
    elif os.path.isfile(path):
        print((f"ERROR: Cannot relink to '{path}':"
               " Please specify a folder instead of a file."))
        return
    else:
        print(f"ERROR: Cannot relink to '{path}': No such file or folder.")
        return

    for clip in timeline.each_clip():
        url = name_to_url.get(clip.name)
        if url is not None:
            clip.media_reference = otio.schema.ExternalReference(target_url=url)
            count += 1

    print(f"Relinked {count} clips to files in folder {path}")


def copy_media_to_folder(timeline, folder):
    """Copy or download all referenced media to this folder, and relink media
    references to the copies."""

    # @TODO: Add an option to allow mkdir
    # if not os.path.exists(folder):
    #     os.mkdir(folder)

    copied_files = set()
    for clip in timeline.all_clips():
        media_reference = clip.media_reference
        has_actual_url = (media_reference and
                          hasattr(media_reference, 'target_url') and
                          media_reference.target_url)
        if has_actual_url:
            source_url = media_reference.target_url
            filename = os.path.basename(source_url)
            # @TODO: This is prone to name collisions if the basename is not unique
            # We probably need to hash the url, or turn the whole url into a filename.
            destination_path = os.path.join(folder, filename)
            already_copied_this = destination_path in copied_files
            file_exists = os.path.exists(destination_path)
            if already_copied_this:
                media_reference.target_url = destination_path
            else:
                if file_exists:
                    print(
                        "WARNING: Relinking clip {} to existing file"
                        " (instead of overwriting it): {}".format(
                            clip.name, destination_path
                        )
                    )
                    media_reference.target_url = destination_path
                    already_copied_this.add(destination_path)
                else:
                    try:
                        copy_media(source_url, destination_path)
                        media_reference.target_url = destination_path
                        already_copied_this.add(destination_path)
                    except Exception as ex:
                        print(f"ERROR: Problem copying/downloading media {ex}")
                        # don't relink this one, since the copy failed


def print_timeline_stats(timeline):
    """Print some statistics about the given timeline."""
    print(f"Name: {timeline.name}")
    trimmed_range = timeline.tracks.trimmed_range()
    print("Start:    {}\nEnd:      {}\nDuration: {}".format(
        otio.opentime.to_timecode(trimmed_range.start_time),
        otio.opentime.to_timecode(trimmed_range.end_time_exclusive()),
        otio.opentime.to_timecode(trimmed_range.duration),
    ))


def inspect_timelines(name_regex, timeline):
    """Print some detailed information about the item(s) in the timeline with names
    that match the given regular expression."""
    print("TIMELINE:", timeline.name)
    items_to_inspect = [_filter(item, [], name_regex)
                        for item in timeline.all_children()]
    items_to_inspect = list(filter(None, items_to_inspect))
    for item in items_to_inspect:
        print(f"  ITEM: {item.name} ({type(item)})")
        print("    source_range:", item.source_range)
        print("    trimmed_range:", item.trimmed_range())
        print("    visible_range:", item.visible_range())
        try:
            print("    available_range:", item.available_range())
        except Exception:
            pass
        print("    range_in_parent:", item.range_in_parent())
        print(
            "    trimmed range in timeline:",
            item.transformed_time_range(
                item.trimmed_range(), timeline.tracks
            )
        )
        print(
            "    visible range in timeline:",
            item.transformed_time_range(
                item.visible_range(), timeline.tracks
            )
        )
        ancestor = item.parent()
        while ancestor is not None:
            print(
                "    range in {} ({}): {}".format(
                    ancestor.name,
                    type(ancestor),
                    item.transformed_time_range(item.trimmed_range(), ancestor)
                )
            )
            ancestor = ancestor.parent()


def summarize_timeline(list_tracks, list_clips, list_media, verify_media,
                       list_markers, timeline):
    """Print a summary of a timeline, optionally listing the tracks, clips, media,
    and/or markers inside it."""
    print("TIMELINE:", timeline.name)
    for child in [timeline.tracks] + list(timeline.all_children()):
        if isinstance(child, otio.schema.Track):
            if list_tracks:
                print(f"TRACK: {child.name} ({child.kind})")
        if isinstance(child, otio.schema.Clip):
            if list_clips:
                print("  CLIP:", child.name)
            if list_media or verify_media:
                try:
                    url = child.media_reference.target_url
                except Exception:
                    url = None
                detail = ""
                if verify_media and url:
                    if os.path.exists(url):
                        detail = " EXISTS"
                    else:
                        detail = " NOT FOUND"
                print(f"    MEDIA{detail}: {url}")

        if list_markers and hasattr(child, 'markers'):
            top_level = child
            while top_level.parent() is not None:
                top_level = top_level.parent()
            for marker in child.markers:
                template = "  MARKER: global: {} local: {} duration: {} color: {} name: {}"  # noqa: E501
                print(template.format(
                    otio.opentime.to_timecode(child.transformed_time(
                        marker.marked_range.start_time,
                        top_level)),
                    otio.opentime.to_timecode(marker.marked_range.start_time),
                    marker.marked_range.duration.value,
                    marker.color,
                    marker.name
                ))


def write_output(output_path, output):
    """Write the given OTIO object to a file path. If the file path given is
    the string '-' then the output is written to stdout instead."""
    if output_path == '-':
        result = otio.adapters.write_to_string(output)
        print(result)
    else:
        otio.adapters.write_to_file(output, output_path)


if __name__ == '__main__':
    main()
