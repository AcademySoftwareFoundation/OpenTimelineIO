# Shots Added or Removed From The Cut

**Status: Planned**

## Summary

The creative process of editing often involves adding, removing or replacing shots in a sequence. Other groups of people
working on the same project want to know about changes to the list of shots in use on a day to day basis. For example,
animators working on a shot should be informed if the shot they are working on has been cut from the sequence, so they
can stop working on it. Similarly, if new shots are added, animation should start working on those shots. Since the
creative decision about which shots are in or out of the cut comes from editorial, we can use OTIO to communicate these
changes.

## Example
Editorial is working on a short film in Avid Media Composer. They have several bins of media with live action footage,
rendered animation clips, dialogue recordings, sound effects and music. The lead editor is actively working on the cut
for the short film over the course of a few weeks. At the same time, the animation department is actively working on
the animated shots for the film. As revisions are made to the animated shots, rendered clips are delivered to editorial
with a well established naming convention. On a daily basis, an EDL or AAF is exported from Media Composer and passed
to the animation department so they can stay up to date with the current cut.

In each revision of the cut, Animation wants to know which shots have been added or removed. They run a Python script
which uses OpenTimelineIO to read an EDL or AAF from editorial and produces a list of video clip names found in the cut.
Some of these names match the animation department's shot naming convention - or contain shot tracking metadata - and
can be compared to existing shots that the animators are working on.

If there are shots being animated that are not in this cut, then animation can stop working on those shots, as they are
no longer needed.

When the editor wants to request a new shot with a new camera angle or new animation, he or she can duplicate an existing
clip and give it a new name, or insert a placeholder with a previously unused name, or otherwise flag the new clip as a
request for a new shot. When animation sees this newly requested shot in the cut, they can respond as appropriate and
deliver the new shot to editorial when it is ready.

## Features Needed in OTIO

- EDL reading (done)
    - Clip names across all tracks
- [AAF reading](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/issues/1)
    - Clip names across all tracks, subclips, etc.
- Timeline should include (done)
    -  a Stack of tracks, each of which is a Sequence
- Sequence should include (done)
    - a list of Clips
- Clips should include (done)
    - Name
    - Metadata

## Features of Python Script

- Use OTIO to read the EDL or AAF. (done)
- Iterate through every Clip in the Timeline, printing its name. (done)
- Compare these names to the shots in a production tracking system.