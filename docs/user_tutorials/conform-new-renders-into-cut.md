# Conform New Renders Into The Cut

**Status: Done**
This use case is in active use at several feature film production studios.

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
