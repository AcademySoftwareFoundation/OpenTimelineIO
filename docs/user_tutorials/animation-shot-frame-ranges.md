# Animation Shot Frame Ranges Changed

**Status: Planned**

## Summary

This case is very similar to the
[](/use-cases/shots-added-removed-from-cut).
The editorial and animation departments are working with a sequence of shots simultaneously over the course of a few
weeks. The initial delivery of rendered video clips from animation to editorial provides enough footage for the
editor(s) to work with, at least as a starting point. As the cut evolves, the editor(s) may need more frames at the
head or tail of some shots, or they may trim frames from the head or tail that are no longer needed. Usually there is
an agreement that some extra frames, called handles, should be present at the head and tail of each shot to give the
editors some flexibility. In the case where the editors need more frames than the handles provide, they might use a
freeze frame effect, or a slow down effect to stretch the clip, or simply repeat a segment of a clip to fill the gap.
This is a sign that new revisions of those shots should be animated and rendered with more frames to fill the needs of
the cut. Furthermore, as the sequence nears completion, the cut becomes more stable and the cost of rendering frames
becomes higher, so there is a desire to trim unused handles from the shots on the animation side. In both cases, we
can use OTIO to compare the frame range of each shot between the two departments.

## Example
Animation delivers the first pass of 100 shots to editorial. Editorial makes an initial cut of the sequence. In the cut,
several shots are trimmed down to less than half of the initial length, but 2 shots need to be extended. Editorial
exports an EDL or AAF of the sequence from Avid Media Composer and gives this cut to the animation department. Animation
runs a Python script which compares the frame range of each shot used in the cut to the frame range of the most recent
take of each shot being animated. Any shot that is too short must be extended and any shot that is more than 12 frames
too long can be trimmed down. The revised shots are animated, re-rendered and re-delivered to editorial. Upon receiving
these new deliveries, editorial will cut them into the sequence (see also
[](/use-cases/conform-new-renders-into-cut)).
For shots that used timing effects to temporarily extend them, those effects can be removed, since the new version of
those shots is now longer.

## Features Needed in OTIO

- EDL reading
    - Clip names for video track
    - Source frame range for each clip
    - [Timing effects](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/issues/39)
- [AAF reading](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/issues/1)
    - Clip names across all video tracks, subclips, etc.
    - Source frame range for each clip
    - Timing effects
- Timeline should include (done)
    -  a Stack of tracks, each of which is a Sequence
- Sequence should include (done)
    - a list of Clips
- Clips should include (done)
    - Name
    - Metadata
    - Timing effects
- [Timing effects](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/issues/39)
    - Source frame range of each clip as effected by timing effects.
- Composition
    - Clips in lower tracks that are obscured (totally or partially) by overlapping clips in higher tracks are considered trimmed or hidden.
    - Visible frame range for each clip.

## Features of Python Script

- Use OTIO to read the EDL or AAF
- Iterate through every Clip in the Timeline, printing its name and visible frame range