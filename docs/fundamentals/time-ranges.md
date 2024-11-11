# Time Ranges

## Overview

A Timeline and all of the Tracks and Stacks it contains work together to place
the Clips, Gaps and Transitions relative to each other in time. You can think
of this as a 1-dimensional coordinate system. Simple cases of assembling Clips
into a Track will lay the Clips end-to-end, but more complex cases involve
nesting, cross-dissolves, trimming, and speed-up/slow-down effects which can
lead to confusion. In an attempt to make this easy to work with OpenTimelineIO 
uses the following terminology and API for dealing with time ranges.

Note: You probably also want to refer to [Timeline Structure](otio-timeline-structure.md).

## Clips

There are several ranges you might want from a Clip. For each of these, it is
important to note which time frame (the 1-dimensional coordinate system of time)
the range is relative to. We call these the "Clip time frame" and the "parent
time frame" (usually the Clip's parent Track).

### Ranges within the Clip and its media:

#### `Clip.available_range()`

The `available_range()` method on Clip returns a TimeRange that tells you
how much media is available via the Clip's `media_reference`. If a Clip 
points to a movie file on disk, then this should tell you how long that 
movie is and what timecode it starts at. For example: "wedding.mov" starts 
at timecode 01:00:00:00 and is 30 minutes long.

Note that `available_range()` may return `None` if the range is not known.

#### `Clip.source_range`

Setting the `source_range` property on a Clip will trim the Clip to only 
that range of media.

The `source_range` is specified in the Clip time frame.

Note that `source_range` may be `None` indicating that the Clip should use
the full `available_range()` whatever that may be. If both `source_range`
and `available_range()` are `None`, then the Clip is invalid. You need at
least one of those.

Usually this will be a shorter segment than the `available_range()` but this
is not a hard constraint. Some use cases will intentionally ask for
a Clip that is longer (or starts earlier) than the available media as a way
to request that new media (a newly animated take, or newly recorded audio) 
be made to fill the requested `source_range`.

#### `Clip.trimmed_range()`

This will return the Clip's `source_range` if it is set, otherwise it will
return the `available_range()`. This tells you how long the Clip is meant to
be in its parent Track or Stack.

The `trimmed_range()` is specified in the Clip time frame.

#### `Clip.visible_range()`

This will return the same thing as `trimmed_range()` but also takes any 
adjacent Transitions into account. For example, a Clip that is trimmed to 
end at frame 10, but is followed by a cross-dissolve with `out_offset` of 5
frames, will have a `visible_range()` that ends at frame 15.

The `visible_range()` is specified in the Clip time frame.

#### `Clip.duration()`

This is the way to ask for the Clip's "natural" duration. In `oitoview` or
most common non-linear editors, this is the duration of the Clip you will
see in the timeline user interface.

`Clip.duration()` is a convenience for `Clip.trimmed_range().duration()`.
If you want a
different duration, then you can ask for `Clip.available_range().duration()`
or `Clip.visible_range().duration()` explicitly. This makes it clear in your
code when you are asking for a different duration.

### Ranges of the Clip in its parent Track or Stack:

#### `Clip.range_in_parent()`

The answer to this depends on what type is the Clip's parent. In the
typical case, the Clip is inside a Track, so the `Clip.range_in_parent()`
will give you the range within that Track where this Clip is visible.
Each clip within the Track will have a start time that is directly after
the previous clip's end. So, given a Track with clipA and clipB in it,
this is always true:

- The `range_in_parent()` is specified in the parent time frame.
- `clipA.range_in_parent().end_time_exclusive() == clipB.range_in_parent().start_time`

If the parent is a Stack, then `range_in_parent()` is less interesting. The
start time will always have `.value == 0` and the duration is the Clip's 
duration. This means that the start of each clip in a Stack is aligned. If you 
want to shift them around, then use a Stack of Tracks (like the top-level 
Timeline has by default) and then you can use Gaps to shift the contents of each
Track around.

#### `Clip.trimmed_range_in_parent()`

This is the same as `Clip.range_in_parent()` but trimmed to the *parent*
`source_range`. In most cases the parent has a `source_range` of `None`, so
there is no trimming, but in cases where the parent is trimmed, you may
want to ask where a Clip is relative to the trimmed parent. In cases where
the Clip is completely trimmed by the parent, the 
`Clip.trimmed_range_in_parent()` will be `None`.

The `trimmed_range_in_parent()` is specified in the parent time frame.

## Tracks

### `Track.available_range()`

Total duration of the track, totalling all items inside it.
For example, if there is a clip and a gap in the track,
and each is 5 seconds long, the `available_range()`
would return 10 seconds.

### `Track.range_of_child_at_index(index)`

Returns range of nth item (specified by `index`) in the track.
Same as item's `duration`, including transition time.

### `Track.trimmed_range_of_child_at_index(index)`

Same as `range_of_child_at_index()`,
but trimmed relative to the track's source range.

### `Track.range_of_all_children()`

Returns a list of every item,
mapped to their trimmed range in the track.

## Markers

Markers can be attached to any Item (Clips, Tracks, Stacks, Gaps, etc.)

Each Marker has a `marked_range` which specifies the position and duration of
the Marker relative to the object it is attached to.

The `marked_range` of a Marker on a Clip is in the Clip's time frame (same as 
the Clip's `source_range`, `trimmed_range()`, etc.)

The `marked_range` of a Marker on a Track is in the Track's time frame (same as 
the Track's `source_range`, `trimmed_range()`, etc.)

The `marked_range.duration.value` may be 0 if the Marker is meant to be a
instantaneous moment in time, or some other duration if it spans a length of 
time.

## Transitions

### `Transition.range_in_parent()`

Range of transition for whatever holds the transition.
Calls its parent's `range_in_child()`.

### `Transition.trimmed_range_in_parent()`

The same as `range_in_parent()`,
but trimmed relative to the parent.
Calls its parent's `trimmed_range_in_child()`.

## Gaps

### `Gap.source_range`

Time range of the gap, in between other items like Clips.

## Stacks

### `Stack.source_range`

Defined range for the set of tracks.

### `Stack.available_range()`

Returns a range representing its tracks' longest duration
(based on the underlying clip `duration()`s).

### `Stack.range_of_child_at_index(int index)`

Returns the total duration of the track at position `index`.

### `Stack.trimmed_range_of_child_at_index(int index)`

Same as `range_of_child_at_index()`, but trimmed relative
to the duration of the `source_range` of the stack.

### `Stack.range_of_all_children()`

Returns set of Tracks mapped to their individual time ranges.

## Timelines

### `Timeline.range_of_child(child)`

Get trimmed time range of direct as well as indirect children (like clips and gaps).
