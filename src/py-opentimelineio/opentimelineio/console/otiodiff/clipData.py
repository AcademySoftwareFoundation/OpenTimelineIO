import opentimelineio as otio

# TODO: clip comparable??? ClipInfo
# source clip or clip ref?

class ClipData:
    """ClipData holds information from an OTIO clip that's necessary for
    comparing differences. It also keeps some information associated with
    the clip after comparisons are made, such as a matched ClipData and a note
    about what has changed.
    
    source_clip = original OTIO clip the ClipData represents
    full_name = full name of source_clip
    name and version splits full_name on space
    ex: full_name: clipA version1, name: clipA, version: version1
    """

    full_name = ""
    name = ""
    version = None    # currently not used in comparisons
    media_ref = None
    source_range = otio.opentime.TimeRange()
    timeline_range = otio.opentime.TimeRange()
    track_num = None    # not originally stored in otio.schema.Clip
    source_clip = otio.schema.Clip()
    # everything below holds comparison result info
    note = ""
    matched_clipData = None

    def __init__(self, source_clip, track_num, note=None):
        self.full_name = source_clip.name
        self.name = self.splitFullName(source_clip)[0]
        self.version = self.splitFullName(source_clip)[1]
        self.media_ref = source_clip.media_reference
        self.source_range = source_clip.source_range
        self.timeline_range = source_clip.trimmed_range_in_parent()
        self.track_num = track_num
        self.source_clip = source_clip
        self.note = note

    # split full name into name of clip and version by white space
    # uses structure of "clipA v1" where clipA is the name and v1 is the version

    def splitFullName(self, clip):
        """Split full name into name and version"""
        shortName = clip.name.split(" ")[0]
        version = clip.name.split(" ")[1] if len(clip.name.split(" ")) > 1 else None

        return shortName, version

    def printData(self):
        """Prints to console all parameters of ClipData"""
        print("name: ", self.name)
        print("version: ", self.version)
        print("media ref: ", self.media_ref)
        print("source start time: ", self.source_range.start_time.value,
              " duration: ", self.source_range.duration.value)
        print("timeline start time:", self.timeline_range.start_time.value,
              " duration: ", self.timeline_range.duration.value)
        if (self.note != ""):
            print("note: ", self.note)
        print("source clip: ", self.source.name)

    def sameName(self, cA):
        """Compare names and returns if they are the same"""
        if (self.name.lower() == cA.name.lower()):
            return True
        else:
            return False

    # note: local and source duration should always match, can assume same
    def sameDuration(self, cA):
        """Compare duration within the timeline of this ClipData
        against another ClipData"""
        return self.timeline_range.duration.value == cA.timeline_range.duration.value


    def checkSame(self, cA):
        """Check if this ClipData is the exact same as another ClipData or if
        it's the same just moved along the timeline. Updates note based on edits"""
        isSame = False
        # check names are same
        if self.sameName(cA):
            # check source range is same
            # TODO: make test where has null source range -> see things break,
            # then go back and change <- low priority
            if (self.source_range == cA.source_range):
                # print(self.name, " ", self.timeline_range, " ", cA.timeline_range)
                # check in same place on timeline
                if (self.timeline_range == cA.timeline_range):
                    isSame = True
                    # check duration is same but not necessarily in same place
                    # on timeline
                # TODO: change to else? (does the elif always run?)
                elif (self.sameDuration(cA)):
                    # Note: check in relation to left and right?
                    #       know if moved in seq rather than everything shifted over
                    # because of lengthen/shorten of other clips
                    isSame = True
                    self.note = "shifted laterally in track"
            else:
                # print("source range different", cA.name, self.name)
                # print(self.media_ref)
                # print(self.media_ref.target_url)
                pass

        return isSame

    def checkEdited(self, cA):
        """Compare 2 ClipDatas and see if they have been edited"""
        isEdited = False

        # Note: assumption that source range and timeline range duration always equal
        # assert(self.source_range.duration.value == self.timeline_range.duration.value
        # ), "clip source range and timeline range durations don't match"
        # assert(cA.source_range.duration.value == cA.timeline_range.duration.value
        # ), "clip source range and timeline range durations don't match"

        selfDur = self.source_range.duration
        cADur = cA.source_range.duration

        selfSourceStart = self.source_range.start_time
        cASourceStart = cA.source_range.start_time

        # clip duration same but referencing different areas on the same timeline
        # if selfDur.value == cADur.value:
        #     if (self.source_range.start_time != cA.source_range.start_time):
        #         # print("source range dif between: ", self.name, "and", cA.name)
        #         # self.printData()
        #         # cA.printData()
        #         self.note = "source range start times differ"
        #         isEdited = True

        if (self.source_range != cA.source_range):
            self.note = "source range changed"
            isEdited = True
            deltaFramesStr = str(abs(selfDur.to_frames() - cADur.to_frames()))

            if (selfDur.value == cADur.value):
                self.note = "start time in source range changed"

        # TODO: put note assignment into function, return note?
        # self, other, olderClipData rather than cA
            # clip duration shorter
            elif (selfDur.value < cADur.value):
                self.note = "trimmed " + deltaFramesStr + " frames"

                if (selfSourceStart.value == cASourceStart.value):
                    self.note = "trimmed tail by " + deltaFramesStr + " frames"
                elif (selfSourceStart.value < cASourceStart.value):
                    self.note = "trimmed head by " + deltaFramesStr + " frames"

            # clip duration longer
            elif (selfDur.value > cADur.value):
                self.note = "lengthened " + deltaFramesStr + " frames"

                if (selfSourceStart.value == cASourceStart.value):
                    self.note = "lengthened tail by " + deltaFramesStr + " frames"
                elif (selfSourceStart.value > cASourceStart.value):
                    self.note = "lengthened head by " + deltaFramesStr + " frames"

        return isEdited
