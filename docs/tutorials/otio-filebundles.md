# File Bundles

## Overview

This document describes OpenTimelineIO's file bundle formats, `otiod` and `otioz`, and how to read and write them from Python and C++.

The OTIOZ/D File Bundle formats package OpenTimelineIO data and associated media into a single file.  This can be useful for sending, archiving and interchange of a single unit that collects cut information and media together.

## OTIOZ/D File Bundle Format Details

There are two encodings for OTIO file bundles, OTIOZ and OTIOD.  OTIOD is an encoding in the file system that uses a directory hierarchy of files.  OTIOZ is the identical structure packed into a single .zip file.  Both contain a content.otio entry at the top level which contains the cut information for the bundle.

### Structure

File bundles have a consistent structure:

OTIOD:

```
something.otiod (directory)
├── content.otio (file)
├── version.txt (file)
└── media (directory)
    ├── media1 (file)
    ├── media2 (file)
    └── media3 (file)
```

OTIOZ (encoded in a zipfile):

```
something.otioz (zipfile)
├── content.otio (compressed file)
├── version.txt (compressed file)
└── media (directory)
    ├── media1 (uncompressed file)
    ├── media2 (uncompressed file)
    ├── media3 (uncompressed file)
    └── ...    (uncompressed files)
```

The media files in an OTIOZ are stored without compression, so an application can read them directly from the zipfile without extracting it first.  Paths inside an OTIOZ always use the unix style separator (`/`), so a bundle created on one platform can be read on any other.

### content.otio file

This is an OpenTimelineIO file whose media references are one of:

- `ExternalReference`s with a `target_url` that is a relative path into the `media` directory, such as `media/shot1.mov`.
- `ImageSequenceReference`s with a `target_url_base` of `media/`.
- `MissingReference`s.

Clips with multiple media references have all of their references bundled.

### version.txt file

This file encodes the bundle version, with no other text, in the form:

```
1.0.0
```

OTIOD bundles written before the C++ implementation do not have a `version.txt` file; they can still be read.

### "media" Directory

The `media` directory contains all the media files that the media references in the `content.otio` point at, in a flat structure.  Each image of an image sequence is a separate file in the directory.  Media files can be encoded in whichever codec/container the user wishes (otio is unable to decode or encode the media files).

Because the directory is flat, each media file must have a unique basename.  Basenames are compared without regard to case, so that a bundle can be extracted on a case insensitive file system.  See [Unique Basenames](#unique-basenames) below.

## Reading Bundles

When a bundle is read, only the `content.otio` file is read and parsed by default.

For example, to get some stats of the timeline (not the media) of an otioz file, you can run:

`otiostat something.otioz`

Because this will _only_ read the `content.otio` from the bundle, it is usually a fast operation to run. None of the media is decoded or unzipped during this process.

### Read Options

The adapters take these optional arguments:

- `extract_to_directory` (OTIOZ only): extract the contents of the bundle into this directory, which must not already exist.
- `absolute_media_reference_paths` (OTIOD only): convert the media references in the bundle to absolute paths.  Default is `False`.

### Read Example

Extract the contents of the bundle and convert to an rv playlist:

`otioconvert -i /var/tmp/some_file.otioz -a extract_to_directory=/var/tmp/example_directory -o /var/tmp/example_directory/some_file.rv`

## Writing Bundles

### Source Timeline Constraints

When a bundle is written, the media that the source timeline references is copied into the bundle.  There are some constraints on the source timeline.

#### Unique Basenames

Because file bundles have a flat namespace for media, the media references in the source timeline must point at media files with unique basenames.

For example, if there are media references that point at:

`/project_a/academy_leader.mov`

and:

`/project_b/Academy_Leader.mov`

Because the basenames of both files are the same, ignoring case, this will be an error.  Media references that point at the same file are fine; the file is only copied once.

#### Media Reference URLs

The `target_url` of an `ExternalReference` (and the `target_url_base` of an `ImageSequenceReference`) can be:

- A file URL: `file:///path/to/some/file`.  Percent encoded characters (`%20`), Windows drive letters (`file:///C:/path`) and UNC paths (`file://host/share/path`) are supported.
- A path: `/path/to/some/file` or `path/to/some/file`.

Relative paths are resolved against the `relative_media_base_dir` option if it is given, otherwise against the current working directory.

URLs with other schemes, such as `http://`, are not files, and are handled by the media reference policy.

### Write Options

The adapters take these optional arguments:

- `relative_media_base_dir`: the directory that relative media paths are resolved against.
- `media_policy`: the media reference policy, see below.
- `dryrun`: check the timeline against the media reference policy, and return the total size in bytes of the files that would be written, without writing the bundle.
- `target_schema_versions`: write `content.otio` at older schema versions, see below.

### Media Reference Policy

The media reference policy decides what happens to media references that are not files.  The policies are:

- `error_if_not_file` (default): writing the bundle is an error.
- `missing_if_not_file`: the media reference is replaced with a `MissingReference`.
- `all_missing`: all media references are replaced with `MissingReference`s, and no media is put into the bundle.

A `MissingReference` that replaces a media reference keeps the original metadata, and adds `missing_reference_because` and `original_target_url` entries.  Media references that are already `MissingReference`s are left as they are, and are not an error.

To use this argument with `otioconvert` from the commandline, you can use the `-A` flag with the argument name `media_policy`:

```
otioconvert -i <some_file> -o path/to/output_file.otioz -A media_policy="all_missing"
```

The names used by earlier versions of OTIO, such as `AllMissing`, are also accepted.

### Older Schema Versions

As with `.otio` files, `content.otio` can be written at older schema versions so that it can be read by an older version of OpenTimelineIO.  Pass a map of schema name to version as `target_schema_versions`, for example one of the `OTIO_CORE` version maps (see [Versioning Schemas](versioning-schemas)):

```python
downgrade_manifest = otio.versioning.fetch_map("OTIO_CORE", "0.18.1")
otio.adapters.write_to_file(
    timeline,
    "/path/to/file.otioz",
    target_schema_versions=downgrade_manifest
)
```

If `target_schema_versions` is not given, the {term}`OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL` environment variable is used if it is set.

From the commandline:

```
otioconvert -i some_file.otio -o /var/tmp/some_file.otioz -A target_schema_versions="{'Marker':2}"
```

### Write Example

Convert an otio into a zip bundle:

`otioconvert -i some_file.otio -o /var/tmp/some_file.otioz`

## Python API

In Python, bundles are read and written with the adapters, using the options above as keyword arguments:

```python
import opentimelineio as otio

timeline = otio.adapters.read_from_file("cut.otio")

# Write the bundle, resolving relative media paths against the project
# directory
otio.adapters.write_to_file(
    timeline,
    "cut.otioz",
    relative_media_base_dir="/path/to/project",
    media_policy="missing_if_not_file"
)

# Read the bundle, extracting the media
timeline = otio.adapters.read_from_file(
    "cut.otioz",
    extract_to_directory="/var/tmp/cut"
)
```

Errors are raised as exceptions.

## C++ API

Bundles are read and written in C++ with the functions in `opentimelineio/bundle.h`:

```cpp
#include <opentimelineio/bundle.h>

using namespace OTIO_NS;

ErrorStatus error_status;

bundle::WriteOptions write_options;
write_options.relative_media_base_dir = "/path/to/project";
if (!bundle::write_otioz(timeline, "cut.otioz", write_options, &error_status))
{
    // Handle the error
}

bundle::ReadOptions read_options;
read_options.extract_path = "/var/tmp/cut";
read_options.absolute_media_reference_paths = true;
SerializableObject::Retainer<Timeline> result(dynamic_cast<Timeline*>(
    bundle::read_otioz("cut.otioz", read_options, &error_status)));
if (!result || is_error(error_status))
{
    // Handle the error
}
```

See `examples/bundle.cpp` for a complete example.
