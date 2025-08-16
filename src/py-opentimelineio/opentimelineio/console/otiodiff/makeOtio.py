import opentimelineio as otio
import copy
from .clipData import ClipData

def sortClips(trackClips):
    """Sort ClipDatas based on start time on the timeline"""
    # sort by clip start time in timeline
    return sorted(trackClips, key=lambda clipData: clipData.timeline_range.start_time.value)

def addRavenColor(clip, color):
    """Add color of clip to metadata of raven so clips are correctly color-coded in raven viewer.
    Specific to raven only."""

    # parses name of color from otio.core.Color and puts into format that raven can read
    color = color.name.upper()

    # TODO: if raven not in metadata, add empty dict

    if "raven" in clip.metadata:
        clip.metadata["raven"]["color"] = color
    else:
        colorData = {"color" : color}
        clip.metadata["raven"] = colorData
    
    return clip

def addMarker(newClip, color, clipData):
    """Add marker of specified color and name to clip"""
    newMarker = otio.schema.Marker()
    newMarker.marked_range = clipData.source_range
    
    # parses name of color from otio.core.Color and puts into format that markers can read
    colorName = color.name.upper()
    newMarker.color = colorName

    if(colorName == "GREEN"):
        newMarker.name = "added"
    elif(colorName == "PINK"):
        newMarker.name = "deleted"

    if isinstance(clipData, ClipData) and clipData.note is not None:
        # print("edit note added")
        newMarker.name = clipData.note

    newClip.markers.append(newMarker)

    return newClip

def makeSeparaterTrack(trackType):
    """Make empty track that separates the timeline A tracks from the timeline B tracks"""
    return otio.schema.Track(name="=====================", kind=trackType)

def makeTrack(trackName, trackKind, trackClips, clipColor=None, markersOn=False):
    """Make OTIO track from ClipDatas with option to add markers and color to all clips on track"""
    # make new blank track with name of kind 
    # print("make track of kind: ", trackKind)
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

            if(delta > 0):
                gapDur = otio.opentime.RationalTime(delta, tlRate)
                gap = otio.schema.Gap(duration = gapDur)
                track.append(gap)

                currentEnd = tlStart + tlDuration
                # print("new end: ", currentEnd)
            else:
                currentEnd += tlDuration

            # add clip to track
            newClip = copy.deepcopy(clipData.source_clip)
            if clipColor is not None:
                #testing
                newClip = addRavenColor(newClip, clipColor)
                newClip.color = clipColor

            # TODO: move out of if and make clipColor optional with default color
                if markersOn:
                    newClip = addMarker(newClip, clipColor, clipData)
            track.append(newClip)

    return track

def makeTrackB(clipGroup, trackNum, trackKind):
    """Make an annotated track from timeline B. Shows added and edited clips as well as 
    clips that have moved between tracks."""
    tAdd = makeTrack("added", trackKind, clipGroup.add, otio.core.Color.GREEN)
    tEdited = makeTrack("edited", trackKind, clipGroup.edit, otio.core.Color.ORANGE, markersOn=True)
    tSame = makeTrack("same", trackKind, clipGroup.same)
    tMoved = makeTrack("moved", trackKind, clipGroup.move, otio.core.Color.PURPLE, markersOn=True)

    flatB = otio.core.flatten_stack([tSame, tEdited, tAdd, tMoved])
    if trackKind == otio.schema.Track.Kind.Video:
        flatB.name = "Video B" + str(trackNum)
    elif trackKind == otio.schema.Track.Kind.Audio:
        flatB.name = "Audio B" + str(trackNum)

    flatB.kind = trackKind

    return flatB

def makeTrackA(clipGroup, trackNum, trackKind):
    """Make an annotated track from timeline A. Shows deleted clips and the original clips
    corresponding to clips edited in timeline B."""
    tSame = makeTrack("same", trackKind, clipGroup.same)
    # grab the original pair from all the edit clipDatas
    
    prevEdited = []
    prevMoved = []
    for e in clipGroup.edit:
        prevEdited.append(e.matched_clipData)
    tEdited = makeTrack("edited", trackKind, prevEdited, otio.core.Color.ORANGE) 

    tDel = makeTrack("deleted", trackKind, clipGroup.delete, otio.core.Color.PINK)

    # TODO: explain the make sep then merge flatten tracks thing
    flatA = otio.core.flatten_stack([tSame, tEdited, tDel])

    # TODO: change video to directly use trackKind
    if trackKind == otio.schema.Track.Kind.Video:
        flatA.name = "Video A" + str(trackNum)
    elif trackKind == otio.schema.Track.Kind.Audio:
        flatA.name = "Audio A" + str(trackNum)
    
    flatA.kind = trackKind

    return flatA