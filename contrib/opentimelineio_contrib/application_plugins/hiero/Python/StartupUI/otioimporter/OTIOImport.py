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


import os
import hiero.core
import hiero.ui

import PySide2.QtWidgets as qw

try:
    from urllib import unquote

except ImportError:
    from urllib.parse import unquote  # lint:ok

import opentimelineio as otio


def inform(messages):
    if isinstance(messages, type('')):
        messages = [messages]

    qw.QMessageBox.information(
        hiero.ui.mainWindow(),
        'OTIO Import',
        '\n'.join(messages),
        qw.QMessageBox.StandardButton.Ok
    )


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


def find_trackitem(otio_clip, hiero_track):
    for item in hiero_track.items():
        if item.timelineIn() == otio_clip.range_in_parent().start_time.value:
            if item.name() == otio_clip.name:
                return item

    return None


def get_neighboring_trackitems(otio_item, otio_track, hiero_track):
    _in, _out = otio_track.neighbors_of(otio_item)
    trackitem_in = None
    trackitem_out = None

    if _in:
        trackitem_in = find_trackitem(_in, hiero_track)

    if _out:
        trackitem_out = find_trackitem(_out, hiero_track)

    return trackitem_in, trackitem_out


def apply_transition(otio_track, otio_item, track):
    warning = None

    # Figure out type of transition
    transition_type = get_transition_type(otio_item, otio_track)

    # Figure out track kind for getattr below
    kind = ''
    if isinstance(track, hiero.core.AudioTrack):
        kind = 'Audio'

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

        try:
            transition = transition_func(
                item_in,
                item_out,
                otio_item.in_offset.value,
                otio_item.out_offset.value
            )

        # Catch error raised if transition is bigger than TrackItem source
        except RuntimeError as e:
            transition = None
            warning = \
                'Unable to apply transition "{t.name}": {e} ' \
                'Ignoring the transition.' \
                .format(t=otio_item, e=e.message)

    elif transition_type == 'fade_in':
        transition_func = getattr(
            hiero.core.Transition,
            'create{kind}FadeInTransition'.format(kind=kind)
        )

        # Warn user if part of fade is outside of clip
        if otio_item.in_offset.value:
            warning = \
                'Fist half of transition "{t.name}" is outside of clip and ' \
                'not valid in Hiero. Only applied second half.' \
                .format(t=otio_item)

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

        # Warn user if part of fade is outside of clip
        if otio_item.out_offset.value:
            warning = \
                'Second half of transition "{t.name}" is outside of clip ' \
                'and not valid in Hiero. Only applied first half.' \
                .format(t=otio_item)

    else:
        # Unknown transition
        return

    # Apply transition to track
    if transition:
        track.addTransition(transition)

    # Inform user about missing or adjusted transitions
    return warning


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

    legal_media_refs = (
        otio.schema.ExternalReference,
        otio.schema.ImageSequenceReference
    )
    if isinstance(otio_clip.media_reference, legal_media_refs):
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


def load_otio(otio_file, project=None, sequence=None):
    otio_timeline = otio.adapters.read_from_file(otio_file)
    build_sequence(otio_timeline, project=project, sequence=sequence)


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
    for key, value in metadata.get('Hiero', dict()).items():
        if key == 'source_type':
            # Only used internally to reassign tag to correct Hiero item
            continue

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
        meta = marker.metadata.get('Hiero', dict())
        if 'source_type' in meta:
            if hiero_item.__class__.__name__ != meta.get('source_type'):
                continue

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

        if hasattr(hiero_item, 'addTagToRange'):
            tag = hiero_item.addTagToRange(_tag, start, end)

        else:
            tag = hiero_item.addTag(_tag)

        tag.setName(marker.name or marker_color_map[marker_color])
        # tag.setNote(meta.get('tag.note', ''))

        # Add metadata
        add_metadata(marker.metadata, tag)


def create_track(otio_track, tracknum, track_kind):
    if track_kind is None and hasattr(otio_track, 'kind'):
        track_kind = otio_track.kind

    # Create a Track
    if track_kind == otio.schema.TrackKind.Video:
        track = hiero.core.VideoTrack(
            otio_track.name or 'Video{n}'.format(n=tracknum)
        )

    else:
        track = hiero.core.AudioTrack(
            otio_track.name or 'Audio{n}'.format(n=tracknum)
        )

    return track


def create_clip(otio_clip, tagsbin, sequencebin):
    # Create MediaSource
    url = None
    media = None
    otio_media = otio_clip.media_reference

    if isinstance(otio_media, otio.schema.ExternalReference):
        url = prep_url(otio_media.target_url)
        media = hiero.core.MediaSource(url)

    elif isinstance(otio_media, otio.schema.ImageSequenceReference):
        url = prep_url(otio_media.abstract_target_url('#'))
        media = hiero.core.MediaSource(url)

    if media is None or media.isOffline():
        media = create_offline_mediasource(otio_clip, url)

    # Reuse previous clip if possible
    clip = None
    for item in sequencebin.clips():
        if item.activeItem().mediaSource() == media:
            clip = item.activeItem()
            break

    if not clip:
        # Create new Clip
        clip = hiero.core.Clip(media)

        # Add Clip to a Bin
        sequencebin.addItem(hiero.core.BinItem(clip))

    # Add markers
    add_markers(otio_clip, clip, tagsbin)

    return clip


def create_trackitem(playhead, track, otio_clip, clip):
    source_range = otio_clip.source_range

    trackitem = track.createTrackItem(otio_clip.name)
    trackitem.setPlaybackSpeed(source_range.start_time.rate)
    trackitem.setSource(clip)

    time_scalar = 1.

    # Check for speed effects and adjust playback speed accordingly
    for effect in otio_clip.effects:
        if isinstance(effect, otio.schema.LinearTimeWarp):
            time_scalar = effect.time_scalar
            # Only reverse effect can be applied here
            if abs(time_scalar) == 1.:
                trackitem.setPlaybackSpeed(trackitem.playbackSpeed() * time_scalar)

        elif isinstance(effect, otio.schema.FreezeFrame):
            # For freeze frame, playback speed must be set after range
            time_scalar = 0.

    # If reverse playback speed swap source in and out
    if trackitem.playbackSpeed() < 0:
        source_out = source_range.start_time.value
        source_in = source_range.end_time_inclusive().value

        timeline_in = playhead + source_out
        timeline_out = (
            timeline_in +
            source_range.duration.value
        ) - 1
    else:
        # Normal playback speed
        source_in = source_range.start_time.value
        source_out = source_range.end_time_inclusive().value

        timeline_in = playhead
        timeline_out = (
            timeline_in +
            source_range.duration.value
        ) - 1

    # Set source and timeline in/out points
    trackitem.setTimes(
        timeline_in,
        timeline_out,
        source_in,
        source_out

    )

    # Apply playback speed for freeze frames
    if abs(time_scalar) != 1.:
        trackitem.setPlaybackSpeed(trackitem.playbackSpeed() * time_scalar)

    # Link audio to video when possible
    if isinstance(track, hiero.core.AudioTrack):
        for other in track.parent().trackItemsAt(playhead):
            if other.source() == clip:
                trackitem.link(other)

    return trackitem


def build_sequence(otio_timeline, project=None, sequence=None, track_kind=None):
    if project is None:
        if sequence:
            project = sequence.project()

        else:
            # Per version 12.1v2 there is no way of getting active project
            project = hiero.core.projects(hiero.core.Project.kUserProjects)[-1]

    projectbin = project.clipsBin()

    if not sequence:
        # Create a Sequence
        sequence = hiero.core.Sequence(otio_timeline.name or 'OTIOSequence')

        # Set sequence settings from otio timeline if available
        if hasattr(otio_timeline, 'global_start_time'):
            if otio_timeline.global_start_time:
                start_time = otio_timeline.global_start_time
                sequence.setFramerate(start_time.rate)
                sequence.setTimecodeStart(start_time.value)

        # Create a Bin to hold clips
        projectbin.addItem(hiero.core.BinItem(sequence))

        sequencebin = hiero.core.Bin(sequence.name())
        projectbin.addItem(sequencebin)

    else:
        sequencebin = projectbin

    # Get tagsBin
    tagsbin = hiero.core.project("Tag Presets").tagsBin()

    # Add timeline markers
    add_markers(otio_timeline, sequence, tagsbin)

    if isinstance(otio_timeline, otio.schema.Timeline):
        tracks = otio_timeline.tracks

    else:
        tracks = [otio_timeline]

    for tracknum, otio_track in enumerate(tracks):
        playhead = 0
        _transitions = []

        # Add track to sequence
        track = create_track(otio_track, tracknum, track_kind)
        sequence.addTrack(track)

        # iterate over items in track
        for itemnum, otio_clip in enumerate(otio_track):
            if isinstance(otio_clip, (otio.schema.Track, otio.schema.Stack)):
                inform('Nested sequences/tracks are created separately.')

                # Add gap where the nested sequence would have been
                playhead += otio_clip.source_range.duration.value

                # Process nested sequence
                build_sequence(
                    otio_clip,
                    project=project,
                    track_kind=otio_track.kind
                )

            elif isinstance(otio_clip, otio.schema.Clip):
                # Create a Clip
                clip = create_clip(otio_clip, tagsbin, sequencebin)

                # Create TrackItem
                trackitem = create_trackitem(
                    playhead,
                    track,
                    otio_clip,
                    clip
                )

                # Add markers
                add_markers(otio_clip, trackitem, tagsbin)

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
        warnings = list()
        for otio_track, otio_item in _transitions:
            # Catch warnings form transitions in case of unsupported transitions
            warning = apply_transition(otio_track, otio_item, track)
            if warning:
                warnings.append(warning)

        if warnings:
            inform(warnings)
