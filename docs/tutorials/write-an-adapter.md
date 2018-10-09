# Writing an OTIO Adapter

OpenTimelineIO Adapters are plugins that allow OTIO to read and/or write other timeline formats.

Users of OTIO can read and write files like this:

```
#/usr/bin/env python
import opentimelineio as otio
mytimeline = otio.adapters.read_from_file("something.edl")
otio.adapters.write_to_file(mytimeline, "something.otio")
```

The otio.adapters module will look at the file extension (in this case ".edl" or ".otio") and pick the right adapter to convert to or from the appropriate format.

Note that the OTIO JSON format is treated like an adapter as well. The ".otio" format is the only format that is lossless. It can store and retrieve all of the objects, metadata and features available in OpenTimelineIO. Other formats are lossy - they will only store and retrieve features that are supported by that format (and by the adapter implementation). Some adapters may choose to put extra information, not supported by OTIO, into metadata on any OTIO object.

## Registering Your Contrib Adapter

To create a new contrib OTIO Adapter, you need to create a file `myadapter.py` in the `opentimelineio_contrib/adapters` folder. Then add an entry to `opentimelineio_contrib/adapters/contrib_adapters.plugin_manifest.json` that registers your new adapter.  Note that contrib adapters are community supported, and not supported by the OTIO team.  They must still provide unit tests and pass both testing and linting before they are accepted into the repository.

### Custom Adapters

Alternately, if you are creating a site specific adapter that you do _not_ intend to share with the community, you can create your `myadapter.py` file anywhere.  In this case, you must create a `mysite.plugin_manifest.json` (with an entry like the below example that points at `myadapter.py`) and then put the path to your `mysite.plugin_manifest.json` on your `$OTIO_PLUGIN_MANIFEST_PATH` environment variable, which is ":" separated.

For example, to register `myadapter.py` that supports files with a `.myext` file extension:
```json
{
    "OTIO_SCHEMA" : "Adapter.1",
    "name" : "myadapter",
    "execution_scope" : "in process",
    "filepath" : "myadapter.py",
    "suffixes" : ["myext"]
}
```

Currently (as of OTIO Beta 8) only execution_scope "in process" is supported. If your adapter needs to execute non-Python code, then we intend to support execution_scope "external process" in the future.

### Packaging and Sharing Custom Adapters

Adapters may also be organized into their own independent Python project for subsequent [packaging](https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives), [distribution](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives) and [installation](https://packaging.python.org/tutorials/packaging-projects/#installing-your-newly-uploaded-package) by [`pip`](https://packaging.python.org/key_projects/#pip). We recommend you organize your project like so:
```
.
├── setup.py
└── opentimelineio_mystudio
    ├── __init__.py
    ├── plugin_manifest.json
    ├── adapters
    │   ├── __init__.py
    │   ├── my_adapter_x.py
    │   └── my_adapter_y.py
    └── operations
        ├── __init__.py
        └── my_linker.py
```

With a `setup.py` containing this minimum entry set:
```python
from setuptools import setup

setup(
    name='OpenTimelineMyStudioAdapters',
    entry_points={
        'opentimelineio.plugins': 'opentimelineio_mystudio = opentimelineio_mystudio'
    },
    package_data={
        'opentimelineio_mystudio': [
            'plugin_manifest.json',
        ],
    },
    version='0.0.1',
    packages=[
        'opentimelineio_mystudio',
        'opentimelineio_mystudio.adapters',
        'opentimelineio_mystudio.operations',
    ],
)
```

And a `plugin_manifest.json` like:
```json
{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "adapters" : [
        {
            "OTIO_SCHEMA" : "Adapter.1",
            "name" : "adapter_x",
            "execution_scope" : "in process",
            "filepath" : "adapters/my_adapter_x.py",
            "suffixes" : ["xxx"]
        },
        {
            "OTIO_SCHEMA" : "Adapter.1",
            "name" : "adapter_y",
            "execution_scope" : "in process",
            "filepath" : "adapters/my_adapter_y.py",
            "suffixes" : ["yyy", "why"]
        }
    ],
    "media_linkers" : [
        {
            "OTIO_SCHEMA" : "MediaLinker.1",
            "name" : "my_studios_media_linker",
            "execution_scope" : "in process",
            "filepath" : "operations/my_linker.py"
        }
    ]
}
```

## Required Functions

Each adapter must implement at least one of these functions:
```
def read_from_file(filepath):
    ...
    return timeline

def read_from_string(input_str):
    ...
    return timeline

def write_to_string(input_otio):
    ...
    return text

def write_to_file(input_otio, filepath):
    ...
    return
```

If your format is text-based, then we recommend that you implement `read_from_string` and `write_to_string`. The adapter module will automatically wrap these and allow users to call `read_from_file` and `write_to_file`.

## Constructing a Timeline

To construct a Timeline in the `read_from_string` or `read_from_file` functions, you can use the API like this:
```
timeline = otio.schema.Timeline()
timeline.name = "Example Timeline"
track = otio.schema.Sequence()
track.name = "V1"
timeline.tracks.append(track)
clip = otio.schema.Clip()
clip.name = "Wedding Video"
track.append(clip)
```

### Metadata

If your timeline, tracks, clips or other objects have format-specific, application-specific or studio-specific metadata, then you can add metadata to any of the OTIO schema objects like this:
```
timeline.metadata["mystudio"] = {
    "showID": "zz"
}
clip.metadata["mystudio"] = {
    "shotID": "zz1234",
    "takeNumber": 17,
    "department": "animation",
    "artist": "hanna"
}
```
Note that all metadata should be nested inside a sub-dictionary (in this example "mystudio") so that metadata from other applications, pipeline steps, etc. can be kept separate. OTIO carries this metadata along blindly, so you can put whatever you want in there (within reason). Very large data should probably not go in there.

### Media References

Clip media (if known) should be linked like this:
```
clip.media_reference = otio.media_reference.External(
    target_url="file://example/movie.mov"
)
```

Some formats don't support direct links to media, but focus on metadata instead. It is fine to leave the media_reference empty (None) if your adapter doesn't know a real file path or URL for the media.

### Source Range vs Available Range

To specify the range of media used in the Clip, you must set the Clip's source_range like this:
```
clip.source_range = otio.opentime.TimeRange(
    start_time=otio.opentime.RationalTime(150, 24), # frame 150 @ 24fps
    duration=otio.opentime.RationalTime(200, 24) # 200 frames @ 24fps
)
```

Note that the source_range of the clip is not necessarily the same as the available_range of the media reference. You may have a clip that uses only a portion of a longer piece of media, or you might have some media that is too short for the desired clip length. Both of these are fine in OTIO. Also, clips can be relinked to different media, in which case the source_range of the clip stays the same, but the media_reference (and its available_range) will change after the relink. For example, you might relink from an old render to a newer render which has been extended to cover the source_range references by the clip.

If you know the range of media available at that Media Reference's URL, then you can specify it like this:
```
clip.media_reference = otio.media_reference.External(
  target_url="file://example/movie.mov",
  available_range=otio.opentime.TimeRange(
      start_time=otio.opentime.RationalTime(100, 24), # frame 100 @ 24fps
      duration=otio.opentime.RationalTime(500, 24) # 500 frames @ 24fps
  )
)
```

It is fine to leave the Media Reference's available_range empty if you don't know it, but you should always specify a Clip's source_range.

## Traversing a Timeline

When exporting a Timeline in the `write_to_string` or `write_to_file` functions, you will need to traverse the Timeline data structure. Some formats only support a single track, so a simple adapter might work like this:
```
def write_to_string(input_otio):
    """Turn a single track timeline into a very simple CSV."""
    result = "Clip,Start,Duration\n"
    if len(input_otio.tracks) != 1:
        raise Exception("This adapter does not support multiple tracks.")
    for item in input_otio.each_clip():
        start = otio.opentime.to_seconds(item.source_range.start_time)
        duration = otio.opentime.to_seconds(item.source_range.duration)
        result += ",".join([item.name, start, duration]) + "\n"
    return result
```

More complex timelines will contain multiple tracks and nested sequences. OTIO supports nesting via the abstract Composition class, with two concrete subclasses, Sequence and Stack. In general a Composition has children, each of which is an Item. Since Composition is also a subclass of Item, they can be nested arbitrarily.

In typical usage, you are likely to find that a Timeline has a Stack (the property called 'tracks'), and each item within that Stack is a Sequence. Each item within a Sequence will usually be a Clip, Transition or Gap. If you don't support Transitions, you can just skip them and the overall timing of the Sequence should still work.

If the format your adapter supports allows arbitrary nesting, then you should traverse the composition in a general way, like this:
```
def export_otio_item(item):
    result = MyThing(item)
    if isinstance(item, otio.core.Composition):
        result.children = map(export_otio_item, item.children)
    return result
```

If the format your adapter supports has strict expectations about the structure, then you should validate that the input has the expected structure and then traverse it based on those expectations, like this:
```
def export_timeline(timeline):
    result = MyTimeline(timeline.name, ...)
    for track in timeline.tracks:
        if !isinstance(track, otio.schema.Sequence):
            raise Exception("This adapter requires each track to be a sequence, not a "+typeof(track))
      t = result.AddTrack(track.name, ...)
      for clip in track.each_clip():
          c = result.AddClip(clip.name, ...)
    return result
```

## Examples

OTIO includes a number of "core" (supported by the core team) adapters in `opentimelineio/adapters` as well as a number of community supported adapters in `opentimelineio_contrib/adapters`.