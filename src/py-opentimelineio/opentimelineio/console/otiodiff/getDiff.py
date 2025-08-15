import argparse
import os
import copy
from collections import namedtuple

import opentimelineio as otio

from .clipData import ClipData
from . import makeOtio

#currently only handles video and audio tracks
def diff(timelineA, timelineB):
    # TODO: put docstring here, descriptive name, most wordy descrip
    hasVideo = False
    hasAudio = False

    # check input timelines for video and audio tracks
    if len(timelineA.video_tracks()) > 0 or len(timelineB.video_tracks()) > 0:
        hasVideo = True
    # else:
    #     print("no video tracks")

    if len(timelineA.audio_tracks()) > 0 or len(timelineB.audio_tracks()) > 0:
        hasAudio = True
    # else:
    #     print("no audio tracks")

    makeTlSummary(timelineA, timelineB)

    outputTl = None
    # process video tracks, audio tracks, or both
    if hasVideo and hasAudio:
        videoClipTable = processTracks(timelineA.video_tracks(), timelineB.video_tracks())
        audioClipTable = processTracks(timelineA.audio_tracks(), timelineB.audio_tracks())

        makeSummary(videoClipTable, otio.schema.Track.Kind.Video, "perTrack")
        makeSummary(audioClipTable, otio.schema.Track.Kind.Audio, "summary")

        videoTl = makeNewOtio(videoClipTable, otio.schema.Track.Kind.Video)
        outputTl = makeNewOtio(audioClipTable, otio.schema.Track.Kind.Audio)
        # combine
        for t in videoTl.tracks:
            outputTl.tracks.append(copy.deepcopy(t))
    
    elif hasVideo:
        videoClipTable = processTracks(timelineA.video_tracks(), timelineB.video_tracks())
        makeSummary(videoClipTable, otio.schema.Track.Kind.Video, "summary")
        outputTl = makeNewOtio(videoClipTable, otio.schema.Track.Kind.Video)

    elif hasAudio:
        audioClipTable = processTracks(timelineA.audio_tracks(), timelineB.audio_tracks())
        makeSummary(audioClipTable, "Audio", "summary")
        outputTl = makeNewOtio(audioClipTable, otio.schema.Track.Kind.Audio)

    else:
        # TODO: log no vid/aud or throw
        pass

    # Debug
    # origClipCount = len(timelineA.find_clips()) + len(timelineB.find_clips())

    # print(origClipCount)
    # print(len(outputTl.find_clips()))

    return outputTl

def toOtio(data, path):
    otio.adapters.write_to_file(data, path)

# for debugging, put response into file
def toJson(file):
    with open("clipDebug.json", "w") as f:
        f.write(file)

def toTxt(file):
    with open("report.txt", "w") as f:
        f.write(file)

# create a dictionary with all the cloned clips (ones that share the same truncated name)
# key is the truncated name, value is a list of ClipDatas
# @parameter clips, list of ClipDatas
def findClones(clips):
    clones = {}
    nonClones = []
    names = []

    for c in clips:
        names.append(c.name)
        
    for c in clips:
        if c.name in clones:
            clones[c.name].append(c)
        elif names.count(c.name) > 1:
            clones[c.name] = [c]
        else:
            nonClones.append(c)

    return clones, nonClones

def sortClones(clipDatasA, clipDatasB):
    # find cloned clips and separate out from unique clips
    clonesA, nonClonesA = findClones(clipDatasA)
    clonesB, nonClonesB = findClones(clipDatasB)

    # move clips that are clones in the other files into the clones folder
    # leaves stricly unique clips in nonClones
    # if a clip is a clone in the other timeline, put into clones dictionary
    for c in nonClonesA:
        if c.name in clonesB.keys():
            clonesA[c.name] = [c]
            nonClonesA.remove(c)
            # print("clone in B file: ", c.name)
    for c in nonClonesB:
        if c.name in clonesA.keys():
            clonesB[c.name] = [c]
            nonClonesB.remove(c)
            # print("clone in A file: ", c.name)

    # clipCountA = 0
    # clipCountB = 0
    return (clonesA, nonClonesA), (clonesB, nonClonesB)

# compare all clips that had a clone
def compareClones(clonesA, clonesB):
    added = []
    unchanged = []
    deleted = []

    for nameB in clonesB:
        # if there are no clips in timeline A with the same name
        # as cloneB, all of the clones of cloneB are new and added
        # print("name b: ", nameB)
        if nameB not in clonesA:
            added.extend(clonesB[nameB])

        # name matched, there exists clones in both A and B, check if there are same clips
        # technically can be the first one is "edited" and the rest are "added"/"deleted" -> depends on how want to define
        # currently, all clones that aren't the exact same get categorized as either "added" or "deleted"
        else:
            clipsA = clonesA[nameB]
            clipsB = clonesB[nameB]

            for clipB in clipsB:
                for clipA in clipsA:
                    isSame = clipB.checkSame(clipA)
                    if(isSame):
                        unchanged.append(clipB)
                    else:
                        if(clipB not in added):
                            added.append(clipB)
                        if(clipA not in deleted): 
                            deleted.append(clipA)

    # same as above for deleted clips
    for nameA in clonesA:
        if nameA not in clonesB:
            deleted.extend(clonesA[nameA])

    # print("from clones added: ", len(added), " deleted: ", len(deleted))
    
    return added, unchanged, deleted

# compare all strictly unique clips
def compareClips(clipDatasA, clipDatasB):
    namesA = {}
    namesB = {}

    added = []
    edited = []
    unchanged = []
    deleted = []

    for c in clipDatasA:
        namesA[c.name] = c
    for c in clipDatasB:
        namesB[c.name] = c

    for cB in clipDatasB:
        if cB.name not in namesA:
            added.append(cB)
        else:
            cB.matched_clipData = namesA[cB.name]
            isSame = cB.checkSame(cB.matched_clipData)
            if(isSame):
                # cB.pair = namesA[cB.name]
                unchanged.append(cB)
            else:
                isEdited = cB.checkEdited(cB.matched_clipData)
                if(isEdited):
                    # cB.matched_clipData = namesA[cB.name]
                    edited.append(cB)
                else:
                    print("======== not categorized ==========")
                    cA = namesA[cB.name]
                    print("Clips: ", cA.name, cB.name)
                    # cA.printData()
                    # cB.printData()
                    # print("===================")
                    # print type of object

    for cA in clipDatasA:
        if cA.name not in namesB:
            deleted.append(cA)

# TODO: some can be sets instead of lists
    return added, edited, unchanged, deleted

# # clip is an otio Clip
# def getTake(clip):
#     take = None
#     if(len(clip.name.split(" ")) > 1):
#         take = clip.name.split(" ")[1]
#     else:
#         take = None 
#     return take

# TODO: change name, make comparable rep? clip comparator? 
# TODO: learn abt magic functions ex __eq__
# def makeClipData(clip, trackNum):
#     cd = ClipData(clip.name.split(" ")[0],
#                   clip.media_reference,
#                   clip.source_range,
#                   clip.trimmed_range_in_parent(),
#                   trackNum,
#                   clip,
#                   getTake(clip))
#     return cd

# the consolidated version of processVideo and processAudio, meant to replace both
def compareTracks(trackA, trackB, trackNum):
    clipDatasA = []
    clipDatasB = []

    for c in trackA.find_clips():
        # put clip info into ClipData
        cd = ClipData(c, trackNum)
        clipDatasA.append(cd)
    
    for c in trackB.find_clips():
        # put clip info into ClipData
        cd = ClipData(c, trackNum)
        clipDatasB.append(cd)

    (clonesA, nonClonesA), (clonesB, nonClonesB) = sortClones(clipDatasA, clipDatasB)

    # compare clips and put into categories
    addV = []
    editV = []
    sameV = []
    deleteV = []
    
    # compare and categorize unique clips
    addV, editV, sameV, deleteV = compareClips(nonClonesA, nonClonesB)

    # compare and categorize cloned clips
    addCloneV, sameCloneV, deleteCloneV = compareClones(clonesA, clonesB)
    addV.extend(addCloneV)
    sameV.extend(sameCloneV)
    deleteV.extend(deleteCloneV)

    # SortedClipDatas = namedtuple('VideoGroup', ['add', 'edit', 'same', 'delete'])
    # videoGroup = SortedClipDatas(addV, editV, sameV, deleteV)

    return addV, editV, sameV, deleteV
    # return videoGroup

def checkMoved(allDel, allAdd):
    # ones found as same = moved
    # ones found as edited = moved and edited

    # wanted to compare full names to account for dif dep/take
    # otherwise shotA (layout123) and shotA (anim123) would count as a move and not as add
    # TODO: maybe preserve full name and also clip name, ex. id and name
    # TODO: fix compareClips so that it allows check by full name
    for c in allDel:
        c.name = c.full_name
    for c in allAdd:
        c.name = c.full_name

    newAdd, moveEdit, moved, newDel = compareClips(allDel, allAdd)
    # removes clips that are moved in same track, just keep clips moved between tracks
    moved = [clip for clip in moved if clip.track_num != clip.matched_clipData.track_num]
    for clip in moved:
        clip.note = "Moved from track: " + str(clip.matched_clipData.track_num)
        # print(i.name, i.track_num, i.note, i.pair.name, i.pair.track_num)
    # TODO: check if empty string or not
    for i in moveEdit:
        i.note += " and moved from track " + str(i.matched_clipData.track_num)
        # print(i.name, i.note)

    return newAdd, moveEdit, moved, newDel

# TODO? account for move edit, currently only identifies strictly moved
def sortMoved(clipTable):
    allAdd = []
    allEdit = []
    allSame = []
    allDel = []

    for track in clipTable.keys():
        clipGroup = clipTable[track]
        # print(clipTable[track]["add"])
        if "add" in clipGroup.keys():
            allAdd.extend(clipGroup["add"])
        if "delete" in clipGroup.keys():
            allDel.extend(clipGroup["delete"])
        if "same" in clipGroup.keys():
            allSame.extend(clipGroup["same"])
        if "edit" in clipGroup.keys():
            allEdit.extend(clipGroup["edit"])

        clipGroup["move"] = []

    add, moveEdit, moved, delete = checkMoved(allDel, allAdd)

    # currently moved clips are still marked as delete in timelineA 
    for cd in moved:
        clipTable[cd.track_num]["add"].remove(cd)
        clipTable[cd.track_num]["move"].append(cd)
        # clipTable[cd.track_num]["delete"].remove(cd)
        # clipTable[cd.pair.track_num]["moved"].append(cd.pair)
    
    return clipTable

def makeNewOtio(clipTable, trackType):
    newTl = otio.schema.Timeline(name="diffed")
    # TODO: rename into track sets
    tracksInA = []
    tracksInB = []

    # make tracks A and B in output timeline
    for trackNum in clipTable.keys():
        # use named tuple here since clip categories won't change anymore
        SortedClipDatas = namedtuple('ClipGroup', ['add', 'edit', 'same', 'delete', 'move'])
        clipGroup = SortedClipDatas(clipTable[trackNum]["add"], clipTable[trackNum]["edit"], clipTable[trackNum]["same"], clipTable[trackNum]["delete"], clipTable[trackNum]["move"])

        newTrackA = makeOtio.makeTrackA(clipGroup, trackNum, trackType)
        tracksInA.append(newTrackA)       

        newTrackB = makeOtio.makeTrackB(clipGroup, trackNum, trackType)
        tracksInB.append(newTrackB)

    # write order to output timeline so that timeline B is on top for both video and audio
    if trackType == otio.schema.Track.Kind.Video:
        newTl.tracks.extend(tracksInA)

        newEmpty = makeOtio.makeEmptyTrack(trackType)
        newTl.tracks.append(newEmpty)
        
        newTl.tracks.extend(tracksInB)
    elif trackType == otio.schema.Track.Kind.Audio:
        newTl.tracks.extend(tracksInB)

        newEmpty = makeOtio.makeEmptyTrack(trackType)
        newTl.tracks.append(newEmpty)
        
        newTl.tracks.extend(tracksInA)

    # makeOtio.colorMovedA(newTl, clipTable)

    return newTl

# TODO: rename to create bucket/cat/db/stuff; categorizeClipsByTracks + comment

def processTracks(tracksA, tracksB):
    # TODO: add docstring like this for public facing functions, otherwise comment is ok
    """Return a copy of the input timelines with only tracks that match
    either the list of names given, or the list of track indexes given."""
    clipTable = {}
    # READ ME IMPORTANT READ MEEEEEEE clipTable structure: {1:{"add": [], "edit": [], "same": [], "delete": []}
    # clipTable keys are track numbers, values are dictionaries
    # per track dictionary keys are clip categories, values are lists of clips of that category

    # TODO? ^change to class perhaps? low priority
    
    shorterTlTracks = tracksA if len(tracksA) < len(tracksB) else tracksB
    # print("len tracksA: ", len(tracksA), "len tracksB:", len(tracksB))

    # TODO: compute min of 2, then go through leftover and assign accordingly
    # maybe compare unmatched against empty track? pad shorter one with empty

    # Process Matched Tracks
    # index through all the tracks of the timeline with less tracks
    for i in range(0, len(shorterTlTracks)):
        currTrackA = tracksA[i]
        currTrackB = tracksB[i]
        trackNum = i + 1

        # clipGroup = compareTracks(currTrackA, currTrackB, trackNum)
        add, edit, same, delete = compareTracks(currTrackA, currTrackB, trackNum)
        # print(add)

        clipTable[trackNum] = {"add": add, "edit": edit, "same": same, "delete": delete}
        # print("here", clipTable[trackNum]["add"][0].name)

    # Process Unmatched Tracks
    if shorterTlTracks == tracksA:
        # timelineA is shorter so timelineB has added tracks
        for i in range(len(shorterTlTracks), len(tracksB)):
            newTrack = tracksB[i]
            trackNum = i + 1
            # newTrack.name = trackType + " B" + str(trackNum)

            added = []
            for c in newTrack.find_clips():
                cd = ClipData(c, trackNum)
                added.append(cd)

            clipTable[trackNum] = {"add": added, "edit": [], "same": [], "delete": []}
           
    else:
        for i in range(len(shorterTlTracks), len(tracksA)):
            newTrack = tracksA[i]
            trackNum = i + 1
            # newTrack.name = trackType + " A" + str(trackNum)

            deleted = []
            for c in newTrack.find_clips():
                cd = ClipData(c, trackNum)
                deleted.append(cd)

            clipTable[trackNum] = {"add": [], "edit": [], "same": [], "delete": deleted}

    # recat added/deleted into moved
    clipTable = sortMoved(clipTable)

    # tracksInA, tracksInB = makeNewOtio(clipTable, trackType)
    return clipTable
   
def makeSummary(clipTable, trackType, mode):
    print(trackType.upper(), "CLIPS")
    print("===================================")
    print("          Overview Summary         ")
    print("===================================")

    allAdd = []
    allEdit = []
    allSame = []
    allDel = []
    allMove = []

    if mode == "summary":
        for track in clipTable.keys():
            clipGroup = clipTable[track]

            allAdd.extend(clipGroup["add"]) if "add" in clipGroup.keys() else print("no add")
            allDel.extend(clipGroup["delete"]) if "delete" in clipGroup.keys() else print("no del")
            allSame.extend(clipGroup["same"]) if "same" in clipGroup.keys() else print("no same")
            allEdit.extend(clipGroup["edit"]) if "edit" in clipGroup.keys() else print("no edit")
            allMove.extend(clipGroup["move"]) if "move" in clipGroup.keys() else print("no move")

        print("total added:", len(allAdd))
        print("total edited:", len(allEdit))
        print("total moved:", len(allMove))
        print("total deleted:", len(allDel))

    if mode == "perTrack":
        # print by track
        for track in clipTable.keys():
            clipGroup = clipTable[track]
            print("================== Track", track, "==================")
            for cat in clipGroup.keys():
                print("")
                print(cat.upper(), ":", len(clipGroup[cat]))
                if cat != "same":
                    for i in clipGroup[cat]:
                        print(i.name)
    print("")

def makeTlSummary(timelineA, timelineB):
    print("Comparing Timeline B:", timelineB.name, "vs")
    print("          Timeline A:", timelineA.name)
    print("")

    if len(timelineA.video_tracks()) == 0:
        print("No video tracks in A")
    if len(timelineB.video_tracks()) == 0:
        print("No video tracks in B")

    if len(timelineA.audio_tracks()) == 0:
        print("No audio tracks in A")
    if len(timelineB.audio_tracks()) == 0:
        print("No audio tracks in B")

    # compare overall file duration
    if(timelineB.duration() > timelineA.duration()):
        delta = timelineB.duration().to_seconds() - timelineA.duration().to_seconds()
        print(f"Timeline duration increased by {delta:.2f} seconds")
    elif(timelineB.duration() < timelineA.duration()):
        delta = timelineA.duration().to_seconds() - timelineB.duration().to_seconds()
        print(f"Timeline duration decreased by {delta:.2f} seconds")   
    else:
        print("Timeline duration did not change")
    print("")  

''' ======= Notes =======
    maybe can make use of algorithms.filter.filter_composition

# a test using python difflib, prob not useful
    # # find deltas of 2 files and print into html site
    # d = HtmlDiff(wrapcolumn=100)
    # diff = d.make_file(file1.splitlines(), file2.splitlines(), context=True)
    # with open("diff.html", "w", encoding="utf-8") as f:
    #     f.write(diff)

    # s = SequenceMatcher(None, file1, file2)
    # print(s.quick_ratio())   

    # each one in new check with each one in old
    # if everything matches, unchanged <- can't just check with first instance because might have added one before it
    # if everything matches except for timeline position-> moved
    # if length doesn't match, look for ordering? or just classify as added/deleted
    # if counts of old and new dif then def add/deleted

    
    Test shot simple:
        python ./src/getDif.py /Users/yingjiew/Documents/testDifFiles/h150_104a.105j_2025.04.04_ANIM-flat.otio /Users/yingjiew/Documents/testDifFiles/150_104a.105jD_2025.06.27-flat.otio     

    Test seq matching edit's skywalker:
        python ./src/getDif.py /Users/yingjiew/Folio/casa/Dream_EP101_2024.02.09_Skywalker_v3.0_ChangeNotes.Relinked.01.otio /Users/yingjiew/Folio/casa/Dream_EP101_2024.02.23_Skywalker_v4.0_ChangeNotes.otio

    Test shot multitrack:
        python ./src/getDif.py /Users/yingjiew/Folio/edit-dept/More_OTIO/i110_BeliefSystem_2022.07.28_BT3.otio /Users/yingjiew/Folio/edit-dept/More_OTIO/i110_BeliefSystem_2023.06.09.otio
'''