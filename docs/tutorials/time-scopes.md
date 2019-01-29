# Time Coordinate Spaces

## Introduction

OpenTimelineIO represents a 1-dimensional coordinate system with many of the
features associated with computer graphics 3-dimensional systems, including
transformations and a hierarchy of named coordinate spaces.

This document's goal is to explain the transformations and spaces that 
OpenTimelineIO exposes to help you answer questions like:

- "What frame of media is playing during the nth frame in the top timeline?"
- "Which frames need to be rendered overnight for today's cut?"
- "Given a clip in a video track, which segments of audio correspond to it?"

This document is inspired by this very useful document from the Renderman 
documentation:
https://renderman.pixar.com/resources/RenderMan_20/appnote.10.html

This document also assumes familiarity with the objects in an OpenTimelineIO
hierarchy.

## A Simple Example file

Taking a simple example first, this file has a single track, with a single clip
with a media reference in it.

`TODO: CREATE DIAGRAM`

# Math Classes

## `CoordinateSpaceReference`

The `CoordinateSpaceReference` class is used to refer to a specific named
coordinate space on a specific object.  For example, the `Item` class defines a
`TrimmedCoordinateSpace` named coordinate space.  The method `trimmed_space` on
`Item` will return a `CoordinateSpaceReference`, which has a weak reference to
the `Item` and an enum for `TrimmedCoordinateSpace`.

These `CoordinateSpaceReference` objects are passed to functions to indicate
the space a time range is coming from or to be transformed into.

## `TimeTransformFunction` and `TimeTransformMatrix`: Transformations Between
## Named Coordinate Spaces

Editorial timelines are unlike 3 dimensional coordinate systems in that they
typically involve non-linear transformations on time (for example: freeze
frames, speed ramps).  OpenTimelineIO abstracts this concept with the
`TimeTransformFunction` class.  `TimeTransformFunction` objects represent
1-dimensional *INVERTIBLE* functions that map an input domain to an output
range.  The input domain is made of discrete input frame to output mappings,
between which output mappings are linearly interpolated (or an
interpolant is provided).

In python, this is encoded with a dictionary where the keys are the input
frames and the values are the output frame values.  `TimeTransformFunction` 
objects also encode a `interpolant` enum for choosing an interpolation function.

Use the `*` operator to apply `TimeTransformFunction` objects to `RationalTime`
or other `TimeTransformFunction` objects (including `TimeTransformMatrix`,
described below.

For purely linear transfomrations, the `TimeTransformMatrix` in OpenTimelineIO is
a 1-dimensional homogenous coordinates transformation matrix.  This means it
encodes offset (a `RationalTime`) and scale (a number).  It can be applied to
`RationalTime`, `TimeRange`, or other `TimeTransform` objects by using the `*`
(`__mul__`) operator.  Most of the methods described in this document will
compute and concatenate `TimeTransform` objects internally, but these matrices
can be referenced directly if need be.

# Named Coordinate Spaces on Objects

This section describes what coordinate spaces various OpenTimelineIO objects 
define are and how to access them.

## `MediaReference`

The leaf-most object in an OpenTimelineIO hierarchy is the `MediaReference`, 
which is OpenTimelineIO's way of referencing external media.

The only named coordinate space defined by the `MediaReference` class is the
`media_space`, which is the coordinate space of the media that is being
referenced.  This space is the space that the `available_range` property is
defined in.

For example, if the media being referenced has a starting timecode of one hour,
and goes for another hour, and the intent is to make this entire range
available, the `available_range` for this reference should have start frame of
one hour and duration of one hour.  _NOT_ a start frame of zero and a duration
of one hour.

If the `available_range` is not set, than the `media_space()` method will return
`None`.  

## Items

<!-- todo: how to handle the 'rate' of a space for which there are mutliple children, since we don't define a specific rate on objects. -->
<!-- todo: "available_space" might be a better name than internal space -->

Items are objects go into the composition hierarchy.  They define a number of coordinate spaces.

### Internal Space

The `internal_space` is defined by the child object.

- `Clip`: the `internal_space` of a Clip is the `media_space` of its `media_reference`.
- `Sequence`: the `internal_space` of a sequence starts at 0 and has a duration that is the sum of the durations of all of the children of the `Sequence`.
- `Stack`:  the `internal_space` of a `Stack` starts at 0 and has a duration equal to that of the longest child.

In other words, the transform from the `external_space` or `media_space` of the 
child object to the `internal_space` of the `Item` should be an identity 
transform matrix.

The `source_range` property trims this space.  For example, if a `Clip` has a
`MediaReference` with an `available_range` that starts at frame 100 and have a
duration of 100 frames, a `source_range` on the `Clip` that trims 10 frames off
the front and back would start at frame 110 and have a duration of 80 frames.

### Trimmed Space

The transform from the `internal_space` to the `trimmed_space` is a matrix with
the offset equal to the `start_time` of the `source_range` of the item and a
scale of one.  If the `source_range` is not set, than the transform matrix will
be an identity.  

This makes the origin of this space the `start_time` of the
`source_range` if set and otherwise the origin of the `internal_space` if not
set.

### Effects Space

The `effects_space` is the space after the effects have been applied.  To
compute the transformation matrix from `trimmed_space` to `effects_space`, the
item walks through its effects and concatenates all the transformation
matrices.

### External Space

*TODO: debate around moving transition information onto the track.*

The `external_space` is finally achieved by applying the transitions to the
effects space.

## Timeline

The timeline additionally defines a `global_space`, which is the final, top
level space of the timeline.  The transformation matrix from the
`external_space` of the `tracks` `Stack` has: 

- offset: `timeline.global_offset` 
- scale: 1.0

This is useful for starting the entire resulting timeline at an hour, for example.

# Time Occupied vs Frames Displayed

There is a distinction between the time something occupies on a timeline and the
frames that it displays.

For example, a timeline with a single track containing a single clip, that has 
a duration of 20 frames.  The parent also has a source range of 0-20.  In this 
case the media_range and the occupied_range of the clip are identical.

Now imagine that a freeze frame effect is added to the clip, so that only the 
first frame of the clip is used.

The clip still occupies frames 0-20 of the parent timeline, but only frame 0 of
the clip is being used.  The media_range of the clip therefore has a duration of
1, while the occupied_range has a duration of 20.

# API

## Specifying a Coordinate Space

You can use the utility methods on various objects to generate references to their
coordinate space, for example:

- `some_clip.internal_space()`
- `some_clip.trimmed_space()`
- `some_clip.external_space()`
- `some_timeline.global_space()`

These functions return a `CoordinateSpaceReference` struct, which contain both
a pointer back to the object on which the coordinate space is to be computed,
as well as an enum for which coordinate space you wanted to reference on that 
object.  Functions that transform time use instances of 
`CoordinateSpaceReference` to compute transforms and apply any relevant trims
or effects.

## Transforming Time from One Coordinate Space to Another

Functions you can use to query or transform time:

- `otio.algorithms.transform_time(from_space, t, to_space)`

For example, to translate a time from the global space of a timeline to the 
media space of one of its items:

- `otio.algorithms.transform_time(some_timeline.global_space(), t, some_clip.media_space())`

If the translate or trim functions return a `None`, that means that the time is
trimmed out entirely from the parent coordinate spaces.

Note that these operations do not take compositing into account.  A clip may be
occluded by something, or be transparent, and these functions will not be able
to take that into account.  They only take time operations into account.

## Pattern

You can query objects for their named spaces.

- `MediaReference`: `media_space`
- `Item`: `internal_space`, `trimmed_space`, `effects_space`, `external_space`
- `Clip`: `Item` spaces, as well as: `media_space` (a convienence for the `media_reference.media_space`)
- `Timeline`: `global_space`

In addition to the properties that define the trimming ranges and so on of the 
objects, `Item`, `Clip`, and `MediaReference` implement methods that let you 
query their ranges:

- `media_range()`: The range of media used, as described above.
- `occupied_range()`: The range of time this clip occupies.

Both of these methods take a convienence method which is the space that to transform and trim the result into.

For example:

- The frames of media used in the space of the top level timeline: `some_clip.media_range(some_timeline.global_space())`
- The range in the parent track that a clip occupies: `some_clip.occupied_range(some_clip.parent().trimmed_space())`

The default space, when none is specified for a given operation, is the 
`external_space`.  For example, these return the same result:

- `some_clip.duration()`
- `some_clip.duration(some_clip.external_space())`

and these return the same result:
- `some_clip.media_range()`
- `some_clip.media_range(some_clip.external_space())`

# Use Case Example Code

## "What frame of media is playing during the nth frame in the top timeline?"

```python

some_frame = otio.opentime.RationalTime(86410, 24)
clip_that_is_playing = some_timeline.tracks.top_clip_at_time(some_frame)

result = otio.algorithms.transform_time(
    some_frame,
    some_timeline.global_space(),
    clip_that_is_playing.media_reference.media_space()
)

# results
media_that_is_playing = clip_that_is_playing.media_reference
frame_that_is_playing = result
```

## "Which frames need to be rendered overnight for today's cut?"

```python

flat_tl = otio.algorithms.flattened_timeline(some_timeline)

needs_to_be_rendered = []

for child_clip in flat_tl.each_clip():
    required_range = child_clip.media_range(
        flat_tl.global_space(),
        # are there cases where trim is false?
        # trim=True
    )

    needs_to_be_rendered.append((child_clip.media_reference, required_range))
```

## "Given a clip in a timeline, which segments of audio overlap with it in time?"

```python

clip_range_in_tl = some_clip.occupied_range(some_timeline.global_space())

clips_that_overlap = some_timeline.each_clip(search_range=clip_range_in_tl)

overlapping_audio_clips = []
for cl in clips_that_overlap:
    # only find overlapping audio clips.
    if cl.parent.kind == otio.schema.TrackKind.Audio:
        overlapping_audio_clips.append(cl)
```

## (EDL Example) "How can I compute EDL's 'source time' and 'record time'?"


```python
# the edl has a source range which is the media time that is being used
mr_in_tl = clip.media_range(in_space=tl.global_space(), trim = True)

# transform the result back to media space
edl_source_range = otio.algorithms.transform(
    mr_in_tl,
    tl.global_space(),
    clip.media_reference.space()
    trim = False
)
line.source_in = edl_source_range.start_time
line.source_out= edl_source_range.end_time_exclusive()

record_range = clip.occupied_range(tl.global_space(), trim = True)
line.record_in = record_range.start_time
line.record_out = record_range.end_time_exclusive()
```
