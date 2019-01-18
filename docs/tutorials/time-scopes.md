# Time Scopes

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

# Objects

## The Pattern

We say objects have an "internal" space, which is the space they inherit from
their children or media reference, and an "external" space, which is the space
after the transformations they provide.  They also implement additional 
intermediate spaces, or we provide more descriptive synonyms for useful spaces.

## Media Reference

The leaf-most object in an OpenTimelineIO hierarchy is the `MediaReference`, which
is OpenTimelineIO's way at pointing at media.

It defines an `availabe_range` field, which is in the space of the media that is
being referenced.  We refer to this space as `media_space`, and can access it 
with the `.media_space()` method. 

For example, if the media being referenced has a starting timecode of one hour,
and goes for another hour, the `available_range` for this reference should have
start frame of one hour and duration of one hour.  _NOT_ a start frame of zero
and a duration of one hour.

## Items

Instances of `Item` define objects in the OpenTimelineIO composition hierarchy 
with time scopes.

### Internal Space

Instances of `Item` inherit an `internal_space` from their children or media 
references.  They perform a series of transformations on those spaces

The `internal_space` of an `Item` may be `None` if it has no `source_range` or
`media_reference`.

For clips, the `internal_space` is the `media_space` of the `media_reference`,
and for compositions, `internal_space` starts at 0 and inherits the duration
from its children (depending on the kind of composition).

### Trimmed Space

If set, the `source_range` is expressed in the `internal_space` and trims the 
`available_range`, which is inherited from the `MediaReference` (for `Clip`s) or
from children (for subclasses of `Composition`).

The `trimmed_space` is the space after this trim.  If `source_range` is `None`,
`internal_space` and `trimmed_space` are the same.

Origin: the `start_time` of the `source_range` becomes the origin of 
`trimmed_space`.

### Effects Space

The `effects_space` is the space after the effects have been applied.

### External Space

*TODO: debate around moving transition information onto the track.*

The `external_space` is finally achieved by applying the transitions to the effects
space.

## Timeline

The timeline additionally defines a `global_space`, which the space resulting
from applying the `global_offset` parameter to the `external_space` of the `tracks`
stack.

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

This produces a `FrameReference`, which has a pointer back to the original object
as well as an enum for which frame you wanted to reference on that object.

## Transforming Time from One Scope to Another

Functions you can use to query or transform time:

- `otio.algorithms.transform_time(from_space, t, to_space)`

For example, to translate a time from the global space of a timeline to the 
media space of one of its items:

- `otio.algorithms.transform_time(some_timeline.global_space(), t, some_clip.media_space())`

If the translate or trim functions return a `None`, that means that the time is
trimmed out entirely from the parent scopes.

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

