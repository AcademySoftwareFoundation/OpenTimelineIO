# Architecture

Overview
----------

OpenTimelineIO is an open source library for the interchange of editorial information.  This document describes the structure of the python library.

To import the library into python:
`import opentimelineio as otio`

Canonical Structure
--------------------

Although you can compose your OTIO files differently if you wish, the canonical OTIO structure is as follows:

- root: `otio.schema.Timeline` This file contains information about the root of a timeline, including a `global_start_time` and a top level container, `tracks`
- `timeline.tracks`: This member is a `otio.schema.Stack` which contains `otio.schema.Track` objects
- `timeline.tracks[i]`:  The `otio.schema.Track` contained by a `timeline.tracks` object contains the clips, transitions and subcontainers that compose the rest of the editorial data

Modules
--------

The most interesting pieces of OTIO to a developer integrating OTIO into another application or workflow are:
- `otio.schema`: The classes that describe the in-memory OTIO representation
- `otio.opentime`: Classes and utility functions for representing time, time ranges and time transforms
- `otio.adapters`: Modules that can read/write to or from an on-disk format and the in-memory OTIO representation

Additionally, for developers integrating OTIO into a studio pipeline:
- `otio.media_linker`: Plugin system for writing studio or workflow specific media linkers that run after adapters read files

The in-memory OTIO representation data model is rooted at an `otio.schema.Timeline` which has a member `tracks` which is a `otio.schema.Stack` of `otio.schema.Track`, which contain a list of items such as:
- `otio.schema.Clip`
- `otio.schema.Gap`
- `otio.schema.Stack`
- `otio.schema.Track`
- `otio.schema.Transition`

The `otio.schema.Clip` objects can reference media through a `otio.schema.ExternalReference` or indicate that they are missing a reference to real media with a `otio.schema.MissingReference`.  All objects have a metadata dictionary for blind data.

Schema composition objects (`otio.schema.Stack` and `otio.schema.Track`) implement the python mutable sequence API.  A simple script that prints out each shot might look like:


```python
import opentimelineio as otio

# read the timeline into memory
tl = otio.adapters.read_from_file("my_file.otio")

for each_seq in tl.tracks:
    for each_item in each_seq:
        if isinstance(each_item, otio.schema.Clip):
            print each_item.media_reference
```

Or, in the case of a nested composition, like this:

```python
import opentimelineio as otio

# read the timeline into memory
tl = otio.adapters.read_from_file("my_file.otio")

for clip in tl.each_clip():
    print clip.media_reference
```

## Time on otio.schema.Clip

A clip may set its timing information (which is used to compute its `duration()` or its `trimmed_range()`) by configuring either its:
- `media_reference.available_range`
 This is the range of the available media that can be cut in.  So for example, frames 10-100 have been rendered and prepared for editorial.
- `source_range`
 The range of media that is cut into the sequence, in the space of the available range (if it is set). In other words, it further truncates the available_range.

A clip must have at least one set or else its duration is not computable:

```python
cl.duration()
# raises: opentimelineio._otio.CannotComputeAvailableRangeError: Cannot compute available range: No available_range set on media reference on clip: Clip("", ExternalReference("file:///example.mov"), None, {})
```

You may query the `available_range` and `trimmed_range` via accessors on the `Clip()` itself, for example:

```python
cl.trimmed_range()
cl.available_range() # == cl.media_reference.available_range
```

Generally, if you want to know the range of a clip, we recommend using the `trimmed_range()` method, since this takes both the `media_reference.available_range` and the `source_range` into consideration.

## Time On Clips in Containers

Additionally, if you want to know the time of a clip in the context of a container, you can use the local:
`trimmed_range_in_parent()` method, or a parent's `trimmed_range_of_child()`.  These will additionally take into consideration the `source_range` of the parent container, if it is set.  They return a range in the space of the specified parent container.

## otio.opentime

Opentime encodes timing related information.

### RationalTime

A point in time at `rt.value*(1/rt.rate)` seconds.  Can be rescaled into another RationalTime's rate.

### TimeRange

A range in time.  Encodes the start time and the duration, meaning that end_time_inclusive (last portion of a sample in the time range) and end_time_exclusive can be computed.

## otio.adapters

OpenTimelineIO includes several adapters for reading and writing from other file formats. The `otio.adapters` module has convenience functions that will auto-detect which adapter to use, or you can specify the one you want.

Adapters can be added to the system (outside of the distribution) via JSON files that can be placed on the {term}`OTIO_PLUGIN_MANIFEST_PATH` environment variable to be made available to OTIO.

Most common usage only cares about:
- `timeline = otio.adapters.read_from_file(filepath)`
- `timeline = otio.adapters.read_from_string(rawtext, adapter_name)`
- `otio.adapters.write_to_file(timeline, filepath)`
- `rawtext = otio.adapters.write_to_string(timeline, adapter_name)`

The native format serialization (`.otio` files) is handled via the "otio_json" adapter, `otio.adapters.otio_json`.

In most cases you don't need to worry about adapter names, just use `otio.adapters.read_from_file()` and `otio.adapters.write_to_file` and it will figure out which one to use based on the filename extension.

For more information, see [How To Write An OpenTimelineIO Adapter](write-an-adapter).

## otio.media_linkers

Media linkers run on the otio file after an adapter calls `.read_from_file()` or `.read_from_string()`.  They are intended to replace media references that exist after the adapter runs (which depending on the adapter are likely to be `MissingReference`) with ones that point to valid files in the local system.  Since media linkers are plugins, they can use proprietary knowledge or context and do not need to be part of OTIO itself.

You may also specify a media linker to be run after the adapter, either via the `media_linker_name` argument to `.read_from_file()` or `.read_from_string()` or via the {term}`OTIO_DEFAULT_MEDIA_LINKER` environment variable.  You can also turn the media linker off completely by setting the `media_linker_name` argument to `otio.media_linker.MediaLinkingPolicy.DoNotLinkMedia`.

For more information about writing media linkers, see [How To Write An OpenTimelineIO Media Linker](write-a-media-linker).

Example Scripts
----------------

Example scripts are located in the [examples subdirectory](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/tree/main/examples).
