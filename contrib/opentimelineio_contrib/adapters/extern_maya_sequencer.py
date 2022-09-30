# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import os
import sys

import urllib.parse

# import maya and handle standalone mode
from maya import cmds

try:
    cmds.ls
except AttributeError:
    from maya import standalone
    standalone.initialize(name='python')

import opentimelineio as otio

# Mapping of Maya FPS Enum to rate.
FPS = {
    'game': 15,
    'film': 24,
    'pal': 25,
    'ntsc': 30,
    'show': 48,
    'palf': 50,
    'ntscf': 60
}


def _url_to_path(url):
    if url is None:
        return None

    return urllib.parse.urlparse(url).path


def _video_url_for_shot(shot):
    current_file = os.path.normpath(cmds.file(q=True, sn=True))
    return os.path.join(
        os.path.dirname(current_file),
        'playblasts',
        '{base_name}_{shot_name}.mov'.format(
            base_name=os.path.basename(os.path.splitext(current_file)[0]),
            shot_name=cmds.shot(shot, q=True, shotName=True)
        )
    )


def _match_existing_shot(item, existing_shots):
    if existing_shots is None:
        return None

    if item.media_reference.is_missing_reference:
        return None

    url_path = _url_to_path(item.media_reference.target_url)
    return next(
        (
            shot for shot in existing_shots
            if _video_url_for_shot(shot) == url_path
        ),
        None
    )


# ------------------------
# building single track
# ------------------------

def _build_shot(item, track_no, track_range, existing_shot=None):
    camera = None
    if existing_shot is None:
        camera = cmds.camera(name=item.name.split('.')[0] + '_cam')[0]
    cmds.shot(
        existing_shot or item.name.split('.')[0],
        e=existing_shot is not None,
        shotName=item.name,
        track=track_no,
        currentCamera=camera,
        startTime=item.trimmed_range().start_time.value,
        endTime=item.trimmed_range().end_time_inclusive().value,
        sequenceStartTime=track_range.start_time.value,
        sequenceEndTime=track_range.end_time_inclusive().value
    )


def _build_track(track, track_no, existing_shots=None):
    for n, item in enumerate(track):
        if not isinstance(item, otio.schema.Clip):
            continue

        track_range = track.range_of_child_at_index(n)
        if existing_shots is not None:
            existing_shot = _match_existing_shot(item, existing_shots)
        else:
            existing_shot = None

        _build_shot(item, track_no, track_range, existing_shot)


def build_sequence(timeline, clean=False):
    existing_shots = cmds.ls(type='shot') or []
    if clean:
        cmds.delete(existing_shots)
        existing_shots = []

    tracks = [
        track for track in timeline.tracks
        if track.kind == otio.schema.TrackKind.Video
    ]

    for track_no, track in enumerate(reversed(tracks)):
        _build_track(track, track_no, existing_shots=existing_shots)


def read_from_file(path, clean=True):
    timeline = otio.adapters.read_from_file(path)
    build_sequence(timeline, clean=clean)


# -----------------------
# parsing single track
# -----------------------

def _get_gap(duration):
    rate = FPS.get(cmds.currentUnit(q=True, time=True), 25)
    gap_range = otio.opentime.TimeRange(
        duration=otio.opentime.RationalTime(duration, rate)
    )
    return otio.schema.Gap(source_range=gap_range)


def _read_shot(shot):
    rate = FPS.get(cmds.currentUnit(q=True, time=True), 25)
    start = int(cmds.shot(shot, q=True, startTime=True))
    end = int(cmds.shot(shot, q=True, endTime=True)) + 1

    video_reference = otio.schema.ExternalReference(
        target_url=_video_url_for_shot(shot),
        available_range=otio.opentime.TimeRange(
            otio.opentime.RationalTime(value=start, rate=rate),
            otio.opentime.RationalTime(value=end - start, rate=rate)
        )
    )

    return otio.schema.Clip(
        name=cmds.shot(shot, q=True, shotName=True),
        media_reference=video_reference,
        source_range=otio.opentime.TimeRange(
            otio.opentime.RationalTime(value=start, rate=rate),
            otio.opentime.RationalTime(value=end - start, rate=rate)
        )
    )


def _read_track(shots):
    v = otio.schema.Track(kind=otio.schema.track.TrackKind.Video)

    last_clip_end = 0
    for shot in shots:
        seq_start = int(cmds.shot(shot, q=True, sequenceStartTime=True))
        seq_end = int(cmds.shot(shot, q=True, sequenceEndTime=True))

        # add gap if necessary
        fill_time = seq_start - last_clip_end
        last_clip_end = seq_end + 1
        if fill_time:
            v.append(_get_gap(fill_time))

        # add clip
        v.append(_read_shot(shot))

    return v


def read_sequence():
    rate = FPS.get(cmds.currentUnit(q=True, time=True), 25)
    shots = cmds.ls(type='shot') or []
    per_track = {}

    for shot in shots:
        track_no = cmds.shot(shot, q=True, track=True)
        if track_no not in per_track:
            per_track[track_no] = []
        per_track[track_no].append(shot)

    timeline = otio.schema.Timeline()
    timeline.global_start_time = otio.opentime.RationalTime(0, rate)

    for track_no in reversed(sorted(per_track.keys())):
        track_shots = per_track[track_no]
        timeline.tracks.append(_read_track(track_shots))

    return timeline


def write_to_file(path):
    timeline = read_sequence()
    otio.adapters.write_to_file(timeline, path)


def main():
    read_write_arg = sys.argv[1]
    filepath = sys.argv[2]

    write = False
    if read_write_arg == "write":
        write = True

    if write:
        # read the input OTIO off stdin
        input_otio = otio.adapters.read_from_string(
            sys.stdin.read(),
            'otio_json'
        )
        build_sequence(input_otio, clean=True)
        cmds.file(rename=filepath)
        cmds.file(save=True, type="mayaAscii")
    else:
        cmds.file(filepath, o=True)
        sys.stdout.write(
            "\nOTIO_JSON_BEGIN\n" +
            otio.adapters.write_to_string(
                read_sequence(),
                "otio_json"
            ) +
            "\nOTIO_JSON_END\n"
        )

    cmds.quit(force=True)


if __name__ == "__main__":
    main()
