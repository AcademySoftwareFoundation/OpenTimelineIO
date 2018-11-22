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

import opentimelineio as otio


def get_transition_type(otio_item, otio_track):
    _in, _out = otio_track.neighbors_of(otio_item)

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


def prep_url(url):
    if url.startswith('file://localhost/'):
        return url

    url = 'file://localhost{sep}{url}'.format(
        sep=url.startswith(os.sep) and '' or os.sep,
        url=url.startswith(os.sep) and url[1:] or url
        )

    return url


def create_offline_mediasource(otio_clip):
    media = hiero.core.MediaSource.createOfflineVideoMediaSource(
        prep_url(otio_clip.name),
        otio_clip.source_range.start_time.value,
        otio_clip.source_range.duration.value,
        hiero.core.TimeBase(
            otio_clip.source_range.start_time.rate
            )
        )

    return media


def load_otio(otio_file):
    otio_timeline = otio.adapters.read_from_file(otio_file)
    build_sequence(otio_timeline)


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

    # TODO: Set sequence settings from otio timeline if available
    if isinstance(otio_timeline, otio.schema.Timeline):
        tracks = otio_timeline.tracks

    else:
        # otio.schema.Stack
        tracks = [otio_timeline]

    for tracknum, otio_track in enumerate(tracks):
        playhead = 0
        _transitions = []

        # Fallback when dealing with nested stacks
        videotrack = False
        if isinstance(otio_track, otio.schema.Stack):
            videotrack = track_kind == 'Video'

        # Create a Track
        if videotrack or otio_track.kind == otio.schema.TrackKind.Video:
            track = hiero.core.VideoTrack(
                            otio_track.name or 'Video{n}'.format(n=tracknum)
                            )

        else:
            track = hiero.core.AudioTrack(
                            otio_track.name or 'Audio{n}'.format(n=tracknum)
                            )

        # Add track to sequence
        sequence.addTrack(track)

        # iterate over items in track
        for itemnum, otio_clip in enumerate(otio_track):
            if isinstance(otio_clip, otio.schema.Stack):
                build_sequence(otio_clip, project, otio_track.kind)

            elif isinstance(otio_clip, otio.schema.Clip):
                source_range = otio_clip.source_range

                # Create TrackItem
                trackitem = track.createTrackItem(otio_clip.name)
                trackitem.setPlaybackSpeed(source_range.start_time.rate)

                # Create MediaSource
                otio_media = otio_clip.media_reference
                if isinstance(otio_media, otio.schema.ExternalReference):
                    url = prep_url(otio_media.target_url)
                    media = hiero.core.MediaSource(url)

                else:
                    media = create_offline_mediasource(otio_clip)

                # Create Clip
                clip = hiero.core.Clip(media)
                sequencebin.addItem(hiero.core.BinItem(clip))

                # Attach clip to TrackItem
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
                    #TODO look at duration on these
                    source_out = source_range.start_time.value
                    source_in = (
                        source_range.start_time.value +
                        source_range.duration.value
                        )
                    timeline_in = playhead + source_out
                    timeline_out = (
                        timeline_in +
                        source_range.duration.value
                        )
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

                # Add trackitem to track
                track.addTrackItem(trackitem)

                # Update playhead
                playhead = timeline_out + 1

            elif isinstance(otio_clip, otio.schema.Transition):
                # Store transitions for when all clips in the track are created
                _transitions.append((otio_track, otio_clip))

            elif isinstance(otio_clip, otio.schema.Gap):
                # Hiero has no fillers, slugs or blanks at the moment
                playhead += otio_clip.source_range.duration.value

        # Apply transitions we stored earlier now that all clips are present
        for otio_track, otio_item in _transitions:
            apply_transition(otio_track, otio_item, track)
