import unittest
import opentimelineio as otio

from opentimelineio.console.otiodiff.clipData import ClipData
import opentimelineio.console.otiodiff.makeOtio as makeOtio
import opentimelineio.console.otiodiff.getDiff as getDiff

from collections import namedtuple


class TestClipData(unittest.TestCase):
    # check if the names of two ClipDatas are the same
    def test_same_name(self):
        clipA = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        assert(clipA.sameName(clipB))

    def test_different_name(self):
        clipA = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("testName2",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        assert(not clipA.sameName(clipB))


    def test_same_duration(self):
        # check that length of clip is the same
        clipA = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("testName2",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        assert(clipA.sameDuration(clipB))

    def test_different_duration(self):
        # check that length of clip is the different
        clipA = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(duration=otio.opentime.RationalTime(100,1)),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("testName2",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        assert(not clipA.sameDuration(clipB))


    def test_check_same(self):
        # check that two exact same clips are the same
        # check that two exact same clips but moved in the timeline are the same
        clipA = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        
        assert clipA.checkSame(clipB)

    def test_check_not_same(self):
        # check that two exact same clips are the same
        # check that two exact same clips but moved in the timeline are the same
        clipA = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("testName2",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        
        assert not clipA.checkSame(clipB)
        assert clipA.note is None

    def test_check_not_same2(self):
        # check that two exact same clips are the same
        # check that two exact same clips but moved in the timeline are the same
        clipA = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(duration=otio.opentime.RationalTime(100,1)),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        
        assert not clipA.checkSame(clipB)
        assert clipA.note is None

    def test_check_not_same3_moved(self):
        # check that two exact same clips are the same
        # check that two exact same clips but moved in the timeline are the same
        clipA = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(start_time=otio.opentime.RationalTime(100,1)),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        
        assert clipA.checkSame(clipB)
        assert clipA.note == "moved"

    def test_check_Edited(self):
        # check for trim head/tail and lengthen head/tail
        clipA = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(start_time=otio.opentime.RationalTime(0,1)),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("testName",
                    "testMR.mov",
                    otio.opentime.TimeRange(start_time=otio.opentime.RationalTime(100,1)),
                    otio.opentime.TimeRange(),
                    otio.schema.Clip(),
                    "testTake")
        
        assert clipA.checkEdited(clipB)
        assert clipA.note == "start time changed"

class TestGetDif(unittest.TestCase):
    def test_find_clones(self):
        clipA = ClipData("clipA",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(0, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("clipB",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(10, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipC = ClipData("clipC",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(20, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipCClone = ClipData("clipC",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(30, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipD = ClipData("clipD",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(40, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        
        testClips = [clipA, clipB, clipC, clipCClone, clipD]
        clones, nonClones = getDiff.findClones(testClips)

        correctClones = {clipC.name: [clipC, clipCClone]}
        correctNonClones = [clipA, clipB, clipD]

        assert(clones == correctClones), "Not all cloned clips correctly identified"
        assert(nonClones == correctNonClones), "Not all unique clips correctly identified"


    def test_sort_clones_clones_in_both(self):
        # SETUP
        clipA = ClipData("clipA",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(0, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipB = ClipData("clipB",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(10, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipC = ClipData("clipC",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(20, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipCClone = ClipData("clipC",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(30, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipD = ClipData("clipD",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(0, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipDatasA = [clipA, clipB, clipC, clipCClone]
        clipDatasB = [clipB, clipC, clipCClone, clipD]

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
        clipA = ClipData("clipA",
                "testMR.mov",
                otio.opentime.TimeRange(),
                otio.opentime.TimeRange(otio.opentime.RationalTime(0, 24), otio.opentime.RationalTime(10, 24)),
                otio.schema.Clip(),
                "testTake")
        clipB = ClipData("clipB",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(10, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipC = ClipData("clipC",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(20, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipCClone = ClipData("clipC",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(30, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipD = ClipData("clipD",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(0, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipDatasA = [clipA, clipB, clipC, clipCClone]
        clipDatasB = [clipA, clipB, clipD]

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
        clipA = ClipData("clipA",
                "testMR.mov",
                otio.opentime.TimeRange(),
                otio.opentime.TimeRange(otio.opentime.RationalTime(0, 24), otio.opentime.RationalTime(10, 24)),
                otio.schema.Clip(),
                "testTake")
        clipB = ClipData("clipB",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(10, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipC = ClipData("clipC",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(20, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipCClone = ClipData("clipC",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(30, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipD = ClipData("clipD",
                    "testMR.mov",
                    otio.opentime.TimeRange(),
                    otio.opentime.TimeRange(otio.opentime.RationalTime(0, 24), otio.opentime.RationalTime(10, 24)),
                    otio.schema.Clip(),
                    "testTake")
        clipDatasA = [clipA, clipB, clipC, clipCClone]
        clipDatasB = [clipB, clipC, clipD]

        # EXERCISE
        sortedClonesA, sortedClonesB = getDiff.sortClones(clipDatasA, clipDatasB)

        # VERIFY 
        clonesA, nonClonesA = sortedClonesA
        clonesB, nonClonesB = sortedClonesB
        
        assert(len(clonesA) == 1), "Number of clones found in trackA doesn't match"
        assert(len(nonClonesA) == 2), "Number of non-clones found in trackA doesn't match"
        assert(len(clonesB) == 1), "Number of clones found in trackB doesn't match"
        assert(len(nonClonesB) == 2), "Number of non-clones found in trackB doesn't match"

class TestMakeOtio(unittest.TestCase):
    # Test the type parameter to makeTimelineOfType, but not the detailed results.
    def test_make_timeline_type(self):
        # SETUP
        trackA = otio.schema.Track()
        trackB = otio.schema.Track()
        pass

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