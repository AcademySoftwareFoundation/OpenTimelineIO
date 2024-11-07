# For Integrators

 
This document is meant to give application integrators context on typical use patterns and best practices when interacting with the data and mental model of OpenTimelineIO.

In [**How Should My Application Use OpenTimelineIO?**](#how-should-my-application-use-opentimelineio) we discuss some considerations about what kinds of data your application might want to use OTIO as an interchange format for and how thing about their role within user workflows.

[**An Interchange Format and API**](#an-interchange-format-and-api) discusses the OpenTimelineIO draft specification as well as available implementations for reading and writing OTIO files.

[**OTIO General Guidelines**](#otio-general-guidelines) discusses the concept of "schema" in OTIO, best practices around leveraging metadata, some different forms of OTIO files that can be exchanged, and how to best engage with OTIO's evolution and enhancement.

Finally, [**OpenTimelineIO Schema Objects**](#opentimelineio-schema-objects) discusses specific types of OTIO schema objects and their typical usage.

This document focuses on common elements used in the OTIO schema and some typical patterns for how they're composed - there is more depth to the full schema than is covered in this document. [The OpenTimelineIO Data Model Specification](https://sandflow.github.io/otio-core-specification/) covers the schema objects in much deeper detail.

Applications integrating OTIO should rely on one of the implementations provided by the project to read and write `.otio` files and manipulate the data model, but to illustrate the core concepts we may include some JSON serialization as examples.

## How Should My Application Use OpenTimelineIO?

As a developer, you know your application's unique features best and only you will be able to identify the exact ways OpenTimelineIO will make your application more valuable in user workflows. This guide can, however, help with some ways to think about what OTIO is, some of the unique benefits it provides, and how to best take advantage of it.

### What Is Your Application's Role in the Workflow?

The benefits of OTIO come from the fidelity of editorial it communicates, the ability to add extra arbitrary metadata, and ease of access to that data. What key information or creative decisions are captured or made within the application (e.g. edit points, color decisions, notes/markup, camera report or script continuity data, etc.)? Is there somewhere data is getting lost or degraded when moving through the workflow? Where do users wish they could write scripts or automations to interface with the application?

Existing formats imported or exported from an application can give some hints about how interchange could be improved with OTIO:

- In what ways are `.edl` files overly simplistic for user workflows? 
- Is there some metadata that isn't making it in our out of the application because FCP `.xml` doesn't carry it? 
- Are users having trouble deciphering data in `.aaf` files? 
- Are `.ale` metadata fields feeling overloaded or under-expressive? 
- Are there custom XML, CSV, or JSON files that the application is reading/writing? 

Using OTIO in place of these formats can help users integrate your application quicker and with fewer errors by allowing them to skip writing parsers and jump right into using the data.

### Thinking Beyond EDL

Adopting OTIO as a replacement for EDLs or ALEs is a clear win, but integrators should also challenge themselves to think outside just the common use cases. Because OTIO has an extensible schema and hosts rich metadata, its timelines and other editorial objects can be used to carry data not commonly housed in other editorial formats.

Some more interesting (often experimental) examples of data that's been hosted in OTIO include:

* Markup, annotation, and notes attached to the correct time in the cut so an editor can view them in-context with their NLE
* [Timed Text](https://github.com/PixarAnimationStudios/OpenTimelineIO/pull/805)
* [Preservation of lens metadata](https://github.com/reinecke/otio-cookelensmetadata)
* Metadata from a screenplay (scene, location, characters, etc.)

OTIO is really great at expressing how objects exist temporally - so anywhere there is a timing component to the data, it might be a good fit for OTIO.

### Want to Brainstorm?

If you think OTIO might be a good fit and would like to talk to OTIO developers and users, the OTIO community provides a few good avenues:

- The [#OpenTimelineIO channel](https://academysoftwarefdn.slack.com/messages/CMQ9J4BQC) on the [Academy Software Foundation Slack](https://slack.aswf.io/) (registration required) hosts a lot of great conversation
- The project [GitHub Discussions](https://github.com/PixarAnimationStudios/OpenTimelineIO/discussions) is a good place to ask questions too

## An Interchange Format and API

OTIO files are designed to be human readable JSON with work in progress on the [OpenTimelineIO Data Model Specification](https://sandflow.github.io/otio-core-specification/) to ensure they are easy to understand and useful for years to come and into archival status.

While the specification provides detail about specific schema objects, their usage, and semantic meaning; integrators should avoid creating their own implementation unless there is a really compelling reason to do so. The core implementation provides a lot of subtle behavior that can be time consuming to reproduce and could impact an application's ability to effectively interoperate with OpenTimelineIO.

Beyond the main [C++ implementation with Python bindings](http://opentimeline.io), language bindings are available for:

- [C](https://github.com/OpenTimelineIO/OpenTimelineIO-C-Bindings)
- [Java](https://github.com/OpenTimelineIO/OpenTimelineIO-Java-Bindings)
- [Swift](https://github.com/OpenTimelineIO/OpenTimelineIO-Swift-Bindings)

## OTIO General Guidelines

OTIO's implementation is in two layers:

1. The serialization scheme for storing structured data along with a schema name and version for interpreting the data
2. A set of schema which define types of objects and their serialized data fields

When interacting with OTIO, integrators will be dealing almost entirely with deserialized schema objects. The implementation will handle mechanics of translating between in-memory objects and their serialized form. The OTIO implementation also provides a rich set of functionality for querying and modifying timeline data.

### The `metadata` dictionary

In addition to the "first-class" fields offered by OTIO schema objects, every object in OTIO has a field called `metadata` that allows applications and users to attach any arbitrary metadata they like as a nested dictionary structure. This is a unique feature of OTIO and provides some powerful uses in a production pipeline. Studios attach identifiers for internal production tracking systems, adapters store format-specific contextual metadata about the file they derived the OTIO from, and some users even attach metadata like source script page number or notes from a review system. The `metadata` dictionary is also a powerful tool in driving the evolution of first-class schema in OTIO.

OTIO allows for any arbitrarily deep collection of other dictionaries, lists, scalars, and even SerializableObjects in the `metadata` dictionary - the implementation enforces no structure, but there are some strong conventions implementers should follow.

#### use a unique "namespace" key for data your application stores within object `metadata` dictionaries

Using a unique namespace helps avoid collision with metadata populated by others. The "namespace" key in this case is just the top-level key in the `metadata` dictionary under which an implementer places the dictionary containing their data. These top-level "namespace" keys denote informal sorts of sub-schema.

For example, a clip may have a metadata dictionary like the following:

```json
{
  "myAnimStudio": {
    "sequence": "ABC",
    "shot": "ABC010",
    "phase": "LAYOUT",
    "take": "1",
    "shot_id": "7b3aaa14-8305-4fdd-87c2-b0b9d3f9dac7"
  },
  "cdl": {
    "asc_sat": 0.9,
    "asc_sop": {
      "offset": [
        1,
        -0.0122,
        0.0305
      ],
      "power": [
        1,
        0,
        1
      ],
      "slope": [
        0.1,
        0.2,
        0.3
      ]
    }
  },
  "cmx_3600": {
    "comments": [
      "SOURCE FILE: ABC010.LAYOUT3.01"
    ]
  }
}
```

Note that information for studio production tracking, CDL values, and a comment field from the original CMX 3600 EDL all coexist as separated by their namespace keys.

#### Preserve Metadata to the best of your abilities

In reading and writing OTIO, make a best effort to preserve the data in `metadata` dictionaries when writing OTIO back out. If possible, only mutate the data under the namespaces your application controls. This ensures your application will be a "good citizen" and metadata populated upstream of your application will flow downstream through the pipeline without loss. In the previous example, the identifiers under the `myAnimStudio` namespace provide critical value to the pipeline and are useful to the workflow later on. Likewise, creative decisions are stored in the `cdl` namespace, preserving them helps us ensure we maintain the artistic vision.

### `.otio` Files

Part of OTIO is that all schema objects are serializable. `.otio` files are the native [JSON serialization](https://sandflow.github.io/otio-core-specification/#json-serialization) of an OTIO object tree with one root object. 

While there are no current plans to create alternate native OTIO serialization formats, the implementation is built to allow creation of a new serialization format if needed.

#### Root Objects in OTIO files

Any object available in the OTIO schema can be serialized and de-serialized as the root object in a `.otio` file. This means implementers should check what kind of schema object results from reading an OTIO file and handle it appropriately. This also means there is a great degree of freedom in what kind of data can be communicated with OTIO - whole timelines, bins, and individual clips are among the possible objects that can be root objects in OTIO files.

While any OTIO schema object can be serialized at the top-level, **most OTIO files will have either a [`Timeline`](https://sandflow.github.io/otio-core-specification/#object-model-Timeline) or [`SerializableCollection`](https://sandflow.github.io/otio-core-specification/#object-model-SerializableCollection) as the root object.**

For instance, in cases where older workflows might use an `.edl` file, an `.otio` file with a root `Timeline` would be used. In cases where an `.ale` file was used, an `.otio` file with a root `SerializableCollection` of `Clip` objects would be used.

OTIO has no schema for a project, this would typically be represented as a `SerializableCollection` containing `Timelines`, other `SerializableCollections` for folder or bin structure, and `Clips` for various media in the project.

### OTIO is an Evolving format

OTIO offers [a lot of the essentials](https://opentimelineio.readthedocs.io/en/latest/tutorials/feature-matrix.html) for the most common types of cut information used in pipelines, but the team is also actively expanding the schema to enable more and more use cases. When possible, schema development is driven by real-world use in production to ensure the format is providing models that are proven useful.

The file format and implementation provide a number of useful tools to help implementors easily progress with OTIO's evolution.

#### Schema Are Versioned

Each object type has an independent schema version that is stored as an integer that increments each time there is a _breaking_ change. This means non-breaking changes, like addition of fields, won't interfere with loading in older implementations, they just may not be available.

When OTIO encounters a serialized object with an older schema, it automatically migrates that object to the newest available schema, even "up-converting" data if needed. This means application implementors only need to concern themselves with handling the latest schema version when working with OTIO objects.

#### `metadata` dictionaries are a good place to store information that is not yet part of the "first-class" schema

Wherever possible, implementors should try to use the first-class fields available in in OTIO. However, when the schema does not yet represent valuable data, making it available early in a `metadata` dictionary allows pipelines to start using it and aids in the design of a "first-class" schema to be added to OTIO. Most new schema in OTIO starts as extra information in a metadata dictionary, once it has been proven useful and the data modeling has been refined, an update to OTIO will then allow expressing that in new "first-class" schema.

#### Keep up-to-date with the OTIO implementation

Upgrading the OTIO release used in your software ensures you have maximum read compatibility with other applications. There are currently no mechanisms provided for downgrading the schema versions used within an OTIO file, so moving forward with the format helps users from having to make special concessions for your application.

## OpenTimelineIO Schema Objects

[OpenTimelineIO's schema](https://sandflow.github.io/otio-core-specification/#object-model) provides familiar objects meant to directly correlate to the units editors interact with in an NLE while providing advanced compositions. Below are some of the most common schema objects and some guidance on using them.

### Timeline

[`Timeline`](https://sandflow.github.io/otio-core-specification/#object-model-Timeline) objects represent one edit, sequence, or presentation. Timelines are named - as you might see a sequence named in an editor's project.

Using an appropriate namespace key, the `metadata` attribute is a great place to store important timeline/sequence settings such as edit rate, video resolution, and audio sample rate. In the future many of these concepts will be given first-class attributes.

#### Use `global_start_time` for start timecode of a sequence

The `global_start_time` field on a `Timeline` object communicates the offset value for the start of the timeline. This is how you might set a start timecode of `01:00:00:00` for a sequence.

### SerializableCollection

[`SerializableCollection`](https://sandflow.github.io/otio-core-specification/#object-model-SerializableCollection) objects store an ordered collection of other OTIO schema objects. They are commonly used to represent bins or folders in a project and can be nested to create deeper project structure. The `name` property corresponds to the name you see for the folder or bin within a project.

### Choosing Composition Objects

When creating an editorial composition, there are two important relationships items have to one another, sequential presentation (clip B _comes after_ clip A), and simultaneous presentation (clip B _is composited over_ clip A). In OTIO, a [`Track`](https://sandflow.github.io/otio-core-specification/#object-model-Track) is used to compose items in sequential order and a [`Stack`](https://sandflow.github.io/otio-core-specification/#object-model-Stack) is used to compose items that are simultaneous. A `Timeline` object's `tracks` attribute references a `Stack` containing the timeline's audio, video, and other `Tracks`.

This `Stack` of `Track` items is directly analogous to the timeline interface where editors compose their clips in most NLE software.

### Stack

Commonly the only `Stack` used in an OTIO document is the `tracks` stack on the timeline. The `children` of the `Stack` is an ordered list of all the items (typically `Tracks`) that are coincident in "compositing" order - the first item in the collection is the "bottom" and the last item is the "top".

In general, it is assumed that a stack of visual media uses alpha compositing, overlaying items one over the other. Audio media is assumed to use additive compositing, mixing all the tracks together so you hear them all. If another compositing method is used, somewhere under your application's namespace key in the `metadata` on the `Stack` is a great place to store that information.

### Track

In addition to providing items presented in sequential order, a track has a `kind`. The track kind defines what type of output media the track composes. Track kind is deliberately a string as opposed to an enum only allowing a constrained set of media types. The values `Audio` and `Video` are provided via constants for the track kinds often used. Values outside the provided constants can be used, but it is expected that most application implementers will ignore tracks of a kind they don't understand and there may be certain utility methods that don't handle tracks of unknown kind.

As use cases grow for track kinds other than `Audio` and `Video` and the community reaches consensus, those new track kinds will be provided as additional constants.

### Items

The items in a timeline are either [`Clip`](https://sandflow.github.io/otio-core-specification/#object-model-Clip) or [`Gap`](https://sandflow.github.io/otio-core-specification/#object-model-Gap) schema objects. `Clip` objects specify media to use in the composition, whereas `Gap` objects can be used to offset items in the track temporally.

These Items are single-use, meaning any given `Item` instance can be used in a composition once, this allows different item instances to have their own sets of markers, metadata, and effects as relevant to that specific use of the media in the composition. The APIs provide ways of copying items to create any number of identical instances for use multiple times in a composition. One way to think of items is as if each one were a strip of film being spliced end-to-end in a track. A `Gap` is like inserting clear leader of some length, and a `Clip` is like using film from the camera - if you need to use the same strip of film twice, you have to make another copy of it. 

### Clip

A [`Clip`](https://sandflow.github.io/otio-core-specification/#object-model-Clip) represents an instance of using some subsegment of media in the timeline. This is directly analogous to clips you see in a standard NLE.

The source in and out points on a `Clip` are set using `source_range` - this also determines the duration of the `Clip`. The `source_range` is specified as the time range to select within the the source media's `available_range`.

The `media_reference` on a clip specifies how to locate media assets composed in the timeline.

### Gap

[`Gap`](https://sandflow.github.io/otio-core-specification/#object-model-Gap) represents an absence of media - in other words, a `Gap` does not contribute to the composition media, it only serves to offset other items in time. A Gap can be thought of as transparent or silent filler.

### MediaReference

OTIO doesn't embed media assets, instead it provides a way for applications to locate the appropriate media. Subclasses of [MediaReference](https://sandflow.github.io/otio-core-specification/#object-model-MediaReference) provide various methods for identifying the media composed within the timeline.

Use the media's global start time when setting `available_range`. When the `start_time` of the available range is the start timecode or first frame number of the media, applications are able to locate the correct media within a clip through a range of situations - especially when switching between representations that are trimmed with different handles.

#### Choose an Appropriate `MediaReference` Type

When a specific file path/url is available for an asset, use one of the following reference types:

* [`ExternalReference`](https://sandflow.github.io/otio-core-specification/#object-model-ExternalReference) - Identifies an asset by URL (local files use `file://` urls)
* [`ImageSequenceReference`](https://sandflow.github.io/otio-core-specification/#object-model-ImageSequenceReference) - Identifies an asset as a set of sequentially numbered images

When there isn't a specific file path, use [`MissingReference`](https://sandflow.github.io/otio-core-specification/#object-model-MissingReference). Any metadata that might help downstream consumers relink the media (e.g. reel name, tracking IDs, etc.) should be included in the reference's `metadata` dictionary.

If a clip's media is generated programmatically (e.g. solid color, white noise, color bars, tone, etc), a [`GeneratorReference`](https://sandflow.github.io/otio-core-specification/#object-model-GeneratorReference) should be used. The `parameters` dictionary should be used to describe the generator configuration (e.g. what color is the solid color? What frequency of tone should be generated? Sine or square wave?).

### Markers

A [`Marker`](https://sandflow.github.io/otio-core-specification/#object-model-Marker) can be used to attach additional information to a specific time or time range. Markers can be added to the `markers` lists on `Track`, `Stack`, `Gap`, and `Clip` objects.

The `marked_range` attribute specifies the time range marked in item's local time coordinates. For example, if the marked range is `TimeRange(start_time=RationalTime(0, 24), duration=RationalTime(0, 24))`, then the marker occurs at the beginning of the clip in the timeline, not the beginning of the source media.

The `color` attribute on `Marker` objects describes the color the marker is presented as in the user interface and is commonly used to add workflow-specific context about what the marker is communicating (e.g. RED for chapter markers, BLUE for VFX shot names, etc.). As workflows become more OTIO-aware, this overloaded use case for marker color should be phased out in favor of explicitly describing their purpose in an appropriate `metadata` field.

Some of the ways markers are commonly used include:
* Noting chapters in a sequence
* Attaching extra metadata to clip
* Identifying clips to be used for VFX

### Effects

[`Effects`](https://sandflow.github.io/otio-core-specification/#object-model-Effect) model transformations applied to the media as used in the composition. In common terms, effects are sometimes called "filters".

Effects can be added to the `effects` lists on `Track`, `Stack`, `Gap`, and `Clip` objects, though they are most commonly applied to `Clip` objects. The effects list allows stacking of multiple effects on a clip where the media is transformed in order of the effects list. For instance, a video clip could have a 100% desaturation applied as the first effect in the list and a tint with a brown hue as the second effect to add color back and achieve a "sepia" effect.

The `effect_name` property should be set to a key that identifies the specific effect used, and configuration of that usage of the effect can be stored in the metadata dictionary.

In the future, some standardized effects may be defined as new schema in OTIO with specific configuration properties exposed, however at the moment everything aside from timing effects use the base `Effect` schema.

#### Timing Effects

_Note: A newer approach to time transformations is in active development. For more details, please contact the otio developers._

Timing effects are special effects that inform how time in the clip's time coordinate space (0 to the duration of the clip), maps to time in the media's time coordinate space (the available range of the clip).

The [`LinearTimeWarp`](https://sandflow.github.io/otio-core-specification/#object-model-LinearTimeWarp) describes a linear mapping of presentation time to source media time. For instance, if the `time_scalar` property is set to `2.0`, then the clip footage plays back at double the rate.

A clip's `source_range` `start_time` specifies the start point in the source media to use, the `duration` is the duration in the presentation. To determine the duration of source media used by the clip, you multiply the clip's duration by the `time_scalar`.

There is also a [`FreezeFrame`](https://sandflow.github.io/otio-core-specification/#object-model-FreezeFrame) time effect which always has a `time_scalar` of `0` - this results in the first frame of a clip being held for the duration of the clip.

### Transitions

A [`Transition`](https://sandflow.github.io/otio-core-specification/#object-model-Transition) is placed in a track between two other items to indicate that their content will be blended for some amount of time during the presentation. A transition signals an "overlap" between the item that precede it and the item that follows it. The `in_offset` specifies where relative to the end of the preceding item in the track the transition starts, and `out_offset` specifies where relative to the start of the following item the transition ends.

The `transition_type` property should be set to a key that identifies the specific transition effect used (like horizontal wipe or cross-fade), and configuration of that usage of the effect can be stored in the `parameters` dictionary property.

## TODO
- Find all schema object name references and link out to appropriate documentation
- Create illustrations showing examples of some concepts, maybe from otioview, sag adapter?
- Continue reorganization pass through specific schema objects section
- Full proofread and clarity pass