# MIT License
#
# Copyright (c) 2018 Daniel Flehner Heen (Storm Studios)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import hiero.core
import hiero.ui

try:
    from urllib import unquote

except ImportError:
    from urllib.parse import unquote  # lint:ok

import opentimelineio as otio


def get_transition_type(otio_item, otio_track):
    _in, _out = otio_track.neighbors_of(otio_item)

    if isinstance(_in, otio.schema.Gap):
        _in = None

    if isinstance(_out, otio.schema.Gap):
        _out = None

    if _in and _out:
        return 'dissolve'

    elif _in and not _out:
        return 'fade_out'

    elif not _in and _out:
        return 'fade_in'

    else:
        return 'unknown'


def find_trackitem(name, hiero_track):
    for item in hiero_track.items():
        if item.name() == name:
            return item

    return None


def get_neighboring_trackitems(otio_item, otio_track, hiero_track):
    _in, _out = otio_track.neighbors_of(otio_item)
    trackitem_in = None
    trackitem_out = None

    if _in:
        trackitem_in = find_trackitem(_in.name, hiero_track)

    if _out:
        trackitem_out = find_trackitem(_out.name, hiero_track)

    return trackitem_in, trackitem_out


def apply_transition(otio_track, otio_item, track):
    # Figure out type of transition
    transition_type = get_transition_type(otio_item, otio_track)

    # Figure out track kind for getattr below
    if isinstance(track, hiero.core.VideoTrack):
        kind = ''

    else:
        kind = 'Audio'

    try:
        # Gather TrackItems involved in trasition
        item_in, item_out = get_neighboring_trackitems(
            otio_item,
            otio_track,
            track
        )

        # Create transition object
        if transition_type == 'dissolve':
            transition_func = getattr(
                hiero.core.Transition,
                'create{kind}DissolveTransition'.format(kind=kind)
            )

            transition = transition_func(
                item_in,
                item_out,
                otio_item.in_offset.value,
                otio_item.out_offset.value
            )

        elif transition_type == 'fade_in':
            transition_func = getattr(
                hiero.core.Transition,
                'create{kind}FadeInTransition'.format(kind=kind)
            )
            transition = transition_func(
                item_out,
                otio_item.out_offset.value
            )

        elif transition_type == 'fade_out':
            transition_func = getattr(
                hiero.core.Transition,
                'create{kind}FadeOutTransition'.format(kind=kind)
            )
            transition = transition_func(
                item_in,
                otio_item.in_offset.value
            )

        else:
            # Unknown transition
            return

        # Apply transition to track
        track.addTransition(transition)

    except Exception, e:
        sys.stderr.write(
            'Unable to apply transition "{t}": "{e}"\n'.format(
                t=otio_item,
                e=e
            )
        )


def prep_url(url_in):
    url = unquote(url_in)

    if url.startswith('file://localhost/'):
        return url

    url = 'file://localhost{sep}{url}'.format(
        sep=url.startswith(os.sep) and '' or os.sep,
        url=url.startswith(os.sep) and url[1:] or url
    )

    return url


def create_offline_mediasource(otio_clip, path=None):
    hiero_rate = hiero.core.TimeBase(
        otio_clip.source_range.start_time.rate
    )

    if isinstance(otio_clip.media_reference, otio.schema.ExternalReference):
        source_range = otio_clip.available_range()

    else:
        source_range = otio_clip.source_range

    if path is None:
        path = otio_clip.name

    media = hiero.core.MediaSource.createOfflineVideoMediaSource(
        prep_url(path),
        source_range.start_time.value,
        source_range.duration.value,
        hiero_rate,
        source_range.start_time.value
    )

    return media


def load_otio(otio_file):
    otio_timeline = otio.adapters.read_from_file(otio_file)
    build_sequence(otio_timeline)


marker_color_map = {
    "PINK": "Magenta",
    "RED": "Red",
    "ORANGE": "Yellow",
    "YELLOW": "Yellow",
    "GREEN": "Green",
    "CYAN": "Cyan",
    "BLUE": "Blue",
    "PURPLE": "Magenta",
    "MAGENTA": "Magenta",
    "BLACK": "Blue",
    "WHITE": "Green"
}


def get_tag(tagname, tagsbin):
    for tag in tagsbin.items():
        if tag.name() == tagname:
            return tag

        if isinstance(tag, hiero.core.Bin):
            tag = get_tag(tagname, tag)

            if tag is not None:
                return tag

    return None


def add_metadata(metadata, hiero_item):
    for key, value in metadata.items():
        if isinstance(value, dict):
            add_metadata(value, hiero_item)
            continue

        if value is not None:
            if not key.startswith('tag.'):
                key = 'tag.' + key

            hiero_item.metadata().setValue(key, str(value))


def add_markers(otio_item, hiero_item, tagsbin):
    if isinstance(otio_item, (otio.schema.Stack, otio.schema.Clip)):
        markers = otio_item.markers

    elif isinstance(otio_item, otio.schema.Timeline):
        markers = otio_item.tracks.markers

    else:
        markers = []

    for marker in markers:
        marker_color = marker.color

        _tag = get_tag(marker.name, tagsbin)
        if _tag is None:
            _tag = get_tag(marker_color_map[marker_color], tagsbin)

        if _tag is None:
            _tag = hiero.core.Tag(marker_color_map[marker.color])

        start = marker.marked_range.start_time.value
        end = (
            marker.marked_range.start_time.value +
            marker.marked_range.duration.value
        )

        tag = hiero_item.addTagToRange(_tag, start, end)
        tag.setName(marker.name or marker_color_map[marker_color])

        # Add metadata
        add_metadata(marker.metadata, tag)


def create_track(otio_track, tracknum, track_kind):
    # Add track kind when dealing with nested stacks
    if isinstance(otio_track, otio.schema.Stack):
        otio_track.kind = track_kind

    # Create a Track
    if otio_track.kind == otio.schema.TrackKind.Video:
        track = hiero.core.VideoTrack(
            otio_track.name or 'Video{n}'.format(n=tracknum)
        )

    else:
        track = hiero.core.AudioTrack(
            otio_track.name or 'Audio{n}'.format(n=tracknum)
        )

    return track


def create_clip(otio_clip, tagsbin):
    # Create MediaSource
    otio_media = otio_clip.media_reference
    if isinstance(otio_media, otio.schema.ExternalReference):
        url = prep_url(otio_media.target_url)
        media = hiero.core.MediaSource(url)
        if media.isOffline():
            media = create_offline_mediasource(otio_clip, url)

    else:
        media = create_offline_mediasource(otio_clip)

    # Create Clip
    clip = hiero.core.Clip(media)

    # Add markers
    add_markers(otio_clip, clip, tagsbin)

    return clip


def create_trackitem(playhead, track, otio_clip, clip):
    source_range = otio_clip.source_range

    trackitem = track.createTrackItem(otio_clip.name)
    trackitem.setPlaybackSpeed(source_range.start_time.rate)
    trackitem.setSource(clip)

    # Check for speed effects and adjust playback speed accordingly
    for effect in otio_clip.effects:
        if isinstance(effect, otio.schema.LinearTimeWarp):
            trackitem.setPlaybackSpeed(
                trackitem.playbackSpeed() *
                effect.time_scalar
            )

    # If reverse playback speed swap source in and out
    if trackitem.playbackSpeed() < 0:
        source_out = source_range.start_time.value
        source_in = (
            source_range.start_time.value +
            source_range.duration.value
        ) - 1
        timeline_in = playhead + source_out
        timeline_out = (
            timeline_in +
            source_range.duration.value
        ) - 1
    else:
        # Normal playback speed
        source_in = source_range.start_time.value
        source_out = (
            source_range.start_time.value +
            source_range.duration.value
        ) - 1
        timeline_in = playhead
        timeline_out = (
            timeline_in +
            source_range.duration.value
        ) - 1

    # Set source and timeline in/out points
    trackitem.setSourceIn(source_in)
    trackitem.setSourceOut(source_out)
    trackitem.setTimelineIn(timeline_in)
    trackitem.setTimelineOut(timeline_out)

    return trackitem


def build_sequence(otio_timeline, project=None, track_kind=None):
    if project is None:
        # TODO: Find a proper way for active project
        project = hiero.core.projects(hiero.core.Project.kUserProjects)[-1]

    # Create a Sequence
    sequence = hiero.core.Sequence(otio_timeline.name or 'OTIOSequence')

    # Create a Bin to hold clips
    projectbin = project.clipsBin()
    projectbin.addItem(hiero.core.BinItem(sequence))
    sequencebin = hiero.core.Bin(sequence.name())
    projectbin.addItem(sequencebin)

    # Get tagsBin
    tagsbin = hiero.core.project("Tag Presets").tagsBin()

    # Add timeline markers
    add_markers(otio_timeline, sequence, tagsbin)

    # TODO: Set sequence settings from otio timeline if available
    if isinstance(otio_timeline, otio.schema.Timeline):
        tracks = otio_timeline.tracks

    else:
        # otio.schema.Stack
        tracks = otio_timeline

    for tracknum, otio_track in enumerate(tracks):
        playhead = 0
        _transitions = []

        # Add track to sequence
        track = create_track(otio_track, tracknum, track_kind)
        sequence.addTrack(track)

        # iterate over items in track
        for itemnum, otio_clip in enumerate(otio_track):
            if isinstance(otio_clip, otio.schema.Stack):
                bar = hiero.ui.mainWindow().statusBar()
                bar.showMessage(
                    'Nested sequences are created separately.',
                    timeout=3000
                )
                build_sequence(otio_clip, project, otio_track.kind)

            elif isinstance(otio_clip, otio.schema.Clip):
                # Create a Clip
                clip = create_clip(otio_clip, tagsbin)

                # Add Clip to a Bin
                sequencebin.addItem(hiero.core.BinItem(clip))

                # Create TrackItem
                trackitem = create_trackitem(
                    playhead,
                    track,
                    otio_clip,
                    clip
                )

                # Add trackitem to track
                track.addTrackItem(trackitem)

                # Update playhead
                playhead = trackitem.timelineOut() + 1

            elif isinstance(otio_clip, otio.schema.Transition):
                # Store transitions for when all clips in the track are created
                _transitions.append((otio_track, otio_clip))

            elif isinstance(otio_clip, otio.schema.Gap):
                # Hiero has no fillers, slugs or blanks at the moment
                playhead += otio_clip.source_range.duration.value

        # Apply transitions we stored earlier now that all clips are present
        for otio_track, otio_item in _transitions:
            apply_transition(otio_track, otio_item, track)
