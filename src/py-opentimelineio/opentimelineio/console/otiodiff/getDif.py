import argparse
import os
import copy
from collections import namedtuple

import opentimelineio as otio

from .clipData import ClipData
from . import makeOtio

# set otio version to 0.17
os.environ["OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL"] = "OTIO_CORE:0.17.0"

def main(tlA, tlB):
    hasVideo = False
    hasAudio = False

    # check input timelines for video and audio tracks
    if len(tlA.video_tracks()) > 0 or len(tlB.video_tracks()) > 0:
        hasVideo = True
    else:
        print("no video tracks")

    if len(tlA.audio_tracks()) > 0 or len(tlB.audio_tracks()) > 0:
        hasAudio = True
    else:
        print("no audio tracks")

    outputTl = None

    # process video tracks, audio tracks, or both
    if hasVideo and hasAudio:
        videoTl = processTracks(tlA.video_tracks(), tlB.video_tracks(), "Video")
        outputTl = processTracks(tlA.audio_tracks(), tlB.audio_tracks(), "Audio")
        # combine
        for t in videoTl.tracks:
            outputTl.tracks.append(copy.deepcopy(t))
    
    elif hasVideo:
        outputTl = processTracks(tlA.video_tracks(), tlB.video_tracks(), "Video")

    elif hasAudio:
        outputTl = processTracks(tlA.audio_tracks(), tlB.audio_tracks(), "Audio")

    # Debug
    origClipCount = len(tlA.find_clips()) + len(tlB.find_clips())

    print(origClipCount)
    print(len(outputTl.find_clips()))

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
            isSame = cB.checkSame(namesA[cB.name])
            if(isSame):
                cB.pair = namesA[cB.name]
                unchanged.append(cB)
            else:
                isEdited = cB.checkEdited(namesA[cB.name])
                if(isEdited):
                    cB.pair = namesA[cB.name]
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

    return added, edited, unchanged, deleted

# clip is an otio Clip
def getTake(clip):
    take = None
    if(len(clip.name.split(" ")) > 1):
        take = clip.name.split(" ")[1]
    else:
        take = None 
    return take

def makeClipData(clip, trackNum):
    cd = ClipData(clip.name.split(" ")[0],
                  clip.media_reference,
                  clip.source_range,
                  clip.trimmed_range_in_parent(),
                  trackNum,
                  clip,
                  getTake(clip))
    return cd

# the consolidated version of processVideo and processAudio, meant to replace both
def compareTracks(trackA, trackB, trackNum):
    clipDatasA = []
    clipDatasB = []

    for c in trackA.find_clips():
        # put clip info into ClipData
        cd = makeClipData(c, trackNum)
        clipDatasA.append(cd)
    
    for c in trackB.find_clips():
        # put clip info into ClipData
        cd = makeClipData(c, trackNum)
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

    # makeSummary(trackA, trackB, videoGroup)

    return addV, editV, sameV, deleteV
    # return videoGroup

def checkMoved(allDel, allAdd):
    # ones found as same = moved
    # ones found as edited = moved and edited

    # wanted to compare full names to account for dif dep/take
    for c in allDel:
        c.name = c.source.name
    for c in allAdd:
        c.name = c.source.name

    newAdd, moveEdit, moved, newDel = compareClips(allDel, allAdd)
    moved = [clip for clip in moved if clip.track_num != clip.pair.track_num]
    for clip in moved:
        clip.note = "Moved from track: " + str(clip.pair.track_num)
        # print(i.name, i.track_num, i.note, i.pair.name, i.pair.track_num)
    
    for i in moveEdit:
        i.note += " and moved from track " + str(i.pair.track_num)
        # print(i.name, i.note)

    return newAdd, moveEdit, moved, newDel


def processDB(clipDB):
    allAdd = []
    allEdit = []
    allSame = []
    allDel = []

    for track in clipDB.keys():
        clipGroup = clipDB[track]
        # print(clipDB[track]["add"])
        allAdd.extend(clipGroup["add"]) if "add" in clipGroup.keys() else print("no add ")
        allDel.extend(clipGroup["delete"]) if "delete" in clipGroup.keys() else print("no del")
        allSame.extend(clipGroup["same"]) if "same" in clipGroup.keys() else print("no same")
        allEdit.extend(clipGroup["edit"]) if "edit" in clipGroup.keys() else print("no edit")

        clipGroup["move"] = []

    add, moveEdit, moved, delete = checkMoved(allDel, allAdd)

    # currently has redundancy where moved clips aren't deleted from add
    for cd in moved:
        # clipDB[cd.track_num]["add"].remove(cd)
        # clipDB[cd.track_num]["delete"].remove(cd)
        clipDB[cd.track_num]["move"].append(cd)
        # clipDB[cd.pair.track_num]["moved"].append(cd.pair)
    
    return clipDB

def newMakeOtio(clipDB, trackType):
    displayA = []
    displayB = []
    for trackNum in clipDB.keys():
        SortedClipDatas = namedtuple('VideoGroup', ['add', 'edit', 'same', 'delete', 'move'])
        clipGroup = SortedClipDatas(clipDB[trackNum]["add"], clipDB[trackNum]["edit"], clipDB[trackNum]["same"], clipDB[trackNum]["delete"], clipDB[trackNum]["move"])

        newA = makeOtio.makeTrackA(clipGroup, trackNum, trackType)
        displayA.append(newA)       

        newB = makeOtio.makeTrackB(clipGroup, trackNum, trackType)
        displayB.append(newB)

    return displayA, displayB

    # add note moved from track# and moved to track#


    # print("add total: ", len(clipDB["add"]))
    # print("edit total: ", len(clipDB["edit"]))
    # print("same total: ", len(clipDB["same"]))
    # print("delete total: ", len(clipDB["delete"]))

    # # use full names to compare
    # # constrain "moved" to be same dep and take too, otherwise
    # # shotA (layout) and shotA (anim) would count as a move and not as add
    # for c in clipDB["add"]:
    #     c.name = c.source.name
    # for c in clipDB["delete"]:
    #     c.name = c.source.name

    # # problem is this one breaks the relats with track
    # newAdd, newEdit, newSame, newDel = compareClips(clipDB["add"], clipDB["delete"])
    # clipDB["newEdit"] = newEdit
    # clipDB["movedTracks"] = newSame

    # # good to run make summary here
    # print("comparing all adds with all deletes:", len(newAdd), "e", len(newEdit), "s", len(newSame), "d", len(newDel))
    # for c in newEdit:
    #     print(c.name)

    # print("sum: ", len(clipDB["add"]) + 2 * len(clipDB["edit"]) + 2 * len(clipDB["same"]) +len(clipDB["delete"]))

    # print all the adds
    # def printAdd():
    #     for track in clipDB.keys():
    #         print(track, clipDB[track]["add"])

    # return clipDB


def processTracks(tracksA, tracksB, trackType):
    newTl = otio.schema.Timeline(name="timeline")
    displayA = []
    displayB = []
    clipDB = {}
    # clipDB = {"add": [], "edit": [], "same": [], "delete": []}
    
    shorterTlTracks = tracksA if len(tracksA) < len(tracksB) else tracksB
    # print("len tracksA: ", len(tracksA), "len tracksB:", len(tracksB))

    # Process Matched Tracks
    # index through all the tracks of the timeline with less tracks
    for i in range(0, len(shorterTlTracks)):
        currTrackA = tracksA[i]
        currTrackB = tracksB[i]
        trackNum = i + 1


        # clipGroup = compareTracks(currTrackA, currTrackB, trackNum)
        add, edit, same, delete = compareTracks(currTrackA, currTrackB, trackNum)
        # print(add)

        # newDict = {"add": add, "edit": edit, "same": same, "delete": delete}
        # clipDB[trackNum] = newDict
        clipDB[trackNum] = {"add": add, "edit": edit, "same": same, "delete": delete}
        # print("here", clipDB[trackNum]["add"][0].name)

        # clipDB["add"] += clipGroup.add
        # clipDB["edit"] += clipGroup.edit
        # clipDB["same"] += clipGroup.same
        # clipDB["delete"] += clipGroup.delete

        # add to display otio
        # newA = makeOtio.makeTrackA(clipGroup, trackNum, trackType)
        # displayA.append(newA)       

        # newB = makeOtio.makeTrackB(clipGroup, trackNum, trackType)
        # displayB.append(newB)

    # # Process Unmatched Tracks
    if shorterTlTracks == tracksA:
    #     # tlA is shorter so tlB has added tracks
        for i in range(len(shorterTlTracks), len(tracksB)):
            newTrack = tracksB[i]
            trackNum = i + 1
            newTrack.name = trackType + " B" + str(trackNum)

            added = []
            for c in newTrack.find_clips():
    #             c = makeOtio.addRavenColor(c, "GREEN")
    #             # newMarker = makeOtio.addMarker(c, "GREEN")
    #             # c.markers.append(newMarker)

                cd = makeClipData(c, trackNum)
                added.append(cd)

    #         # add to top of track stack
    #         displayB.append(copy.deepcopy(newTrack))
    #         # print("added unmatched track", len(newTl.tracks))
            
            clipDB[trackNum] = {"add": added, "edit": [], "same": [], "delete": []}
    else:
        for i in range(len(shorterTlTracks), len(tracksA)):
    #         # color clips
            newTrack = tracksA[i]
            trackNum = i + 1
            newTrack.name = trackType + " A" + str(trackNum)

            deleted = []
            for c in newTrack.find_clips():
    #             c = makeOtio.addRavenColor(c, "PINK")
    #             # newMarker = makeOtio.addMarker(c, "PINK")
    #             # c.markers.append(newMarker)

                cd = makeClipData(c, trackNum)
                deleted.append(cd)

    #         displayA.append(copy.deepcopy(newTrack))

            clipDB[trackNum] = {"add": [], "edit": [], "same": [], "delete": deleted}

    clipDB = processDB(clipDB)

    newMakeSummary(clipDB, "summary")
    displayA, displayB = newMakeOtio(clipDB, trackType)

    newTl.tracks.extend(displayA)

    newEmpty = makeOtio.makeEmptyTrack(trackType)
    newTl.tracks.append(newEmpty)
    
    newTl.tracks.extend(displayB)

    return newTl

def newMakeSummary(clipDB, mode):
    print("===================================")
    print("          Overview Summary        ")
    print("===================================")
    allAdd = []
    allEdit = []
    allSame = []
    allDel = []
    allMove = []

    if mode == "summary":
        for track in clipDB.keys():
            clipGroup = clipDB[track]

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
        for track in clipDB.keys():
            clipGroup = clipDB[track]
            print("================== Track", track, "==================")
            for cat in clipGroup.keys():
                print("")
                print(cat.upper(), ":", len(clipGroup[cat]))
                for i in clipGroup[cat]:
                    print(i.name)
    print("")

def makeSummary(tlA, tlB, videoGroup):
    print("===================================")
    print("          Overview Summary        ")
    print("===================================")

    # compare overall file duration
    # if(tlB.duration() > tlA.duration()):
    #     delta = tlB.duration().to_seconds() - tlA.duration().to_seconds()
    #     print(f"timeline duration increased by {delta:.2f} seconds")
    # elif(tlB.duration() < tlA.duration()):
    #     delta = tlA.duration().to_seconds() - tlB.duration().to_seconds()
    #     print(f"timeline duration decreased by {delta:.2f} seconds")   
    # print("")     

    # print("======= Cloned Video Clips =======")
    # print("Otio A:")
    # for k in clonesA.keys():
    #     print(k, ":", len(clonesA[k]))
    # print("")    
    # print("Otio B:")
    # for k in clonesB.keys():
    #     print(k, ":", len(clonesB[k]))

    
    print("======= Clip Info Overview =======")
    print("added: ", len(videoGroup.add))
    for c in videoGroup.add:
        print(c.name)
    print("=======")

    print("edited: ", len(videoGroup.edit))
    for c in videoGroup.edit:
        print(c.name)
    print("=======")
    
    print("same: ", len(videoGroup.same))
    # for c in sameV:
        # print(c.name)
    #     if(c["label"] == "moved"):
    #         print(c["name"], " ", c["label"])
    print("=======")

    print("deleted: ", len(videoGroup.delete))
    for c in videoGroup.delete:
        print(c.name)
    print("=======")   

if __name__ == "__main__":
    main()

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

# def processAllTracksAB(tlA, tlB):
#     # determine which track set is shorter

#     hasVideo = False
#     hasAudio = False

#     if len(tlA.video_tracks()) > 0 or len(tlB.video_tracks()) > 0:
#         hasVideo = True
#     else:
#         print("no video tracks")

#     if len(tlA.audio_tracks()) > 0 or len(tlB.audio_tracks()) > 0:
#         hasAudio = True
#     else:
#         print("no audio tracks")


#     if hasVideo:
#         processTracks(tlA.video_tracks(), tlB.video_tracks(), "Video")

#     if hasAudio:
#         processTracks(tlA.audio_tracks(), tlB.audio_tracks(), "Audio")
    
    
#     tracksA = tlA.video_tracks()
#     tracksB = tlB.video_tracks()
#     newTl = otio.schema.Timeline(name="timeline")
#     displayA = []
#     displayB = []

    
#     shorterTlTracks = tracksA if len(tracksA) < len(tracksB) else tracksB
#     # print("len tracksA: ", len(tracksA), "len tracksB:", len(tracksB))

#     # Process Matched Video Tracks
#     # index through all the video tracks of the timeline with less tracks
#     for i in range(0, len(shorterTlTracks)):
#         currTrackA = tracksA[i]
#         currTrackB = tracksB[i]

#         videoGroup = compareTracks(currTrackA, currTrackB)

#         trackNum = i + 1
#         newA = makeOtio.makeTrackA(videoGroup, trackNum, "Video")
#         displayA.append(newA)       

#         newB = makeOtio.makeTrackB(videoGroup, trackNum, "Video")
#         displayB.append(newB)

#     if shorterTlTracks == tracksA:
#         # tlA is shorter so tlB has added tracks
#         for i in range(len(shorterTlTracks), len(tracksB)):
#             newTrack = tracksB[i]
#             for c in newTrack.find_clips():
#                 c = makeOtio.addRavenColor(c, "GREEN")
#                 # newMarker = makeOtio.addMarker(c, "GREEN")
#                 # c.markers.append(newMarker)

#             # add to top of track stack
#             displayB.append(copy.deepcopy(newTrack))
#             # print("added unmatched track", len(newTl.tracks))
#     else:
#         for i in range(len(shorterTlTracks), len(tracksA)):
#             # color clips
#             newTrack = tracksA[i]
#             for c in newTrack.find_clips():
#                 c = makeOtio.addRavenColor(c, "PINK")
#                 # newMarker = makeOtio.addMarker(c, "PINK")
#                 # c.markers.append(newMarker)
#             displayA.append(copy.deepcopy(newTrack))

#     newTl.tracks.extend(displayA)

#     newEmpty = makeOtio.makeEmptyTrack()
#     newTl.tracks.append(newEmpty)
    
#     newTl.tracks.extend(displayB)

#     return newTl
#     # =================================================================================


# def processAllTracks(tlA, tlB, trackType, displayMode):
#     # determine which track set is shorter
#     assert(trackType is not None), "Missing type of track in function call"
#     # TODO add check that timeline track length is not 0

#     tracksA = None
#     tracksB = None
#     newTl = otio.schema.Timeline(name="timeline")
#     tempB = otio.schema.Timeline(name="timeline")

#     if(trackType.lower() == "video"):
#         tracksA = tlA.video_tracks()
#         tracksB = tlB.video_tracks()
#     elif(trackType.lower() == "audio"):
#         tracksA = tlA.audio_tracks()
#         tracksB = tlB.audio_tracks()
#     elif(trackType.lower() == "all"):
#         print("show both video and audio")        
    
#     shorterTlTracks = tracksA if len(tracksA) < len(tracksB) else tracksB
#     print("len tracksA: ", len(tracksA), "len tracksB:", len(tracksB))

#     # Process Matched Video Tracks
#     # index through all the video tracks of the timeline with less tracks
#     tracksOfDels = []
#     for i in range(0, len(shorterTlTracks)):
#         currTrackA = tracksA[i]
#         currTrackB = tracksB[i]

#         videoGroup = compareTracks(currTrackA, currTrackB)

#         # videoGroup = SortedClipDatas(addV, editV, sameV, deleteV)

#         # add processed tracks to display timeline
#         getTl = None
#         if displayMode is None:
#             print("Warning: Display mode not specified, defaulting to inline")
#             getTl = makeOtio.makeTimelineOfType("simple", currTrackA, currTrackB, videoGroup)
#         else:
#             # getTl = makeOtio.makeTimelineOfType(displayMode, currTrackA, currTrackB, videoGroup)
            
#             # split delete out
#             getTl, tDelV = makeOtio.makeTimelineSplitDelete(currTrackA, currTrackB, videoGroup)
#             tracksOfDels.insert(0, tDelV)

#         for t in getTl.tracks:
#             newTl.tracks.append(copy.deepcopy(t))
#         print("current track stack size:", len(newTl.tracks))

#     # Process Unmatched Video Tracks
#     # mark unmatched tracks as either "added" or "deleted" and add to display timeline
#     if shorterTlTracks == tracksA:
#         # tlA is shorter so tlB has added tracks
#         for i in range(len(shorterTlTracks), len(tracksB)):
#             newTrack = tracksB[i]
#             for c in newTrack.find_clips():
#                 c = makeOtio.addRavenColor(c, "GREEN")

#             # add to top of track stack
#             newTl.tracks.append(copy.deepcopy(newTrack))
#             print("added unmatched track", len(newTl.tracks))
#     else:
#         for i in range(len(shorterTlTracks), len(tracksA)):
#             # color clips
#             newTrack = tracksA[i]
#             for c in newTrack.find_clips():
#                 c = makeOtio.addRavenColor(c, "PINK")

#             # add to bottom of track stack
#             # newTl.tracks.append(copy.deepcopy(newTrack))

#             # split delete out
#             # tracksOfDels.insert(0, newTrack)

#             print("added unmatched track", len(newTl.tracks))

#     makeOtio.makeDeletes(newTl, tracksOfDels)

#     return newTl


# def processVideo(videoTrackA, videoTrackB):
#     clipDatasA = []
#     clipDatasB = []

#     for c in videoTrackA.find_clips():
#         take = None
#         if(len(c.name.split(" ")) > 1):
#             take = c.name.split(" ")[1]
#         else:
#             take = None
#         cd = ClipData(c.name.split(" ")[0],
#                       c.media_reference,
#                       c.source_range,
#                       c.trimmed_range_in_parent(),
#                       c,
#                       take)
#         clipDatasA.append(cd)
    
#     for c in videoTrackB.find_clips():
#         take = None
#         if(len(c.name.split(" ")) > 1):
#             take = c.name.split(" ")[1]
#         else:
#             take = None
#         cd = ClipData(c.name.split(" ")[0],
#                       c.media_reference,
#                       c.source_range,
#                       c.trimmed_range_in_parent(),
#                       c,
#                       take)
#         clipDatasB.append(cd)

#     (clonesA, nonClonesA), (clonesB, nonClonesB) = sortClones(clipDatasA, clipDatasB)

#     # compare clips and put into categories
#     addV = []
#     editV = []
#     sameV = []
#     deleteV = []
    
#     # compare and categorize unique clips
#     addV, editV, sameV, deleteV = compareClips(nonClonesA, nonClonesB)

#     # compare and categorize cloned clips
#     addCloneV, sameCloneV, deleteCloneV = compareClones(clonesA, clonesB)
#     addV.extend(addCloneV)
#     sameV.extend(sameCloneV)
#     deleteV.extend(deleteCloneV)

#     return addV, editV, sameV, deleteV

# def processAudio(audioTrackA, audioTrackB):
#     addA = []
#     editA = []
#     sameA = []
#     deleteA = []

#     audioClipDatasA = []
#     audioClipDatasB = []

#     for c in audioTrackA.find_clips():
#         cd = ClipData(c.name,
#                     c.media_reference,
#                     c.source_range,
#                     c.trimmed_range_in_parent(),
#                     c)
#         audioClipDatasA.append(cd)
    
#     for c in audioTrackB.find_clips():
#         cd = ClipData(c.name,
#                     c.media_reference,
#                     c.source_range,
#                     c.trimmed_range_in_parent(),
#                     c)
#         audioClipDatasB.append(cd)

#     addA, editA, sameA, deleteA = compareClips(audioClipDatasA, audioClipDatasB)
    
#     return addA, editA, sameA, deleteA


# def processSingleTrack(tlA, tlB):
#     assert len(tlA.video_tracks()) == 1, "File A contains more than 1 video track. Please flatten to a single track."
#     assert len(tlB.video_tracks()) == 1, "File B contains more than 1 video track. Please flatten to a single track."

#     videoTrackA = tlA.video_tracks()[0]
#     videoTrackB = tlB.video_tracks()[0]

#     # check for nested video tracks and stacks
#     assert(not videoTrackA.find_children(otio._otio.Track)), "File A contains nested track(s). Please flatten to a single track."
#     # assert(not videoTrackA.find_children(otio._otio.Stack)), "File A contains nested stack(s). Please flatten to a single track."
#     assert(not videoTrackB.find_children(otio._otio.Track)), "File B contains nested track(s). Please flatten to a single track."
#     # assert(not videoTrackB.find_children(otio._otio.Stack)), "File B contains nested stack(s). Please flatten to a single track."


#     # ====== VIDEO TRACK PROCESSING ======
#     addV, editV, sameV, deleteV = processVideo(videoTrackA, videoTrackB)

#     # ====== AUDIO TRACK PROCESSING ======
#     # check if audio tracks exist
#     hasAudio = False

#     if(len(tlA.audio_tracks()) != 0):
#         assert len(tlA.audio_tracks()) == 1, "File A contains more than 1 audio track"
#         hasAudio = True
#     if(len(tlB.audio_tracks()) != 0):
#         assert len(tlB.audio_tracks()) == 1, "File B contains more than 1 audio track"
#         hasAudio = True

#     # if audio track(s) present, compare audio track(s)
#     if(hasAudio):
#         audioTrackA = tlA.audio_tracks()[0]
#         audioTrackB = tlB.audio_tracks()[0]

#         addA, editA, sameA, deleteA = processAudio(audioTrackA, audioTrackB)      

#     # ====== MAKE NEW OTIO ======
#     SortedClipDatas = namedtuple('VideoGroup', ['add', 'edit', 'same', 'delete'])
#     videoGroup = SortedClipDatas(addV, editV, sameV, deleteV)

#     # check which display mode is toggled
#     if(args.display is None):
#         print("no display mode specified, defaulting to inline")
#         flatTl = makeOtio.makeTimelineInline(videoTrackA, videoTrackB, videoGroup)
#         toOtio(flatTl)

#     # multi-track output
#     elif(args.display.lower() == "stack"):
#         print("display mode: stack")
#         if(hasAudio):
#             audioGroup = SortedClipDatas(addA, editA, sameA, deleteA)
#             stackTl = makeOtio.makeTimelineStack(videoTrackA, videoTrackB, videoGroup, audioGroup)
#         else:
#             stackTl = makeOtio.makeTimelineStack(videoTrackA, videoTrackB, videoGroup)
#         toOtio(stackTl)

#     # single-track output
#     elif(args.display.lower() == "inline"):
#         print("display mode: inline")
#         if(hasAudio):
#             audioGroup = SortedClipDatas(addA, editA, sameA, deleteA)
#             flatTl = makeOtio.makeTimelineInline(videoTrackA, videoTrackB, videoGroup, audioGroup)

#         # flat track output
#         else:
#             flatTl = makeOtio.makeTimelineInline(videoTrackA, videoTrackB, videoGroup)
#         toOtio(flatTl)

#     # both multi and single track output
#     elif(args.display.lower() == "full"):
#         print("display mode: full")
#         if(hasAudio):
#             audioGroup = SortedClipDatas(addA, editA, sameA, deleteA)
#             fullTl = makeOtio.makeTimelineFull(videoTrackA, videoTrackB, videoGroup, audioGroup)
#         else:
#             fullTl = makeOtio.makeTimelineFull(videoTrackA, videoTrackB, videoGroup)
#         toOtio(fullTl)
        
#     else:
#         print("not an accepted display mode, no otios made")