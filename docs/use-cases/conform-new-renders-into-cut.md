# Conform New Renders Into The Cut

**Status: Done**
This use case is in active use at Pixar (Coco, Incredibles 2, etc.)

## Summary

Artists working on the animation or visual effects for shots in a sequence often want to view their in-progress work in the context of a current cut of the film. This could be accomplished by importing their latest renders into the editing system, but that often involves many steps (e.g. transcoding, cutting the clips into the editing system, etc.) Instead, the artists would like to preview the cut with their latest work spliced in at their desk.

## Workflow
* In Editorial:
1. Export an EDL from the editorial system (Media Composer, Adobe Premiere, Final Cut Pro X, etc.)
2. Export a QuickTime audio/video mixdown that matches that EDL
3. Send the EDL+ QuickTime to the animators or visual effects artists
* At the Artist's Desk:
1. Open the EDL+QuickTime in a video player tool (RV, etc.)
2. Either:
2a. Use OpenTimelineIO to convert the EDL to OTIO or
2b. A plugin in the video player tool uses OpenTimelineIO to read the EDL.
3. In either case, we link the shots in the timeline to segments of the supplied QuickTime movie.
3. The artist can now play the sequence and see exactly what the editor saw.
4. The artist can now relink any or all of the shots to the latest renders (either via OpenTimelineIO or features of the video player tool)

## Features Needed in OTIO

- EDL reading (done)
    - Single video track (done)
    - Clip names (done)
    - Source range for each clip (done)
    - <a href="https://github.com/PixarAnimationStudios/OpenTimelineIO/issues/6" target="_blank">Transitions</a> (done)
- RV support
    - <a href="https://github.com/PixarAnimationStudios/OpenTimelineIO/issues/64" target="_blank">OTIO to RV Session file via adapter</a> (done)
    - RV Plugin that uses OTIO to read an EDL (Pixar has use-case specific code for this) (done)
- Relinking
    - <a href="https://github.com/PixarAnimationStudios/OpenTimelineIO/issues/94" target="_blank">Relinking the whole EDL to segments of the full sequence QuickTime movie.</a> (done)
    - <a href="https://github.com/PixarAnimationStudios/OpenTimelineIO/issues/94" target="_blank">Relinking of individual clips to renders of those shots.</a>(done)