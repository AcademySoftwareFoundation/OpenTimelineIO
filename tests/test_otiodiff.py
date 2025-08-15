import unittest
import opentimelineio as otio

from opentimelineio.console.otiodiff.clipData import ClipData
import opentimelineio.console.otiodiff.makeOtio as makeOtio
import opentimelineio.console.otiodiff.getDiff as getDiff

from collections import namedtuple


class TestClipData(unittest.TestCase):
    # check if the names of two ClipDatas are the same

    def test_same_name(self):
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        clipB = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        trackA.append(clipA)
        trackB.append(clipB)

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)

        assert clipDataB.sameName(clipDataA)

    def test_different_name(self):
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        clipB = otio.schema.Clip(
            name = "testName2 testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        trackA.append(clipA)
        trackB.append(clipB)

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)

        assert not clipDataB.sameName(clipDataA)


    def test_same_duration(self):
        # check that length of clip is the same
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        clipB = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        trackA.append(clipA)
        trackB.append(clipB)

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)

        assert clipDataB.sameDuration(clipDataA)
        
    def test_different_duration(self):
        # check that length of clip is the different
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        clipB = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(20, 24)),
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        trackA.append(clipA)
        trackB.append(clipB)

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)

        assert not clipDataB.sameDuration(clipDataA)


    def test_check_same(self):
        # check that two exact same clips are the same
        # check that two exact same clips but moved in the timeline are the same
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        clipB = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        trackA.append(clipA)
        trackB.append(clipB)

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)

        assert clipDataB.checkSame(clipDataA)

    def test_check_same_if_move(self):
        # check that two exact same clips but moved in the timeline are the same
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),                                    
        )
        clipB = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),                                    
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        gapDur = otio.opentime.RationalTime(5, 24)
        gap = otio.schema.Gap(duration = gapDur)

        trackA.append(clipA)
        trackB.extend([gap, clipB])

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)

        assert clipDataB.checkSame(clipDataA)
        assert clipDataB.note == "moved"
        
    def test_check_not_same(self):
        # check that two clips with different names are not the same
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        clipB = otio.schema.Clip(
            name = "testName2 testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        trackA.append(clipA)
        trackB.append(clipB)

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)

        assert not clipDataB.checkSame(clipDataA)
        assert clipDataB.note is None

    def test_check_not_same2(self):
        # check that two clips with different source range start durations are not the same
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        clipB = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(20, 24)),
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        trackA.append(clipA)
        trackB.append(clipB)

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)
        
        assert not clipDataB.checkSame(clipDataA)
        assert clipDataB.note is None

    def test_check_not_same3(self):
        # check that two clips with different source range start times are not the same
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        clipB = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(10, 24),
                                    otio.opentime.RationalTime(10, 24)),
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        trackA.append(clipA)
        trackB.append(clipB)

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)
        
        assert not clipDataB.checkSame(clipDataA)
        assert clipDataB.note is None

    def test_check_Edited(self):
        # check for trim head/tail and lengthen head/tail
        clipA = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(100, 24)),
        )
        clipB = otio.schema.Clip(
            name = "testName testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(10, 24),
                                    otio.opentime.RationalTime(90, 24))),
            source_range = otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(10, 24),
                                    otio.opentime.RationalTime(90, 24)),
        )
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()

        trackA.append(clipA)
        trackB.append(clipB)

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)
        
        assert clipDataB.checkEdited(clipDataA)
        assert clipDataB.note == "trimmed 10 frames"

class TestGetDif(unittest.TestCase):
    def test_find_clones(self):
        clipA = otio.schema.Clip(
            name = "clipA testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipB = otio.schema.Clip(
            name = "clipB testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(10, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipC = otio.schema.Clip(
            name = "clipC testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(20, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipCClone = otio.schema.Clip(
            name = "clipC testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(30, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipD = otio.schema.Clip(
            name = "clipD testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(40, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        trackA = otio.schema.Track()

        trackA.extend([clipA, clipB, clipC, clipCClone, clipD])

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)
        clipDataC = ClipData(clipC, 1)
        clipDataCClone = ClipData(clipCClone, 1)
        clipDataD = ClipData(clipD, 1)
        
        testClips = [clipDataA, clipDataB, clipDataC, clipDataCClone, clipDataD]
        clones, nonClones = getDiff.findClones(testClips)

        correctClones = {clipDataC.name: [clipDataC, clipDataCClone]}
        correctNonClones = [clipDataA, clipDataB, clipDataD]

        assert(clones == correctClones), "Not all cloned clips correctly identified"
        assert(nonClones == correctNonClones), "Not all unique clips correctly identified"


    def test_sort_clones_clones_in_both(self):
        # SETUP
        clipA = otio.schema.Clip(
            name = "clipA testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipB = otio.schema.Clip(
            name = "clipB testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(10, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipC = otio.schema.Clip(
            name = "clipC testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(20, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipCClone = otio.schema.Clip(
            name = "clipC testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(30, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipD = otio.schema.Clip(
            name = "clipD testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(40, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        trackA = otio.schema.Track()

        trackA.extend([clipA, clipB, clipC, clipCClone, clipD])

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)
        clipDataC = ClipData(clipC, 1)
        clipDataCClone = ClipData(clipCClone, 1)
        clipDataD = ClipData(clipD, 1)

        clipDatasA = [clipDataA, clipDataB, clipDataC, clipDataCClone]
        clipDatasB = [clipDataB, clipDataC, clipDataCClone, clipDataD]

        # EXERCISE
        sortedClonesA, sortedClonesB = getDiff.sortClones(clipDatasA, clipDatasB)

        # VERIFY 
        clonesA, nonClonesA = sortedClonesA
        clonesB, nonClonesB = sortedClonesB
        
        assert(len(clonesA) == 1), "Number of clones found in trackA doesn't match"
        assert(len(nonClonesA) == 2), "Number of non-clones found in trackA doesn't match"
        assert(len(clonesB) == 1), "Number of clones found in trackB doesn't match"
        assert(len(nonClonesB) == 2), "Number of non-clones found in trackB doesn't match"

    def test_sort_clones_clones_in_one(self):
        # SETUP
        clipA = otio.schema.Clip(
            name = "clipA testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipB = otio.schema.Clip(
            name = "clipB testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(10, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipC = otio.schema.Clip(
            name = "clipC testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(20, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipCClone = otio.schema.Clip(
            name = "clipC testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(30, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipD = otio.schema.Clip(
            name = "clipD testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(40, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        trackA = otio.schema.Track()

        trackA.extend([clipA, clipB, clipC, clipCClone, clipD])

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)
        clipDataC = ClipData(clipC, 1)
        clipDataCClone = ClipData(clipCClone, 1)
        clipDataD = ClipData(clipD, 1)

        clipDatasA = [clipDataA, clipDataB, clipDataC, clipDataCClone]
        clipDatasB = [clipDataA, clipDataB, clipDataD]

        # EXERCISE
        sortedClonesA, sortedClonesB = getDiff.sortClones(clipDatasA, clipDatasB)

        # VERIFY 
        clonesA, nonClonesA = sortedClonesA
        clonesB, nonClonesB = sortedClonesB
        
        assert(len(clonesA) == 1), "Number of clones found in trackA doesn't match"
        assert(len(nonClonesA) == 2), "Number of non-clones found in trackA doesn't match"
        assert(len(clonesB) == 0), "Number of clones found in trackB doesn't match"
        assert(len(nonClonesB) == 3), "Number of non-clones found in trackB doesn't match"
        
    def test_sort_clones_clones_in_one_single_in_other(self):
        # SETUP
        clipA = otio.schema.Clip(
            name = "clipA testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(0, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipB = otio.schema.Clip(
            name = "clipB testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(10, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipC = otio.schema.Clip(
            name = "clipC testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(20, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipCClone = otio.schema.Clip(
            name = "clipC testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(30, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        clipD = otio.schema.Clip(
            name = "clipD testTake",
            media_reference = otio.core.MediaReference(
                                available_range=otio.opentime.TimeRange(
                                    otio.opentime.RationalTime(40, 24),
                                    otio.opentime.RationalTime(10, 24))),
        )
        trackA = otio.schema.Track()

        trackA.extend([clipA, clipB, clipC, clipCClone, clipD])

        clipDataA = ClipData(clipA, 1)
        clipDataB = ClipData(clipB, 1)
        clipDataC = ClipData(clipC, 1)
        clipDataCClone = ClipData(clipCClone, 1)
        clipDataD = ClipData(clipD, 1)

        clipDatasA = [clipDataA, clipDataB, clipDataC, clipDataCClone]
        clipDatasB = [clipDataB, clipDataC, clipDataD]

        # EXERCISE
        sortedClonesA, sortedClonesB = getDiff.sortClones(clipDatasA, clipDatasB)

        # VERIFY 
        clonesA, nonClonesA = sortedClonesA
        clonesB, nonClonesB = sortedClonesB
        
        assert(len(clonesA) == 1), "Number of clones found in trackA doesn't match"
        assert(len(nonClonesA) == 2), "Number of non-clones found in trackA doesn't match"
        assert(len(clonesB) == 1), "Number of clones found in trackB doesn't match"
        assert(len(nonClonesB) == 2), "Number of non-clones found in trackB doesn't match"

# class TestMakeOtio(unittest.TestCase):
#     # Test the type parameter to makeTimelineOfType, but not the detailed results.
#     def test_make_timeline_type(self):
#         # SETUP
#         trackA = otio.schema.Track()
#         trackB = otio.schema.Track()
#         pass

        # SortedClipDatas = namedtuple('VideoGroup', ['add', 'edit', 'same', 'delete'])
        # videoGroup = SortedClipDatas([], [], [], [])

        # # EXERCISE
        # tlStack = makeOtio.makeTimelineOfType("stack", trackA, trackB, videoGroup)
        # tlInline = makeOtio.makeTimelineOfType("inline", trackA, trackB, videoGroup)
        # tlFull = makeOtio.makeTimelineOfType("full", trackA, trackB, videoGroup)
        # bogus = makeOtio.makeTimelineOfType("bogus", trackA, trackB, videoGroup)

        # # VERIFY
        # assert(len(tlStack.tracks) == 6), "Number of tracks for stack display mode not matched"
        # assert(len(tlInline.tracks) == 2), "Number of tracks for inline display mode not matched"
        # assert(len(tlFull.tracks) == 5), "Number of tracks for full display mode not matched"
        # assert(bogus is None), "Should have been invalid result"


if __name__ == '__main__':
    unittest.main()