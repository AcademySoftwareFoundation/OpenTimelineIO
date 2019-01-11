# Time Scopes

<!-- TODO: should 'internal space' be called "available space" -->

## Introduction

OpenTimelineIO represents a 1-dimensional coordinate space with many of the
features associated with computer graphics 3-dimensional spaces, including
transformations and named coordinate frames.

Understanding these transformations and scopes is needed for being able to ask
reasonable questions of the library and understand its results.  The hope is that
you can use the design outlined in this document to ask questions like:

- "What frame of media is playing during the nth frame in the top timeline?"
- "Which frames need to be rendered overnight for today's cut?"
- "Given a clip in a video track, which segments of audio correspond to it?"

This document proposes a scheme for named coordinate frames for OpenTimelineIO
that are useful for the implementation and inspection of editorial systems.

It is inspired by this document:
https://renderman.pixar.com/resources/RenderMan_20/appnote.10.html

## A Simple Example file

Taking a simple example first, this file has a single track, with a single clip
with a media reference in it.

`TODO: CREATE DIAGRAM`

## The Pattern

Objects in OpenTimelineIO apply a transform from an "Internal" space, described 
by children or referenced objects, to an "External" space, which runs from the 
origin to the final duration of the object.

## Media Reference / Media Space

The media reference has an `available_range`, which is in the space of the media
that is being referenced.  We call this `Media Space`.  Its external space is this
space.

For example, if the media being referenced has a starting timecode of one hour,
and goes for another hour, the `available_range` for this reference should have
start frame of one hour and duration of one hour.  _NOT_ a start frame of zero
and a duration of one hour.

## Item Spaces

### Internal Space

Items inherit an "internal" space from their children or media references.  They
then perform a series of transformations on those spaces

This may be "None".

### Trimmed Space

Origin: the start_time of the `source_range` becomes the origin of Trimmed Space.

### Effects Space

The effects space is the frame after the effects have been applied.

### External Space

The external space is finally achieved by applying the transitions to the effects
space.

## Timeline / Global Space

The timeline's "internal" space is the "external" space of its "tracks" stack.

The timeline additionally  has a 'global_offset' which is used to set the final
starting time of the global space of the timeline.

## Clip / Media Space

The clip's "internal" space is the "Media Space" of its media reference, so a convienent alias is provided.

# Time Occupied vs Frames Displayed

There is a distinction between the time something occupies on a timeline and the
frames that it displays.

For example, take a simple example.  A timeline with a single track containing 
a single clip, that has a duration of 20 frames.  The parent also has a source 
range of 0-20, exactly the same as the time this clip occupies.

Now imagine that a freeze frame effect is added to the clip, so that only the 
first frame of the clip is used.

The clip still occupies frames 0-20 of the parent timeline, but only frame 0 of
the clip is being used.

# API

## Specifying a Coordinate Space

You can use the utility methods on various objects to generate references to their
coordinate space, for example:

- `some_clip.internal_space()`
- `some_clip.trimmed_space()`
- `some_clip.external_space()`
- `some_timeline.global_space()`

This produces a `FrameReference`, which has a pointer back to the original object
as well as an enum for which frame you wanted to reference on that object.

## Pattern

The default space, when none is specified for a given operation, is the "External
 Trimmed".  For example, these two calls are the same:

- `some_clip.duration()`
- `some_clip.duration(some_clip.trimmed_space())`

## Range

To query the range of an object, there is a method (like `.duration()`).

These are the same:
- `some_clip.range()`
- `some_clip.range(some_clip.external_space())`

These are the same:
- `some_clip.range(some_clip.internal_space())`
- `otio.algorithms.transform_time_range(some_clip.external_space(), some_clip.range(), some_clip.internal_space())`

## Transforming Time from One Scope to Another

Functions you can use to query or transform time:

- `otio.algorithms.transform_time(from_space, t, to_space)`

For example, to translate a time from the global space of a timeline to the 
media space of one of its items:

- `otio.algorithms.transform_time(some_timeline.global_space(), t, some_clip.media_space())`

### Notes to self

The transformations of the hierarchy:
- normal transformation stack (offset, scale)
- trimming (ie I want to know that I would get frame -10, not just get back a Null frame or something)

# Use Cases

## "What frame of media is playing during the nth frame in the top timeline?"

```python
some_frame = otio.opentime.RationalTime(86410, 24)
clip_that_is_playing = some_timeline.tracks.top_clip_at_time(some_frame)

result = otio.algorithms.transform_time(
    some_timeline.external_space(),
    some_frame,
    clip_that_is_playing.media_reference.media_space()
)
```

## "Which frames need to be rendered overnight for today's cut?"

Lets take a simple version of this, "For a clip in a timeline, which frames of that clip appear in the top level timeline?"

```python
some_clip.range(1

