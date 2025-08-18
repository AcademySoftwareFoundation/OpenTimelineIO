import opentimelineio as otio
import copy
from .clipData import ClipData
from opentimelineio.core import Color

# color-coding for clips in output timeline
addedClipsColor = Color.GREEN
editedClipsColor = Color.ORANGE
deletedClipsColor = Color.PINK
movedClipsColor = Color.PURPLE


def sortClips(trackClips):
    """Sort ClipDatas based on start time on the timeline"""
    return sorted(trackClips,
                  key=lambda clipData: clipData.timeline_range.start_time.value)


def addRavenColor(clip, color):
    """Add color of clip to metadata of raven so clips are correctly
    color-coded in raven viewer. Specific to raven only."""
    # parses name of color from otio.core.Color and puts into
    # format that raven can read
    color = color.name.upper()

    if "raven" not in clip.metadata:
        clip.metadata["raven"] = {"color": None}
    clip.metadata["raven"]["color"] = color

    return clip


def addMarker(newClip, clipData, color=None):
    """Add marker of specified color and name to clip"""
    newMarker = otio.schema.Marker()
    newMarker.marked_range = clipData.source_range

    # parses name of color from otio.core.Color and puts into
    # format that markers can read
    if color is not None:
        colorName = color.name.upper()
        newMarker.color = colorName

    if isinstance(clipData, ClipData) and clipData.note is not None:
        newMarker.name = clipData.note

    newClip.markers.append(newMarker)

    return newClip

# TODO: make variables for add, edit, delete, move colors?


def makeSeparaterTrack(trackType):
    """Make empty track that separates the timeline A tracks
    from the timeline B tracks"""
    return otio.schema.Track(name="=====================", kind=trackType)


def makeTrack(trackName, trackKind, trackClips, clipColor=None, markersOn=False):
    """Make OTIO track from ClipDatas with option to add markers
    and color to all clips on track"""
    # make new blank track with name and kind from parameters
    track = otio.schema.Track(name=trackName, kind=trackKind)

    # sort clips by start time in timeline
    sortedClips = sortClips(trackClips)

    currentEnd = 0
    # add clip to timeline
    for clipData in sortedClips:
        if clipData is not None:
            # add gap if necessary
            tlStart = clipData.timeline_range.start_time.value
            tlDuration = clipData.timeline_range.duration.value
            tlRate = clipData.timeline_range.start_time.rate

            delta = tlStart - currentEnd

            if (delta > 0):
                gapDur = otio.opentime.RationalTime(delta, tlRate)
                gap = otio.schema.Gap(duration=gapDur)
                track.append(gap)

                currentEnd = tlStart + tlDuration
                # print("new end: ", currentEnd)
            else:
                currentEnd += tlDuration

            # add clip to track
            newClip = copy.deepcopy(clipData.source_clip)
            if clipColor is not None:
                # testing
                newClip = addRavenColor(newClip, clipColor)
                newClip.color = clipColor

            if markersOn:
                newClip = addMarker(newClip, clipData, clipColor)
            track.append(newClip)

    return track


def makeTrackB(clipGroup, trackNum, trackKind):
    """Make an annotated track from timeline B. Shows added and edited clips
    as well as clips that have moved between tracks.

    Algorithm makes individual tracks for each clip category the track contains,
    then flattens them to form the final track. Since blanks are left in all of
    the individual tracks, flattening should allow all clips to simply
    slot down into place on the flattened track

    Ex. track 1 has added and unchanged clips
    Algorithm steps:
    1) Make a track containing only the unchanged clips of track 1
    2) Make another track containing only the added clips of track 1 and color
    them green
    3) Flatten the added clips track on top of the unchanged clips track to
    create a track containing both
    """

    # for each category of clips, make an indivdual track and color code accordingly
    tSame = makeTrack("same", trackKind, clipGroup.same)
    tAdd = makeTrack("added", trackKind, clipGroup.add, addedClipsColor)
    tEdited = makeTrack("edited", trackKind, clipGroup.edit,
                        editedClipsColor, markersOn=True)
    tMoved = makeTrack("moved", trackKind, clipGroup.move,
                       movedClipsColor, markersOn=True)

    # put all the tracks into a list and flatten them down to a single track
    # that contains all the color-coded clips

    flatB = otio.core.flatten_stack([tSame, tEdited, tAdd, tMoved])

    # update track name and kind
    if trackKind == otio.schema.Track.Kind.Video:
        flatB.name = trackKind + " B" + str(trackNum)
    elif trackKind == otio.schema.Track.Kind.Audio:
        flatB.name = trackKind + " B" + str(trackNum)
    flatB.kind = trackKind

    return flatB


def makeTrackA(clipGroup, trackNum, trackKind):
    """Make an annotated track from timeline A. Shows deleted clips and the original clips
    corresponding to clips edited in timeline B.

    Algorithm makes individual tracks for each clip category the track contains,
    then flattens them to form the final track. Since blanks are left in all of
    the individual tracks, flattening should allow all clips to simmply slot down
    into place on the flattened track

    Ex. track 1 has deleted and unchanged clips
    Algorithm steps:
    1) Make a track containing only the unchanged clips of track 1
    2) Make another track containing only the deleted clips of track 1 and color
    them red
    3) Flatten the deleted clips track on top of the unchanged clips track
    to create a track containing both
    """

    # for each category of clips, make an indivdual track and color code accordingly
    tSame = makeTrack("same", trackKind, clipGroup.same)
    # grab the original pair from all the edit clipDatas
    prevEdited = []
    for e in clipGroup.edit:
        prevEdited.append(e.matched_clipData)
    tEdited = makeTrack("edited", trackKind, prevEdited, editedClipsColor)
    tDel = makeTrack("deleted", trackKind, clipGroup.delete, deletedClipsColor)

    # put all the tracks into a list and flatten them down to a single track
    # that contains all the color-coded clips
    flatA = otio.core.flatten_stack([tSame, tEdited, tDel])

    # update track name and kind
    if trackKind == otio.schema.Track.Kind.Video:
        flatA.name = trackKind + " A" + str(trackNum)
    elif trackKind == otio.schema.Track.Kind.Audio:
        flatA.name = trackKind + " A" + str(trackNum)
    flatA.kind = trackKind

    return flatA
