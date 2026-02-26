# File Bundles

## Overview

This document describes OpenTimelineIO's file bundle formats, `otiod` and `otioz`, as well as how to use the internal adapters that read and write them.

The OTIOZ/D File Bundle formats package OpenTimelineIO data and associated media into a single file.  This can be useful for sending, archiving and interchange of a single unit that collects cut information and media together.

## OTIOZ/D File Bundle Format Details

There are two encodings for OTIO file bundles, OTIOZ and OTIOD.  OTIOD is an encoding in the file system that uses a directory hierarchy of files.  OTIOZ is the identical structure packed into a single .zip file, currently using the python `zipfile` library.  Both contain a content.otio entry at the top level which contains the cut information for the bundle.

### Structure

File bundles have a consistent structure:

OTIOD:

```
something.otiod (directory)
├── content.otio (file)
└── media (directory)
    ├── media1 (file)
    ├── media2 (file)
    └── media3 (file)
```

OTIOZ (adds the version.txt file and is encoded in a zipfile):

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

### content.otio file

This is an OpenTimelineIO file whose media references are either `MissingReference`s, or `ExternalReference`s with target_urls that are relative paths pointing into the `media` directory.

### version.txt file

This file encodes the otioz version of the file, with no other text, in the form:

```
1.0.0
```

### "media" Directory

The `media` directory contains all the media files that the `ExternalReference`s `target_url`s in the `content.otio` point at, in a flat structure.  Each media file must have a unique basename, but can be encoded in whichever codec/container the user wishes (otio is unable to decode or encode the media files).

## Adapter Usage

## Read Adapter Behavior

When a bundle is read from disk using the OpenTimelineIO Python API (using the adapters.read_from_* functions), only the `content.otio` file is read and parsed.

For example, to get some stats of the timeline (not the media) of an otioz file in `otiostat`, you can run:

`otiostat something.otioz`

Because this will _only_ read the `content.otio` from the bundle, it is usually a fast operation to run. None of the media is decoded or unzipped during this process.

### extract_to_directory Optional Argument

extract_to_directory: if a value other than `None` is passed in, will extract the contents of the bundle into the directory at the path passed into the `extract_to_directory` argument.  For the OTIOZ adapter, this will unzip the associated media.

### absolute_media_reference_paths Optional Argument

The OTIOD adapter additionally has an argument `absolute_media_reference_paths` which will convert all the media references in the bundle to be absolute paths if `True` is passed.  Default is `False`.

### Read Adapter Example

Extract the contents of the bundle and convert to an rv playlist:

`otioconvert -i /var/tmp/some_file.otioz -a extract_to_directory=/var/tmp/example_directory -o /var/tmp/example_directory/some_file.rv`

## Write Adapter

### Source Timeline Constraints

For creating otio bundles using the provided python adapter, an OTIO file is used as input.  There are some constraints on the source timeline.

#### Unique Basenames

Because file bundles have a flat namespace for media, and media will be copied into the bundle, the `ExternalReference` media references in the source OTIO must have a target_url fields pointing at media files with unique basenames.

For example, if there are media references that point at:

`/project_a/academy_leader.mov`

and:

`/project_b/academy_leader.mov`

Because the basename of both files is `academy_leader.mov`, this will be an error.  The adapters have different policies for how to handle media references.  See below for more information.

#### Expected Source Timeline External Reference URL Format

The file bundle adapters expect the `target_url` field of any `media_reference`s in the source timeline to be in one of two forms (as produced by python's [urlparse](https://docs.python.org/3/library/urllib.parse.html) library):

- absolute path:  "file:///path/to/some/file" (encodes "/path/to/some/file")
- relative path: "path/to/some/file" (the path is relative to the current working directory of the command running the adapter on the source timeline).

### MediaReferencePolicy Option

When building a file bundle using the OTIOZ/OTIOD adapters, you can set the 'media reference policy', which is described by an enum in the file_bundle_utils module.  The policies can be:

- (default) `ErrorIfNotFile`: will raise an exception if a media reference is found that is of type `ExternalReference` but that does not point at a `target_url`.
- `MissingIfNotFile`: will replace any media references that meet the above condition with a `MissingReference`, preserving the original media reference in the metadata of the new `MissingReference`.
- `AllMissing`: will replace all media references with `MissingReference`, preserving the original media reference in metadata on the new object.

When running in `AllMissing` mode, no media will be put into the bundle.

To use this argument with `otioconvert` from the commandline,  you can use the `-A` flag with the argument name `media_policy`:

```
otioconvert -i <some_file> -o path/to/output_file.otioz -A media_policy="AllMissing"
```

### Write Adapter Example

Convert an otio into a zip bundle:

`otioconvert -i some_file.otio -o /var/tmp/some_file.otioz`
