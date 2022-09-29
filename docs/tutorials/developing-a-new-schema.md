# Schema Proposal and Development Workflow

## Introduction

This document describes a process for proposing and developing a new schema for the
[OpenTimelineIO project](https://opentimeline.io).

The process includes several steps:

* Proposing at a TSC meeting and gathering interested parties for feedback
    * Outlining example JSON
* Implementing and iterating on a branch
* Building support into an adapter as a demonstration
* Incrementing other schemas that are impacted (Eg. Changes to `Clip` to
  implement `Media Multi Reference`

## Examples

A number of schemas have been proposed and introduced during
OpenTimelineIO's development.  These include:

* [ImageSequenceReference](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/pull/602)
* [SpatialCoordinates](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/pull/1219)
* [Multi media-reference](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/pull/1241)

## Core schema or Plugin?

OpenTimelineIO has a number of plugin mechanisms, including the
[Schemadef](write-a-schemadef).  Plugin schemadefs are great for things that
aren't expected to be useful to the broader community, or are specific to a particular studio,
workflow, or practice.  Example of this might be a reference to a proprietary
database or a proprietary effect.  They can also be a good place to prototype a
particular schema before proposing it to the community for adoption.

## Proposal

A proposal can be as fleshed out as a proposed implementation or as vague as an
idea.  Presenting the proposal at a Technical Steering Committee for discussion
is preferred so that interested parties can form a working group if necessary.
The goal is to find view points / impacts that might not have been considered
and advertise the development to the community at large.

Including an example JSON blob which has the fields you think might be needed
can help.

References that are particularly helpful are examples from existing
applications/formats, information about how (or if) the schema participates in
temporal transformations, or other citations.

## Implementing and Iterating on a branch

Development of schemas typically takes longer and includes more feedback and
review than normal development.  To facilitate this, generally the project will
open a branch on the repository so that pull requests can be merged into the
prototype without disturbing the main branch.  For example, the
[ImageSequenceReference](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/pull/602)
branch.

A complete implementation should have a:

* C++ core implementation in src/opentimelineio
* python binding in src/py-opentimelineio
* unit tests

### Unit Tests

Unit Tests should include a C++ test for the C++ component, a python test for
the python binding, and a baseline test.

#### C++ test

The C++ test should directly test the C++ interface.  For examples of that, see
`tests/*.cpp`.

#### Python tests

The Python test should test the python binding, including any extra ergonomic
conveniences unique to the python implementation (iterators, etc).  We use the
`unittest` python library.  For examples of this, see: `tests/test_*.py`.

#### Baseline tests

Baseline tests are written in python and are intended to test the serializer.

They include:

* a file named `tests/baselines/empty_<your_schema>.json`, which is the result
  of calling the constructor and then immediately serializing the object:

```python
ys = YourSchema()
otio.adapters.write_to_file(ys, "empty_your_schema.json", adapter="otio_json")
```

* a test in `tests/test_json_backend.py` of the form:

```python
class TestJsonFormat(unittest.TestCase, otio_test_utils.OTIOAssertions):
    ...
    def test_your_schema(self):
        ys = YourSchema()
        self.check_against_baseline(ys, "empty_your_schema")
    ...
```

## Demo Adapter

Providing an adapter that supports the schema can show how the schema is
translated into another format.  For example, the
[ImageSequenceReference](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/pull/722)
used the RV adapter to demonstrate how it could be used by an adapter.

## Incrementing Other Schemas

Depending on where the schema fits into the overall structure, other schemas
might need to be incremented or changed.  For example, the Media
multi-reference caused the clip schema to increment.  Considering and
implementing this is part of the implementation.  Providing up and downgrade
functions ensure backwards and forwards compatibility.

## Conclusion

OpenTimelineIO is designed to evolve, and through its schema versioning system
hopes to adapt to changes in the world of timelines and time math.  We hope
that working with and on OpenTimelineIO can be a positive, enriching experience
for the community.  Thanks for being a part of it!
