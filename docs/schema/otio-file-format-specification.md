# File Format Specification

## Version

This DRAFT describes the OpenTimelineIO JSON File Format as of OTIO Beta 13.

## Note
It is strongly recommended that everyone use the OpenTimelineIO library to read and write OTIO files instead of implementing a separate parser or writer.

## Naming
OpenTimelineIO files should have a `.otio` path extension. Please do not use `.json` to name OTIO files.

## Contents
OpenTimelineIO files are serialized as JSON (http://www.json.org).

### Number Types

Supported number types:

- integers: `int64_t` (signed 64 bit integer)
- floating point numbers: `double` (IEEE754 64 bit signed floating point number)

In addition to the basic JSON spec, OTIO allows the following values for doubles:

- `NaN` (not a number)
- `Inf`, `Infinity` (positive infinity)
- `-Inf, -Infinity (negative infinity)

## Structure
An OTIO file is a tree structure of nested OTIO objects. Each OTIO object is stored as a JSON dictionary with member fields,
each of which may contain simple data types or nested OTIO objects.

OTIO does not support instancing, there cannot be references the same object multiple times in the tree structure. If the same clip or media appears multiple times in a timeline, it will appear as identical copies of the Clip or MediaReference object.

The top level object in an OTIO file can be any OTIO data type, but is typically a Timeline. This means that most use cases will assume that the top level
object is a Timeline, but in specific workflows, otio files can be read or written that contain
just a Clip, Track, RationalTime, or any other OTIO data type. Due to the nature of JSON, arrays of objects can also be read/written, but it is better to use the OTIO SerializableCollection data type in this case so that metadata can be attached to the container itself. Code that reads an OTIO
file should guard against unexpected top level types and fail gracefully.
Note also, that this is the reason that there is no top level file format version in OTIO. Each data type has a version instead to allow for more granular versioning.

Each OTIO object has an `"OTIO_SCHEMA"` key/value pair that identifies the OTIO data type and version of that type.
For example `"OTIO_SCHEMA": "Timeline.1"` or `"OTIO_SCHEMA": "Clip.5"`. This allows future versions of OTIO to change the serialization details of each data type
independently and introduce new data types over time. (TODO: Link to discussion on schema versioning.)

Member fields of each data type are encoded as key/value pairs in the containing object's dictionary. The value of each key can be a JSON string, number, list,
or dictionary. If the value is a dictionary, then it will often be an OTIO data type. In some cases (specifically metadata) it can be a regular JSON dictionary.

OTIO JSON files are typically formatted with indentation to make them easier to read. This makes the files slightly larger, but dramatically improves human
readability which makes debugging much easier. Furthermore, the OTIO library will write the keys of each object in a predictable order to help with change tracking, comparisons, etc.

Since human readablility and ease of use are explicit goals of the OpenTimelineIO project, it is recommended that OTIO JSON not be minified unless absolutely necessary. If a minimum file size is desired, the recommendation is to use gzip rather than minifying.

## Nesting

A Timeline has one child, called "tracks" which is a Stack. Each of that Stack's children is a Track. From there on down each child can be any of these types: Clip, Filler, Stack, Track.

In a simple case with one track of 3 clips:

```
Timeline "my timeline"
  Stack "tracks"
    Track "video track"
      Clip "intro"
      Clip "main"
      Clip "credits"
```

In order to make the tree structure easy to traverse, OTIO uses the name "children" for the list of child objects in each parent (except for Timeline's "tracks").

## Metadata

Timeline, Stack, Track, Clip, MediaReferece, and most other OTIO objects all have a `metadata` property.
This metadata property holds a dictionary of key/value pairs which may be deeply nested, and may hold any
variety of JSON-compatible data types (numbers, booleans, strings, arrays, dictionaries) as well as any other
OTIO objects.

This is intended to be a place to put information that does not fit into the schema defined properties.
The core of OTIO doesn't do anything with this metadata, it only carries it along so that adapters, scripts,
applications, or other workflows can use that metadata however needed. For example, 
several of the adapters shipped with OTIO use metadata to store information that doesn't (yet) fit into
the core OTIO schema.

Due to the fact that many different workflows can and will use metadata, it is important to group
metadata inside namespaces so that independent workflows can coexist without encountering name collisions. In the example below, there is metadata on the Timeline and on several Clips for both a hypothetical `my_playback_tool` and `my_production_tracking_system` that could coexist with anything else added under a different namespace.

Metadata can also be useful when prototyping new OTIO schemas. An existing object can be extended with metadata which can later be migrated into a new schema version, or a custom schema defined in a [SchemaDef plugin](/python-tutorials/write-a-schemadef).

## Example:

```json
{
    "OTIO_SCHEMA": "Timeline.1",
    "metadata": {
        "my_playback_tool": {
            "metadata_overlay": "full_details",
            "loop": false
        },
        "my_production_tracking_system": {
            "purpose": "dailies",
            "presentation_date": "2020-01-01",
            "owner": "rose"
        }
    },
    "name": "transition_test",
    "tracks": {
        "OTIO_SCHEMA": "Stack.1",
        "children": [
            {
                "OTIO_SCHEMA": "Track.1",
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
                        "metadata": {
                            "my_playback_tool": {
                                "tags": ["for_review", "nightly_render"],
                            },
                            "my_production_tracking_system": {
                                "status": "IP",
                                "due_date": "2020-02-01",
                                "assigned_to": "rose"
                            }
                        },
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
                        "metadata": {
                            "my_playback_tool": {
                                "tags": ["for_review", "nightly_render"],
                            },
                            "my_production_tracking_system": {
                                "status": "IP",
                                "due_date": "2020-02-01",
                                "assigned_to": "rose"
                            }
                        },
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
                        "metadata": {
                            "my_playback_tool": {
                                "tags": [],
                            },
                            "my_production_tracking_system": {
                                "status": "final",
                                "due_date": "2020-01-01",
                                "assigned_to": null
                            }
                        },
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
                "name": "Track1",
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

To see an autogenerated documentation of the serialized types and their fields, see this: [Autogenerated Serialized File Format](otio-serialized-schema).
