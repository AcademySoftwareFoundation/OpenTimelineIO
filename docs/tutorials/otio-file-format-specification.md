# File Format Specification

## Version

    This may be out of date. 

This DRAFT describes the OpenTimelineIO JSON File Format as of OTIO Alpha 5.

## Note
We strongly recommend that you use the OpenTimelineIO library to read and write OTIO files instead of implementing your own parser or writer. However, there will
undoubtedly be cases where this is not practical, so we document the format here for clarity.

## Naming
OpenTimelineIO files should have a `.otio` path extension. Please do not use `.json` to name OTIO files.

## MIME Type/UTI
TODO: Should we specify a MIME Type `application/vnd.pixar.opentimelineio+json` and UTI `com.pixar.opentimelineio` for OTIO, or just use MIME: `application/json` and UTI: `public.json`?

## Contents
OpenTimelineIO files are serialized as JSON (http://www.json.org)

## Structure
An OTIO file is a tree structure of nested OTIO objects. Each OTIO object is stored as a JSON dictionary with member fields,
each of which may contain simple data types or nested OTIO objects.

OTIO does not support instancing, so you cannot reference the same object multiple times in the tree structure. If the same clip or media appears multiple times in your timeline, it will appear as identical copies of the Clip or MediaReference object.

The top level object in an OTIO file can be any OTIO data type, but is typically a Timeline. This means that most use cases will assume that the top level
object is a Timeline, but in specific workflows, you can read and write otio files that contain
just a Clip, Sequence, RationalTime, or any other OTIO data type. Due to the nature of JSON, you could also read/write an array of objects, but we
recommend that you use the OTIO SerializableCollection data type in this case so that you can attach metadata to the container itself. Code that reads an OTIO
file should guard against unexpected top level types and fail gracefully.
Note also, that this is the reason that there is no top level file format version in OTIO. Each data type has a version instead to allow for more granular versioning.

Each OTIO object has an `"OTIO_SCHEMA"` key/value pair that identifies the OTIO data type and version of that type.
For example `"OTIO_SCHEMA": "Timeline.1"` or `"OTIO_SCHEMA": "Clip.5"`. This allows future versions of OTIO to change the serialization details of each data type
independently and introduce new data types over time. (TODO: Link to discussion on schema versioning.)

Member fields of each data type are encoded as key/value pairs in the containing object's dictionary. The value of each key can be a JSON string, number, list,
or dictionary. If the value is a dictionary, then it will often be an OTIO data type. In some cases (specifically metadata) it can be a regular JSON dictionary.

OTIO JSON files are typically formatted with indentation to make them easier to read. This makes the files slightly larger, but dramatically improves human
readability which makes debugging much easier. Since human readablility and ease of use are explicit goals of the OpenTimelineIO project, we recommend that you
do not minify OTIO JSON unless absolutely necessary. If file size is really important, you should probably gzip them instead.

## Nesting 

A Timeline has one child, called "tracks" which is a Stack. Each of that Stack's children is a Sequence. From there on down each child can be any of these types: Clip, Filler, Stack, Sequence.

In a simple case with one track of 3 clips, you have:

```
Timeline "my timeline"
  Stack "tracks"
    Sequence "video track"
      Clip "intro"
      Clip "main"
      Clip "credits"
```

In order to make the tree structure easy to traverse, we use the name "children" for the list of child objects in each parent (except for Timeline's "tracks").

## Metadata

TODO: Explain how metadata works and why we do it that way.

## Example:

```json
{
    "OTIO_SCHEMA": "Timeline.1", 
    "metadata": {}, 
    "name": "transition_test", 
    "tracks": {
        "OTIO_SCHEMA": "Stack.1", 
        "children": [
            {
                "OTIO_SCHEMA": "Sequence.1", 
                "children": [
                    {
                        "OTIO_SCHEMA": "Transition.1",
                        "metadata": {},
                        "name": "t0",
                        "transition_type": "SMPTE_Dissolve",
                        "parameters": {},
                        "in_offset": {
                            "OTIO_SCHEMA" : "RationalTime.1",
                            "rate" : 24,
                            "value" : 10
                        },
                        "out_offset": {
                            "OTIO_SCHEMA" : "RationalTime.1",
                            "rate" : 24,
                            "value" : 10
                        }
                    },
                    {
                        "OTIO_SCHEMA": "Clip.1", 
                        "effects": [], 
                        "markers": [], 
                        "media_reference": null, 
                        "metadata": {}, 
                        "name": "A", 
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1", 
                            "duration": {
                                "OTIO_SCHEMA": "RationalTime.1", 
                                "rate": 24, 
                                "value": 50
                            }, 
                            "start_time": {
                                "OTIO_SCHEMA": "RationalTime.1", 
                                "rate": 24, 
                                "value": 0.0
                            }
                        }

                    },
                    {
                        "OTIO_SCHEMA": "Transition.1",
                        "metadata": {},
                        "name": "t1",
                        "transition_type": "SMPTE_Dissolve",
                        "parameters": {},
                        "in_offset": {
                            "OTIO_SCHEMA" : "RationalTime.1",
                            "rate" : 24,
                            "value" : 10
                        },
                        "out_offset": {
                            "OTIO_SCHEMA" : "RationalTime.1",
                            "rate" : 24,
                            "value" : 10
                        }
                    },
                    {
                        "OTIO_SCHEMA": "Clip.1", 
                        "effects": [], 
                        "markers": [], 
                        "media_reference": null, 
                        "metadata": {}, 
                        "name": "B", 
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1", 
                            "duration": {
                                "OTIO_SCHEMA": "RationalTime.1", 
                                "rate": 24, 
                                "value": 50
                            }, 
                            "start_time": {
                                "OTIO_SCHEMA": "RationalTime.1", 
                                "rate": 24, 
                                "value": 0.0
                            }
                        }

                    },
                    {
                        "OTIO_SCHEMA": "Clip.1", 
                        "effects": [], 
                        "markers": [], 
                        "media_reference": null, 
                        "metadata": {}, 
                        "name": "C", 
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1", 
                            "duration": {
                                "OTIO_SCHEMA": "RationalTime.1", 
                                "rate": 24, 
                                "value": 50
                            }, 
                            "start_time": {
                                "OTIO_SCHEMA": "RationalTime.1", 
                                "rate": 24, 
                                "value": 0.0
                            }
                        }

                    },
                    {
                        "OTIO_SCHEMA": "Transition.1",
                        "metadata": {},
                        "name": "t3",
                        "transition_type": "SMPTE_Dissolve",
                        "parameters": {},
                        "in_offset": {
                            "OTIO_SCHEMA" : "RationalTime.1",
                            "rate" : 24,
                            "value" : 10
                        },
                        "out_offset": {
                            "OTIO_SCHEMA" : "RationalTime.1",
                            "rate" : 24,
                            "value" : 10
                        }
                    }
                    
                ], 
                "effects": [], 
                "kind": "Video", 
                "markers": [], 
                "metadata": {}, 
                "name": "Sequence1", 
                "source_range": null
            }
        ], 
        "effects": [], 
        "markers": [], 
        "metadata": {}, 
        "name": "tracks", 
        "source_range": null
    }
}
```

## Schema Specification

To see an autogenerated documentation of the serialized types and their fields, see this: <a href="otio-serialized-schema.html">Autogenerated Serialized File Format</a>
