import opentimelineio as otio

class ClipData:
    name = ""
    take = None
    media_ref = None
    source_range = otio.opentime.TimeRange()
    timeline_range = otio.opentime.TimeRange()
    note = ""
    source = otio.schema.Clip()
    pair = None

    def __init__(self, name, media_ref, source_range, timeline_range, source, take=None, note=None):
        self.name = name
        self.media_ref = media_ref
        self.source_range = source_range
        self.timeline_range = timeline_range
        self.source = source
        self.take = take
        self.note = note

    def printData(self):
        print("name: ", self.name)
        print("take: ", self.take)
        print("media ref: ", self.media_ref)
        print("source start time: ", self.source_range.start_time.value, " duration: ", self.source_range.duration.value)
        print("timeline start time:", self.timeline_range.start_time.value, " duration: ", self.timeline_range.duration.value)
        if(self.note != ""):
            print("note: ", self.note)
        print("source clip: ", self.source.name)

    # compare truncated names
    def sameName(self, cA):
        if(self.name.lower() == cA.name.lower()):
            return True
        else:
            return False
        
    # note: local and source duration should always match, can assume same
    # compare the duration within the timeline for 2 clips
    def sameDuration(self, cA):
        if(self.timeline_range.duration.value == cA.timeline_range.duration.value):
            return True
        else:
            return False

    # compare 2 clips and see if they are the exact same, whether exact or moved along
    # the timeline
    def checkSame(self, cA):
        isSame = False
        # check names are same
        if(self.sameName(cA)):
            # check source range is same
            if(self.source_range == cA.source_range):
                # print(self.name, " ", self.timeline_range, " ", cA.timeline_range)
                # check in same place on timeline
                if(self.timeline_range == cA.timeline_range):
                    isSame = True
                    # check duration is same but not necessarily in same place on timeline
                elif(self.sameDuration(cA)):
                    # Note: check in relation to left and right?
                    #       know if moved in seq rather than everything shifted over because of lengthen/shorten of other clips
                    isSame = True
                    self.note = "moved"
            else:
                # print("source range different", cA.name, self.name)
                # print(self.media_ref)
                # print(self.media_ref.target_url)
                pass

        return isSame
    
    # compare 2 clips and see if they have been 
    # compare self: "new", to old
    def checkEdited(self, cA):
        isEdited = False

        # Note: assumption that source range and timeline range duration always equal
        assert(self.source_range.duration.value == self.timeline_range.duration.value), "clip source range and timeline range durations don't match"
        assert(cA.source_range.duration.value == cA.timeline_range.duration.value), "clip source range and timeline range durations don't match"

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

        if(self.source_range != cA.source_range):
            self.note = "source range changed"
            isEdited = True
            deltaFramesStr = str(abs(selfDur.to_frames() - cADur.to_frames()))

            if(selfDur.value == cADur.value):
                self.note = "start time changed"

            # clip duration shorter
            elif(selfDur.value < cADur.value):
                self.note = "trimmed " + deltaFramesStr + " frames"
            
                if(selfSourceStart.value == cASourceStart.value):
                    self.note = "trimmed tail by " + deltaFramesStr + " frames"
                elif(selfSourceStart.value < cASourceStart.value):
                    self.note = "trimmed head by " + deltaFramesStr + " frames"

            # clip duration longer
            elif(selfDur.value > cADur.value):
                self.note = "lengthened"

                if(selfSourceStart.value == cASourceStart.value):
                    self.note = "lengthened tail by " + deltaFramesStr + " frames"
                elif(selfSourceStart.value > cASourceStart.value):
                    self.note = "lengthened head by " + deltaFramesStr + " frames"

        return isEdited