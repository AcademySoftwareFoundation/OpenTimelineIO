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

import hiero.core
import hiero.ui

import opentimelineio as otio


def get_transition_type(otio_item):
    _in = otio_item.in_offset.value
    _out = otio_item.out_offset.value

    if _in and _out:
        return 'dissolve'

    elif _in and not _out:
        return 'fade_out'

    elif not _in and _out:
        return 'fade_in'

    else:
        return 'unknown'


def apply_transition(otio_item, clip_index, track):
    # Figure out type of transition
    transition_type = get_transition_type(otio_item)

    # Figure out track kind for getattr below
    if isinstance(track, hiero.core.VideoTrack):
        kind = ''

    else:
        kind = 'Audio'

    # Create transition object
    if transition_type == 'dissolve':
        item_in = track.items()[clip_index]
        item_out = track.items()[clip_index + 1]
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
        item = track.items()[clip_index]
        transition_func = getattr(
                    hiero.core.Transition,
                    'create{kind}FadeInTransition'.format(kind=kind)
                    )
        transition = transition_func(
                                item,
                                otio_item.out_offset.value
                                )

    elif transition_type == 'fade_out':
        item = track.items()[clip_index]
        transition_func = getattr(
                    hiero.core.Transition,
                    'create{kind}FadeOutTransition'.format(kind=kind)
                    )
        transition = transition_func(
                                item,
                                otio_item.in_offset.value
                                )

    # Apply transition to track
    track.addTransition(transition)


def build_sequence(otio_file):
    otio_timeline = otio.adapters.read_from_file(otio_file)
    # TODO: Find a proper way for active project
    project = hiero.core.projects(hiero.core.Project.kUserProjects)[-1]

    # Create a Bin to hold clips
    clipsbin = project.clipsBin()

    # Create a Sequence
    sequence = hiero.core.Sequence(otio_timeline.name or 'OTIOSequence')
    clipsbin.addItem(hiero.core.BinItem(sequence))

    # TODO: Set sequence settings from otio timeline if available

    for tracknum, otio_track in enumerate(otio_timeline.tracks):
        playhead = 0
        _transitions = []

        if otio_track.kind == otio.schema.TrackKind.Video:
            track = hiero.core.VideoTrack(
                            otio_track.name or 'Video{n}'.format(n=tracknum)
                            )

        else:
            track = hiero.core.AudioTrack(
                            otio_track.name or 'Audio{n}'.format(n=tracknum)
                            )

        # Add track to sequence
        sequence.addTrack(track)

        clipcount = -1
        # iterate over items in track
        for itemnum, otio_clip in enumerate(otio_track):
            if isinstance(otio_clip, otio.schema.Clip):
                # Create MediaSource
                source_range = otio_clip.source_range
                otio_media = otio_clip.media_reference

                if isinstance(otio_media, otio.schema.ExternalReference):
                    url = otio_media.target_url

                else:
                    url = ''

                media = hiero.core.MediaSource(url)

                # Create Clip
                clip = hiero.core.Clip(media)
                clipsbin.addItem(hiero.core.BinItem(clip))

                # Create TrackItem
                trackitem = track.createTrackItem(otio_clip.name)

                # Check for speed effects and adjust playback speed accordingly
                for effect in otio_clip.effects:
                    if isinstance(effect, otio.schema.LinearTimeWarp):
                        trackitem.setPlaybackSpeed(
                                                trackitem.playbackSpeed() *
                                                effect.time_scalar
                                                )

                # Attach clip to TrackItem
                trackitem.setSource(clip)

                # If reverse playback speed swap source in and out
                if trackitem.playbackSpeed() < 0:
                    source_out = source_range.start_time.value
                    source_in = (
                            source_range.start_time.value +
                            source_range.duration.value - 1
                            )
                    timeline_in = playhead + source_out
                    timeline_out = (
                                timeline_in +
                                source_range.duration.value - 1
                                )
                else:
                    # Normal playback speed
                    source_in = source_range.start_time.value
                    source_out = (
                            source_range.start_time.value +
                            source_range.duration.value - 1
                            )
                    timeline_in = playhead + source_in
                    timeline_out = (
                                timeline_in +
                                source_range.duration.value - 1
                                )

                # Set source and timeline in/out points
                trackitem.setSourceIn(source_in)
                trackitem.setSourceOut(source_out)
                trackitem.setTimelineIn(timeline_in)
                trackitem.setTimelineOut(timeline_out)

                # Add clip to track
                track.addTrackItem(trackitem)

                # Update playhead
                playhead = timeline_out

                # Update clipcount
                clipcount += 1

            elif isinstance(otio_clip, otio.schema.Transition):
                # Avoid negative index
                clip_index = clipcount and clipcount - 1 or clipcount

                # Store transitions for when all clips in the track are created
                _transitions.append((otio_clip, clip_index))

            elif isinstance(otio_clip, otio.schema.Gap):
                # Hiero has no fillers, slugs or blanks at the moment
                playhead += otio_clip.source_range.duration.value

        # Apply transitions we stored earlier now that all clips are present
        for otio_item, clip_index in _transitions:
            apply_transition(otio_item, clip_index, track)
