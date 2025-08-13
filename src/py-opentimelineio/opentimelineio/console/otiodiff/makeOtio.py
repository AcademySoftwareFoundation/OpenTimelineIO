import opentimelineio as otio
import copy
from .clipData import ClipData

# for debugging, put response into file
def toJson(file):
    with open("clipDebug.json", "w") as f:
        f.write(file)

def toTimeline(tracks, timeline=None):
    tl = timeline

    if tl is None:
        tl = otio.schema.Timeline(name="timeline")

    for t in tracks:
        tl.tracks.append(t)
    
    return tl

def toOtio(file):
    otio.adapters.write_to_file(file, "display.otio")

# input is list of clipDatas, sorts them by start time on the timeline
def sortClips(trackClips):
    # sort by clip start time in timeline
    return sorted(trackClips, key=lambda clipData: clipData.timeline_range.start_time.value)

# @params: clip: otio clip
def addRavenColor(clip, color):
    # print(clip.metadata)

    if "raven" in clip.metadata:
        clip.metadata["raven"]["color"] = color.upper()
    else:
        colorData = {"color" : color.upper()}
        clip.metadata["raven"] = colorData
    
    # debug
    # toJson(otio.adapters.write_to_string(clip.metadata))
    return clip

def addMarker(newClip, color, clipData):
    newMarker = otio.schema.Marker()
    newMarker.marked_range = clipData.source_range
    color = color.upper()
    newMarker.color = color

    if isinstance(clipData, ClipData) and clipData.note is not None:
        # print("edit note added")
        newMarker.name = clipData.note

    if(color == "GREEN"):
        newMarker.name = "added"
    elif(color == "PINK"):
        newMarker.name = "deleted"

    newClip.markers.append(newMarker)

    return newClip

# make new blank track that acts as a separator between the A and B sections
def makeEmptyTrack(trackType):
    return otio.schema.Track(name="=====================", kind=trackType)

def makeTrack(trackName, trackKind, trackClips, clipColor=None, markersOn=False):
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
            newClip = copy.deepcopy(clipData.source)
            if clipColor is not None:
                newClip = addRavenColor(newClip, clipColor)
                if markersOn:
                    newClip = addMarker(newClip, clipColor, clipData)
            track.append(newClip)

    return track

# make tracks from timeline B
def makeTrackB(clipGroup, trackNum, trackKind):
    tAddV = makeTrack("added", trackKind, clipGroup.add, "GREEN")
    tEditedV = makeTrack("edited", trackKind, clipGroup.edit, "ORANGE", markersOn=True)
    tSameV = makeTrack("same", trackKind, clipGroup.same)
    tMovedV = makeTrack("moved", trackKind, clipGroup.move, "PURPLE", markersOn=True)

    flatB = otio.core.flatten_stack([tSameV, tEditedV, tAddV, tMovedV])
    if trackKind == "Video":
        flatB.name = "Video B" + str(trackNum)
    elif trackKind == "Audio":
        flatB.name = "Audio B" + str(trackNum)

    flatB.kind = trackKind

    return flatB

# make tracks from timeline A
def makeTrackA(clipGroup, trackNum, trackKind):
    tSameV = makeTrack("same", trackKind, clipGroup.same)
    # grab the original pair from all the edit clipDatas
    
    prevEdited = []
    prevMoved = []
    for e in clipGroup.edit:
        prevEdited.append(e.pair)
    tEditedV = makeTrack("edited", trackKind, prevEdited, "ORANGE") 

    tDelV = makeTrack("deleted", trackKind, clipGroup.delete, "PINK")

    flatA = otio.core.flatten_stack([tSameV, tEditedV, tDelV])
    if trackKind == "Video":
        flatA.name = "Video A" + str(trackNum)
    elif trackKind == "Audio":
        flatA.name = "Audio A" + str(trackNum)
    
    flatA.kind = trackKind

    return flatA

# def colorMovedA(tl, clipDB):
#     # maybe make an extract all add/edit/move, etc from clipDB
#     movedClips = []
#     for track in clipDB.keys():
#         movedClips.extend(clipDB[track]["move"])

#     for m in movedClips:
#         movedA = m.pair
#         track = movedA.track_num

#         # find clip in new track that was created
#         currentTrack = tl.tracks[track]
#         clips = currentTrack.find_clips()
#         if movedA.source in clips:
#             print("found corresponding clip")
#         # clipToColor = clips.index(movedA.source)

#         # print(clipToColor.name)
    
#     # tMovedV = makeTrack("moved", trackKind, prevMoved, "PURPLE",  markersOn=True)

def makeTimelineOfType(tlType, trackA, trackB, videoGroup, audioGroup=None):
    newTl = None

    if tlType == "stack":
        newTl = makeTimelineStack(trackA, trackB, videoGroup, audioGroup)
    elif tlType == "inline":
        newTl = makeTimelineInline(trackA, trackB, videoGroup, audioGroup)
    elif tlType == "full":
        newTl = makeTimelineFull(trackA, trackB, videoGroup, audioGroup)
    elif tlType == "simple":
        newTl = makeTimelineSimple(trackA, trackB, videoGroup, audioGroup)
    else:
        print("not a valid display type")
    return newTl

def makeTimelineStack(trackA, trackB, videoGroup, audioGroup=None):
    # create new timeline with groups separated out into individual tracks
    tl = otio.schema.Timeline(name="timeline")

    # append two original tracks
    trackA.name = "Track A" + trackA.name
    trackB.name = "Track B" + trackB.name
    tl.tracks.append(copy.deepcopy(trackA))
    tl.tracks.append(copy.deepcopy(trackB))

    tAddV = makeTrack("added", "Video", videoGroup.add, "GREEN")
    tEditedV = makeTrack("edited", "Video", videoGroup.edit, "ORANGE")
    tSameV = makeTrack("same", "Video", videoGroup.same)
    tDelV = makeTrack("deleted", "Video", videoGroup.delete, "RED")

    # append video tracks to timeline
    tl.tracks.append(tDelV)
    tl.tracks.append(tSameV)
    tl.tracks.append(tEditedV)
    tl.tracks.append(tAddV)

    # add audio tracks if present
    if audioGroup is not None:
        tAddA = makeTrack("added", "Audio", audioGroup.add, "GREEN")
        tEditedA = makeTrack("edited", "Audio", audioGroup.edit, "ORANGE")
        tSameA = makeTrack("same", "Audio", audioGroup.same)
        tDelA = makeTrack("deleted", "Audio", audioGroup.delete, "RED")

        # append video tracks to timeline
        tl.tracks.append(tAddA)
        tl.tracks.append(tEditedA)
        tl.tracks.append(tSameA)
        tl.tracks.append(tDelA)

    return tl

# note: flatten_stack doesn't work when there's transitions
def makeTimelineInline(trackA, trackB, clipGroup, audioGroup=None):
    tl = otio.schema.Timeline(name="timeline")

    tAddV = makeTrack("added", "Video", clipGroup.add, "GREEN")
    tEditedV = makeTrack("edited", "Video", clipGroup.edit, "ORANGE")
    tSameV = makeTrack("same", "Video", clipGroup.same)
    tDelV = makeTrack("deleted", "Video", clipGroup.delete, "RED")

    flat_videoA = otio.core.flatten_stack([copy.deepcopy(trackA), tDelV])
    flat_videoA.name = "VideoA"
    tl.tracks.append(flat_videoA)

    flat_videoB = otio.core.flatten_stack([tSameV, tEditedV, tAddV])
    flat_videoB.name = "VideoB"
    tl.tracks.append(flat_videoB)

    # add audio tracks if present
    if audioGroup is not None:
        tAddA = makeTrack("added", "Audio", audioGroup.add, "GREEN")
        tEditedA = makeTrack("edited", "Audio", audioGroup.edit, "ORANGE")
        tSameA = makeTrack("same", "Audio", audioGroup.same)
        tDelA = makeTrack("deleted", "Audio", audioGroup.delete, "RED")

        flat_audioA = otio.core.flatten_stack([tSameA, tDelA])
        flat_audioB = otio.core.flatten_stack([tSameA, tEditedA, tAddA])

        flat_audioA.name = "AudioA"
        flat_audioB.name = "AudioB"
        flat_audioA.kind = "Audio"
        flat_audioB.kind = "Audio"

        # append audio tracks to timeline
        tl.tracks.append(flat_audioB)
        tl.tracks.append(flat_audioA)

    return tl

def makeDeletes(tl, tracksOfDeletes):
    for t in tracksOfDeletes:
        tl.tracks.insert(0, t)
    return tl

# note: flatten_stack doesn't work when there's transitions
def makeTimelineSimple(trackA, trackB, clipGroup, audioGroup=None):
    tl = otio.schema.Timeline(name="timeline")

    tAddV = makeTrack("added", "Video", clipGroup.add, "GREEN")
    tEditedV = makeTrack("edited", "Video", clipGroup.edit, "ORANGE")
    tSameV = makeTrack("same", "Video", clipGroup.same)
    tDelV = makeTrack("deleted", "Video", clipGroup.delete, "PINK")

    tl.tracks.append(tDelV)

    flat_videoB = otio.core.flatten_stack([tSameV, tEditedV, tAddV])
    flat_videoB.name = "VideoB"
    tl.tracks.append(flat_videoB)

    # commented out for now
    # # add audio tracks if present
    # if audioGroup is not None:
    #     tAddA = makeTrack("added", "Audio", audioGroup.add, "GREEN")
    #     tEditedA = makeTrack("edited", "Audio", audioGroup.edit, "ORANGE")
    #     tSameA = makeTrack("same", "Audio", audioGroup.same)
    #     tDelA = makeTrack("deleted", "Audio", audioGroup.delete, "RED")

    #     flat_audioA = otio.core.flatten_stack([tSameA, tDelA])
    #     flat_audioB = otio.core.flatten_stack([tSameA, tEditedA, tAddA])

    #     flat_audioA.name = "AudioA"
    #     flat_audioB.name = "AudioB"
    #     flat_audioA.kind = "Audio"
    #     flat_audioB.kind = "Audio"

    #     # append audio tracks to timeline
    #     tl.tracks.append(flat_audioB)
    #     tl.tracks.append(flat_audioA)

    return tl

def makeTimelineSplitDelete(trackA, trackB, clipGroup, audioGroup=None):
    tl = otio.schema.Timeline(name="timeline")

    tAddV = makeTrack("added", "Video", clipGroup.add, "GREEN")
    tEditedV = makeTrack("edited", "Video", clipGroup.edit, "ORANGE")
    tSameV = makeTrack("same", "Video", clipGroup.same)
    tDelV = makeTrack("deleted", "Video", clipGroup.delete, "PINK")


    for e in clipGroup.edit():
        pass


    flat_videoB = otio.core.flatten_stack([tSameV, tEditedV, tAddV])
    flat_videoB.name = "VideoB"
    tl.tracks.append(flat_videoB)

    # commented out for now
    # # add audio tracks if present
    # if audioGroup is not None:
    #     tAddA = makeTrack("added", "Audio", audioGroup.add, "GREEN")
    #     tEditedA = makeTrack("edited", "Audio", audioGroup.edit, "ORANGE")
    #     tSameA = makeTrack("same", "Audio", audioGroup.same)
    #     tDelA = makeTrack("deleted", "Audio", audioGroup.delete, "RED")

    #     flat_audioA = otio.core.flatten_stack([tSameA, tDelA])
    #     flat_audioB = otio.core.flatten_stack([tSameA, tEditedA, tAddA])

    #     flat_audioA.name = "AudioA"
    #     flat_audioB.name = "AudioB"
    #     flat_audioA.kind = "Audio"
    #     flat_audioB.kind = "Audio"

    #     # append audio tracks to timeline
    #     tl.tracks.append(flat_audioB)
    #     tl.tracks.append(flat_audioA)

    return tl, tDelV

def makeTimelineFull(trackA, trackB, videoGroup, audioGroup=None):
    tl = otio.schema.Timeline(name="timeline")

    tlFlat = makeTimelineInline(trackA, trackB, videoGroup, audioGroup)

    tAddV = makeTrack("added", "Video", videoGroup.add, "GREEN")
    tEditedV = makeTrack("edited", "Video", videoGroup.edit, "ORANGE")
    tDelV = makeTrack("deleted", "Video", videoGroup.delete, "RED")

    # append video tracks to timeline
    tl.tracks.append(tDelV)

    # temp testing
    tl.tracks.append(copy.deepcopy(trackA))
    tl.tracks.append(copy.deepcopy(trackB))

    # temp comment
    # tlFlatVid = tlFlat.video_tracks()
    # for v in tlFlatVid:
    #     tl.tracks.append(copy.deepcopy(v))

    tl.tracks.append(tEditedV)
    tl.tracks.append(tAddV)

    # add audio tracks if present
    if audioGroup is not None:
        tAddA = makeTrack("added", "Audio", audioGroup.add, "GREEN")
        tEditedA = makeTrack("edited", "Audio", audioGroup.edit, "ORANGE")
        tDelA = makeTrack("deleted", "Audio", audioGroup.delete, "RED")

        # append video tracks to timeline
        tl.tracks.append(tAddA)
        tl.tracks.append(tEditedA)

        tlFlatAud = tlFlat.audio_tracks()
        for a in tlFlatAud:
            tl.tracks.append(copy.deepcopy(a))

        tl.tracks.append(tDelA)
    
    return tl
