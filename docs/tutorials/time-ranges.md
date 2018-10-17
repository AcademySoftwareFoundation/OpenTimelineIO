# Time Ranges

Overview
----------

A Timeline and all of the Tracks and Stacks with in it work together to place
the Clips, Gaps and Transitions relative to each other in time. You can think
of this as a 1-dimensional coordinate system. Simple cases of assembling Clips
into a Track will lay the Clips end-to-end, but more complex cases involve
nesting, cross-dissolves, trimming, and speed-up/slow-down effects which can
lead to confusion. In an attempt to make this easy to work with OpenTimelineIO 
uses the following terminology and API for dealing with time ranges.

Note: You probably also want to refer to [Timeline Structure](otio-timeline-structure.html).

Clips
-------

There are several ranges you might want from a Clip.

- Ranges within the Clip and its media:

    - `clip.available_range()`

    The `available_range()` method on Clip returns a TimeRange that tells you
    how much media is available via the Clip's `media_reference`. If a Clip 
    points to a movie file on disk, then this should tell you how long that 
    movie is and what timecode it starts at. For example: "wedding.mov" starts 
    at timecode 01:00:00:00 and is 30 minutes long.

    Note that `available_range()` may return `None` if the range is not known.

    - `clip.source_range`

    Setting the `source_range` property on a Clip will trim the Clip to only 
    that range of media.

    Note that `source_range` may be `None` indicating that the Clip should use
    the full `available_range()` whatever that may be. If both `source_range`
    and `available_range()` are None, then the Clip is invalid. You need at
    least one of those.

    Usually this will be a shorter segment than the `available_range()` but this
    is not a hard constraint. Some use cases will intentionally ask for
    a Clip that is longer (or starts earlier) than the available media as a way
    to request that new media (a newly animated take, or newly recorded audio) 
    be made to fill the requested `source_range`.

    - `clip.trimmed_range()`

    This will return the Clip's `source_range` if it is set, otherwise it will
    return the `available_range()`. This tells you how long the Clip is meant to
    be in its parent Track or Stack.

    - `clip.visible_range()`

    This will return the same thing as `trimmed_range()` but also takes any 
    adjacent Transitions into account. For example, a Clip that is trimmed to 
    end at frame 10, but is followed by a symmetric 10 frame cross-dissolve, 
    will have a `visible_range()` that ends at frame 15.

    - `clip.duration()`
    
    This is the way to ask for the Clip's "natural" duration. In `oitoview` or
    most common non-linear editors, this is the duration of the Clip you will
    see in the timeline user interface.

    `clip.duration()` is a convenience for `clip.trimmed_range().duration()`.
    If you want a
    different duration, then you can ask for `clip.available_range().duration()`
    or `clip.visible_range().duration()` explicitly. This makes it clear in your
    code when you are asking for a different duration.

- Ranges of the Clip in its parent Track or Stack:

    - `clip.range_in_parent()`
    
    The answer to this depends on what type of the Clip's parent. In the
    typical case, the Clip is inside a Track, so the `clip.range_in_parent()`
    will give you the range within that Track where this Clip is visible.
    Each clip within the Track will have a start time that is directly after
    the previous clip's end. So, given a Track with clipA and clipB in it,
    this is always true:
    
    `clipA.range_in_parent().end_time_exclusive() == clipB.range_in_parent().start_time`
    
    If the parent is a Stack, then `range_in_parent()` is less interesting. The
    start time will always be 0 and the duration is the Clip's duration. This
    means that the start of each clip in a Stack is aligned. If you want to
    shift them around, then use a Stack of Tracks (like the top-level Timeline
    has by default) and then you can use Gaps to shift the contents of each
    Track around.
    
    - `clip.trimmed_range_in_parent()`
    
    This is the same as `clip.range_in_parent()` but trimmed to the *parent*
    `source_range`. In most cases the parent has a `source_range` of None, so
    there is no trimming, but in cases where the parent is trimmed, you may
    want to ask where a Clip is relative to the trimmed parent. In cases where
    the Clip is completely trimmed by the parent, the 
    `clip.trimmed_range_in_parent()` will be None.
   

Tracks
--------

TODO.

Transitions
-------------

TODO.

Gaps
------

TODO.

Stacks
--------

TODO.

Timelines
-----------

TODO.
